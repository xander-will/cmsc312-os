from threading import Lock, Thread
from random import randint

import src.exceptions as ex

from src.globals import DebugPrint
from src.monitor import Monitor
from src.process import Process, PThread

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
        self.ready = list()
        self.wait_io = list()
        self.wait_mem = list()

        for file in filelist:
            x = randint(1, 4)
            DebugPrint(f"[Dispatcher] Initializing {x} copies of {file}")
            for _ in range(1):
                self.createProcess(file) 
        
        self.quant = self.quant_left = quant
        self.io = False
        self.mutexes = DisMonitors()
        self.current = None
        self.sch = self.SimpleRoundRobin

        DebugPrint("[Dispatcher] Successfully initialized!")

    def schedule(self):
        self.sch()

    def createProcess(self, filename):
        try:
            proc = Process(filename, self.next_pid, self.ready)
            self.ready.append(proc.getMain())
            self.next_pid += 1
        except ex.ImproperInstructionError:
            DebugPrint(f"[Dispatcher] {filename} failed initialization")
        except ex.MemoryAllocationError:
            print("hello")
            self.wait_mem.append(filename)

    def isIdle(self):
        return not self.ready and self.wait_io

    def addWaitingProcs(self):
        for file in self.wait_mem:
            self.createProcess(file)

    def monitorRelease(self, proc, mon):
        if proc.hasMutex(mon):
            new_thr = self.mutexes.get(mon).release()
            if new_thr:
                DebugPrint(f"[Dispatcher] Thread {new_thr.getName()} acquired mutex {mon}")
                return new_thr

    def runCurrent(self):
        returns = list()
        threads = list()
        for i, thread in enumerate(self.current):
            returns.append(None)
            threads.append(Thread(target=self.runThread, args=(i, thread, returns)))
        for thread in threads:
            thread.join()

        for i, arg in enumerate(returns):
            if arg == True:
                self.ready.append(self.current[i])
                self.current.pop(i)
            elif isinstance(arg, PThread):
                self.ready.append(arg)
            


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
            print(thread)
            thread.incrementPC()
        elif ins == "exe":
            for mon in thread.mutexes:
                self.monitorRelease(thread, mon)
            thread = None
            self.addWaitingProcs()
            return False 
        elif ins == "yield":
            thread.incrementPC()
            self.sch()
            return True
        elif ins == "io":
            if not self.io:
                self.wait_io.append(thread)
                thread = None
                self.sch()
                return True 
            else:
                self.quant_left -= 1
                if not thread.run():
                    thread.setQueue(self.ready)
                    self.ready.append(thread)
                    thread = None
                    self.sch()
                    return True
                elif not self.quant_left:
                    return False
                else:
                    return True
        elif ins == "calculate":
            self.quant_left -= 1
            print(self.quant_left)
            if not thread.run() or not self.quant_left:
                return False
            else:
                return True
        elif ins == "fork":
            thread.incrementPC()
            self.ready.append(thread.fork(self.next_pid, self.ready))
            self.next_pid += 1
            return True
        elif ins == "thread":
            arg = thread.getInstrArg()
            thread.incrementPC()
            for _ in range(arg):
                self.ready.append(thread.createThread(self.ready))
            return True

        return False
        
    def setIO(self, flag):
        self.io = flag
        self.sch()
        DebugPrint(f"[Dispatcher] IO mode is {flag}")

    ## Schedulers
    def SimpleRoundRobin(self):
        # q = self.ready
        # if self.io:
        #     q = self.wait_io if self.wait_io else self.ready

        # if self.current:
        #     self.current.queue.append(self.current)
        
        # try:
        #     p = q.pop(0)
        #     self.current = p
        #     self.quant_left = self.quant
        #     DebugPrint("[Dispatcher] Ran SimpleRoundRobin")
        # except IndexError:
        #     DebugPrint("[Dispatcher] Ran SimpleRoundRobin, is idle")

        q = self.ready
        if self.io:
            q = self.wait_io if self.wait_io else self.ready

        for thread in self.current:
            thread.queue.append(thread)
        self.current = list()
        
        try:
            for _ in range(4):
                if q:
                    self.current.append(q.pop(0))
            self.quant_left = self.quant
            DebugPrint("[Dispatcher] Ran SimpleRoundRobin")
        except IndexError:
            DebugPrint("[Dispatcher] Ran SimpleRoundRobin, is idle")


            


