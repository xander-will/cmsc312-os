from threading import Lock, Thread
from random import randint, shuffle

import src.commands as c
import src.exceptions as ex

from src.globals import DebugPrint, gui_mailbox
from src.monitor import Monitor
from src.process import Process, PThread, GenerateRandomProcess

class DisMonitors:
    def __init__(self):
        self.a = Monitor("a")
        self.b = Monitor("b")
        self.c = Monitor("c")

    def get(self, mon):
        return {
            "a" :   self.a,
            "b" :   self.b,
            "c" :   self.c
        }[mon]

class Dispatcher:

    def __init__(self, quant, filelist):
        self.next_pid = 1
        self.frgrnd = list()    # high priority threads
        self.bckgrnd = list()   # low priority threads
        self.wait = list()      # buffer for threads moving around
        self.wait_io = list()   # buffer for threads waiting for IO
        self.wait_mem = list()  # buffer for processes that can't open up yet

        for file in filelist:
            x = randint(3, 5)
            DebugPrint(f"[Dispatcher] Initializing {x} copies of {file}")
            for _ in range(1):
                self.createProcess(file) 
        
        self.quant = self.quant_left = quant
        self.io = False
        self.mutexes = DisMonitors()
        self.current = None
        self.sch = self.PriorityScheduler
        self.lock = Lock()
        self.pri_cntr = 0
        self.total_threads = 0
        self.threads_ended = 0
        self.sum_of_runtime = 0
        self.num_active_threads = 0

        DebugPrint("[Dispatcher] Successfully initialized!")

    def stats(self):
        s = list()
        s.append(f"Processes started: {self.next_pid-1}\n")
        s.append(f"Threads started: {self.total_threads}\n")
        s.append(f"Threads finished: {self.threads_ended}\n")
        if self.threads_ended:
            s.append(f"Average thread runtime: {round(self.sum_of_runtime / self.threads_ended, 2)} cycles\n")
        s.append(f"Active threads: {self.num_active_threads}\n")
        s.append(f"Processes waiting for memory: {len(self.wait_mem)}\n")
        s.append(f"Processes waiting for io: {len(self.wait_io)}\n")
        s.append(f"Current scheduler: {self.sch.__name__}\n")

        return s

    def switch(self):
        if self.sch.__name__ == "PriorityScheduler": # no clue why it doesn't work with
            self.sch = self.RandomScheduler     # the 'is' operator... very weird
        else:
            self.sch = self.PriorityScheduler

    def schedule(self):
        self.sch()

    def createProcess(self, filename):
        try:
            proc = Process(filename, self.next_pid, self.frgrnd)
            self.frgrnd.append(proc.getMain())
            self.next_pid += 1
            self.total_threads += 1
        except ex.ImproperInstructionError:
            DebugPrint(f"[Dispatcher] {filename} failed initialization")
            gui_mailbox.put(c.Cmd_Error(f"{filename} is miswritten, please update and try again"))
        except ex.MemoryAllocationError:
            self.wait_mem.append(filename)
        #except:
        #    DebugPrint(f"[Dispatcher] {filename} failed initialization... weirdly")
        #    gui_mailbox.put(c.Cmd_Error(f"{filename} failed init... weirdly"))

    def randomProcess(self, x):
        filename = GenerateRandomProcess()
        for _ in range(x):
            self.createProcess(filename)

    def isIdle(self):
        return not self.frgrnd and not self.wait_io and not self.bckgrnd

    def addWaitingProcs(self):
        with self.lock:
            for file in self.wait_mem:
                self.createProcess(file)

    def monitorRelease(self, proc, mon):
        if proc.hasMutex(mon):
            new_thr = self.mutexes.get(mon).release()
            if new_thr:
                DebugPrint(f"[Dispatcher] Thread {new_thr.getName()} acquired mutex {mon}")
                return new_thr

    def runCurrent(self):
        if not self.current:
            return False    # tell the simulator to reschedule if nothing in current queue

        returns = list()
        threads = list()
        for i, thread in enumerate(self.current):
            returns.append(None)
            threads.append(Thread(target=self.runThread, args=(i, thread, returns)))
            threads[-1].start()
        for thread in threads:
            thread.join()

        removals = list()
        for i, arg in enumerate(returns):
            if arg == True:
                self.current[i].setQueue(self.wait)
                self.wait.append(self.current[i])
                removals.append(i)
            elif arg == False:
                DebugPrint("[Monitor] Ending thread")
                removals.append(i)
                self.threads_ended += 1
                self.sum_of_runtime += self.current[i].time
            elif arg == "io":
                removals.append(i)
            elif isinstance(arg, PThread):
                self.wait.append(arg)
                self.num_active_threads += 1
        
        for index in reversed(removals):
            self.current.pop(index)

        self.quant_left -= 1
        if self.quant_left:
            return True
        else:
            self.quant_left = self.quant
            return False
            

    def runThread(self, num, thread, args):
        DebugPrint(thread)

        ins = thread.currentInstr()
        if ins == "acquire":
            mon = self.mutexes.get(thread.getInstrArg())
            thread.incrementPC()
            if not mon.acquire(thread):
                args[num] = True
        elif ins == "release":
            mon = thread.getInstrArg()
            args[num] = self.monitorRelease(thread, mon)
            thread.incrementPC()
        elif ins == "out":
            gui_mailbox.put(c.Cmd_ProcOut(str(thread)))
            thread.incrementPC()
        elif ins == "exe":
            for mon in thread.mutexes:
                self.monitorRelease(thread, mon)
            self.addWaitingProcs()
            args[num] = False
        elif ins == "yield":
            thread.incrementPC()
            args[num] = True
        elif ins == "io":
            if not self.io:
                with self.lock:
                    self.wait_io.append(thread)
                args[num] = "io"
            else:
                if not thread.run():
                    args[num] = True
        elif ins == "calculate":
            if not thread.run():
                args[num] = True
        elif ins == "fork":
            thread.incrementPC()
            with self.lock:
                self.wait.append(thread.fork(self.next_pid, self.wait))
                self.next_pid += 1
                self.total_threads += 1
        elif ins == "thread":
            arg = thread.getInstrArg()
            thread.incrementPC()
            with self.lock:
                for _ in range(arg):
                    self.wait.append(thread.createThread(self.wait))
                    self.total_threads += 1
        elif ins == "send":
            arg = thread.getInstrArg()
            thread.incrementPC()
            mon = self.mutexes.get(arg[1])
            mon.set(arg[0])
        elif ins == "read":
            mon = self.mutexes.get(thread.getInstrArg())
            thread.incrementPC()
            if not mon.get() and thread.currentInstr() not in ["exe", "loop"]:
                thread.incrementPC()
        elif ins == "loop":
            thread.resetPC()
        elif ins == "pipe":
            thread.parent.setPipe(thread.getInstrArg())
            thread.incrementPC()
        elif ins == "check":
            x = thread.parent.getPipe()
            thread.incrementPC()
            if not x and thread.currentInstr() not in ["exe", "loop"]:
                thread.incrementPC()

        
    def setIO(self, flag):
        self.io = flag
        self.sch()
        DebugPrint(f"[Dispatcher] IO mode is {flag}")

    ## Schedulers
    def compileAll(self):
        self.pri_cntr += 1
        temp = self.frgrnd + self.bckgrnd + self.wait
        if self.current:
            for thread in self.current:
                temp.append(thread)
        all = list()
        for thread in temp:         # cleans up some hidden errors where
            if thread not in all:   # threads duplicate themselves
                all.append(thread)  # on accident
                if self.pri_cntr > 20:  # aging routine
                    self.pri_cntr = 0
                    thread.priority -= 1 if thread.priority and not thread.daemon else 0

        self.num_active_threads = len(all)

        return all

    def PriorityScheduler(self):
        all = self.compileAll()

        self.current = list()
        self.frgrnd = list(filter(lambda thread: thread.priority <= 15, all))
        self.bckgrnd = list(filter(lambda thread: thread.priority > 15, all))
        self.wait = list()

        if self.io and self.wait_io:
            for _ in range(4):
                if self.wait_io:
                    self.current.append(self.wait_io.pop(0))
        else:
            for _ in range(3):
                if self.frgrnd:
                    self.current.append(self.frgrnd.pop(0))
            for _ in range(4-len(self.current)):    # background gets at least 1 each time
                if self.bckgrnd:
                    self.current.append(self.bckgrnd.pop(0))
        self.quant_left = self.quant
        DebugPrint("[Dispatcher] Ran PriorityScheduler")

    def RandomScheduler(self):
        all = self.compileAll()

        self.current = list()
        self.frgrnd = list(filter(lambda thread: thread.priority <= 15, all))
        self.bckgrnd = list(filter(lambda thread: thread.priority > 15, all))
        self.wait = list()

        shuffle(self.frgrnd)
        shuffle(self.bckgrnd)

        if self.io and self.wait_io:
            for _ in range(4):
                if self.wait_io:
                    self.current.append(self.wait_io.pop(0))
        else:
            for _ in range(3):
                if self.frgrnd:
                    self.current.append(self.frgrnd.pop(0))
            for _ in range(4-len(self.current)):    # background gets at least 1 each time
                if self.bckgrnd:
                    self.current.append(self.bckgrnd.pop(0))
        self.quant_left = self.quant
        DebugPrint("[Dispatcher] Ran RandomScheduler")


            


