import json

from random import randint
from threading import Lock

import src.exceptions as ex

from src.globals import DebugPrint
from src.memory import memory

class Instruction:
    def __init__(self, owner, instr):
        self.owner = owner
        self.mem_list = None    # suppresses an error
        try:
            self.op = instr["operation"]
            self.arg = {
                "acquire"   :   lambda x: x["monitor"],
                "release"   :   lambda x: x["monitor"], 
                "io"        :   lambda x: None,
                "calculate" :   lambda x: None,
                "out"       :   lambda x: None,
                "yield"     :   lambda x: None,
                "exe"       :   lambda x: None,
                "fork"      :   lambda x: None,
                "thread"    :   lambda x: x["num"],
                "send"      :   lambda x: (x["val"], x["monitor"]), 
                "read"      :   lambda x: x["monitor"]
            }[self.op](instr)
            self.cycle = {
                "acquire"   :   lambda x: 1,
                "release"   :   lambda x: 1, 
                "io"        :   lambda x: x["cycles"],
                "calculate" :   lambda x: x["cycles"],
                "out"       :   lambda x: 1,
                "yield"     :   lambda x: 1,
                "exe"       :   lambda x: 1,
                "fork"      :   lambda x: 1,
                "thread"    :   lambda x: 1,
                "send"      :   lambda x: 1, 
                "read"      :   lambda x: 1
            }[self.op](instr)
            if self.cycle is None:
                self.cycle = randint(1, 100)

            self.mem_list = memory.allocate(instr["memory"])
        except IndexError:
            DebugPrint("[Process] Improper instructions")
            raise ex.ImproperInstructionError

    def __del__(self):
        if self.mem_list:
            memory.deallocate(self.mem_list)

    def run(self):
        memory.access(self.mem_list)

class PThread:
    def __init__(self, parent, tid, text, queue, priority, daemon=False):
        self.parent = parent
        self.tid = tid
        self.text = text
        self.queue = queue
        self.priority = priority
        self.daemon = daemon

        self.pc = self.time = 0
        self.mutexes = list()
        self.cycles_left = self.text[0].cycle

    def getName(self):
        return self.parent.name

    def createThread(self, queue):
        return self.parent.createThread(self, queue)

    def setQueue(self, queue):
        self.queue = queue

    def setTime(self, time):
        self.cycles_left = time

    def run(self):
        self.time += 1
        self.cycles_left -= 1
        self.text[self.pc].run
        if self.cycles_left:
            DebugPrint(f"[Process] TID {self.tid} PID {self.parent.pid} just ran {self.text[self.pc].op}")
            return True
        else:
            DebugPrint(f"[Process] TID {self.tid} PID {self.parent.pid} just ended {self.text[self.pc].op}")
            self.pc += 1
            self.cycles_left = self.text[self.pc].cycle
            return False

    def currentInstr(self):
        return self.text[self.pc].op
        
    def hasMutex(self, mon):
        return mon in self.mutexes

    def setMutex(self, mon):
        self.mutexes.append(mon)

    def unsetMutex(self, mon):
        self.mutexes.remove(mon)

    def getInstrArg(self):
        return self.text[self.pc].arg

    def incrementPC(self):
        self.pc += 1
        self.cycles_left = self.text[self.pc].cycle

    def fork(self, pid, queue):
        return self.parent.fork(self, pid, queue)

    def __repr__(self):
        return f"TID {self.tid}/PID {self.parent.pid}"

    def __str__(self):
        s = f"Thread ID {self.tid} (Parent ID {self.parent.pid})\n"
        s += f"\tName: {self.parent.name}\n"
        s += f"\tPriority: {self.priority}\n"
        s += f"\tMemory: {self.parent.size} MB\n"
        s += f"\tElapsed time: {self.time} cycles\n"
        s += f"\tMutexes: {self.mutexes}\n"
        s += f"\tText section: {len(self.text)} instructions\n"
        s += f"\tCurrent instruction: {self.currentInstr()}\n"
        s += f"\tTime left in current instruction: {self.cycles_left}\n"

        return s    

class Process:
    def __init__(self, filename, pid, queue, fork_dump=None):
        if fork_dump:
            dump = fork_dump
        else:
            with open(filename, "r") as f:
                dump = json.load(f)

        self.name = dump["name"]
        self.priority = dump["priority"]
        self.daemon = dump["daemon"] if "daemon" in dump else False

        self.size = 0
        for instr in dump["instructions"]:
            self.size += instr["memory"]
        if self.size > memory.remaining():
            raise ex.MemoryAllocationError

        self.text = list()
        for instr in dump["instructions"]:
            self.text.append(Instruction(self, instr))

        self.thread_text = list()
        if "threadinstr" in dump:
            for instr in dump["threadinstr"]:
                self.thread_text.append(Instruction(self, instr))

        self.next_tid = 0
        self.threads = [PThread(self, 0, self.text, queue, self.priority, daemon=self.daemon)]
        self.pid = pid
        self.dump = dump
        self.lock = Lock()

    def getMain(self):
        return self.threads[0]

    def createThread(self, requester, queue):
        with self.lock:
            self.next_tid += 1
            thr = PThread(self, self.next_tid, requester.text[requester.pc:], queue, self.priority, daemon=self.daemon)
            self.threads.append(thr)
            ret = self.threads[-1]
        return ret

    def setQueue(self, queue):
        self.queue = queue

    def fork(self, requester, pid, queue):
        new_proc = Process("", pid, queue, fork_dump=self.dump)
        main = new_proc.getMain()
        main.pc = requester.pc 
        main.cycles_left = requester.cycles_left

        return new_proc.getMain()

    # def setTime(self, time):
    #     self.cycles_left = time

    # def currentInstr(self):
    #     return self.text[self.pc].op

    # def getInstrArg(self):
    #     return self.text[self.pc].arg

    # def incrementPC(self):
    #     self.pc += 1
    #     self.cycles_left = self.text[self.pc].cycle

    

    