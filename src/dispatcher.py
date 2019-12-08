from random import randint

import src.exceptions as ex

from src.globals import DebugPrint
from src.monitor import Monitor
from src.process import Process

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
            for _ in range(x):
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
            self.ready.append(Process(filename, self.next_pid, self.ready))
            self.next_pid += 1
        except ex.ImproperInstructionError:
            DebugPrint(f"[Dispatcher] {filename} failed initialization")
        except ex.MemoryAllocationError:
            self.wait_mem.append(filename)

    def isIdle(self):
        return not self.ready and self.wait_io

    def addWaitingProcs(self):
        for file in self.wait_mem:
            self.createProcess(file)

    def monitorRelease(self, proc, mon):
        if proc.hasMutex(mon):
            new_proc = self.mutexes.get(mon).release()
            if new_proc:
                self.ready.append(new_proc)

    def runCurrProc(self):
        if not self.current:
            return False

        DebugPrint(self.current)
        ins = self.current.currentInstr()
        
        if ins == "acquire":
            mon = self.mutexes.get(self.current.getInstrArg())
            self.current.incrementPC()
            if mon.acquire(self.current):
                return True
            else:
                self.current = None
                return False
        elif ins == "release":
            self.current.incrementPC()
            mon = self.current.getInstrArg()
            self.monitorRelease(self.current, mon)
            return False
        elif ins == "out":
            print(self.current)
            self.current.incrementPC()
            return True
        elif ins == "exe":
            for mon in self.current.mutexes:
                self.monitorRelease(self.current, mon)
            self.current = None
            self.addWaitingProcs()
            return False 
        elif ins == "yield":
            self.current.incrementPC()
            self.sch()
            return True
        elif ins == "io":
            if not self.io:
                self.wait_io.append(self.current)
                self.current = None
                self.sch()
                return True 
            else:
                self.quant_left -= 1
                if not self.current.run():
                    self.current.setQueue(self.ready)
                    self.ready.append(self.current)
                    self.current = None
                    self.sch()
                    return True
                elif not self.quant_left:
                    return False
                else:
                    return True
        elif ins == "calculate":
            self.quant_left -= 1
            if not self.current.run() or not self.quant_left:
                return False
            else:
                return True
        
    def setIO(self, flag):
        self.io = flag
        self.sch()
        DebugPrint(f"[Dispatcher] IO mode is {flag}")

    ## Schedulers
    def SimpleRoundRobin(self):
        q = self.ready
        if self.io:
            q = self.wait_io if self.wait_io else self.ready

        if self.current:
            self.current.queue.append(self.current)
        
        try:
            p = q.pop(0)
            self.current = p
            self.quant_left = self.quant
            DebugPrint("[Dispatcher] Ran SimpleRoundRobin")
        except IndexError:
            DebugPrint("[Dispatcher] Ran SimpleRoundRobin, is idle")


            


