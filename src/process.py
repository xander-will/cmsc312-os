import json

from random import randint

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
            }[self.op](instr)
            self.cycle = {
                "acquire"   :   lambda x: 1,
                "release"   :   lambda x: 1, 
                "io"        :   lambda x: x["cycles"],
                "calculate" :   lambda x: x["cycles"],
                "out"       :   lambda x: 1,
                "yield"     :   lambda x: 1,
                "exe"       :   lambda x: 1,
            }[self.op](instr)
            if self.cycle is None:
                self.cycle = randint(1, 100)

            self.mem_list = memory.allocate(instr["memory"])
        except ValueError:
            DebugPrint("[Process] Improper Instruction")
            raise ex.ImproperInstructionError

    def __del__(self):
        if self.mem_list:
            memory.deallocate(self.mem_list)

    def run(self):
        memory.access(self.mem_list)
                

class Process:
    def __init__(self, filename, pid, queue):
        with open(filename, "r") as f:
            dump = json.load(f)

        self.name = dump["name"]

        self.size = 0
        for instr in dump["instructions"]:
            self.size += instr["memory"]
        if self.size > memory.remaining():
            raise ex.MemoryAllocationError

        self.text = list()
        for instr in dump["instructions"]:
            self.text.append(Instruction(self, instr))

        self.pc = self.priority = self.time = 0
        self.mutexes = list()
        self.pid = pid
        self.cycles_left = self.text[0].cycle
        self.queue = queue

    def setQueue(self, queue):
        self.queue = queue

    def setTime(self, time):
        self.cycles_left = time

    def run(self):
        self.time += 1
        self.cycles_left -= 1
        self.text[self.pc].run
        if self.cycles_left:
            DebugPrint(f"[Process] PID {self.pid} just ran {self.text[self.pc].op}")
            return True
        else:
            DebugPrint(f"[Process] PID {self.pid} just ended {self.text[self.pc].op}")
            self.pc += 1
            self.cycles_left = self.text[self.pc].cycle
            return False

    def currentInstr(self):
        return self.text[self.pc].op
        
    def hasMutex(self, mon):
        return self.mutexes.count(mon)

    def setMutex(self, mon):
        self.mutexes.append(mon)

    def unsetMutex(self, mon):
        self.mutexes.remove(mon)

    def getInstrArg(self):
        return self.text[self.pc].arg

    def incrementPC(self):
        self.pc += 1
        self.cycles_left = self.text[self.pc].cycle

    def __str__(self):
        s = f"Process ID {self.pid}\n"
        s += f"\tName: {self.name}\n"
        s += f"\tMemory: {self.size} MB\n"
        s += f"\tElapsed time: {self.time} cycles\n"
        s += f"\tText section: {len(self.text)} instructions\n"
        s += f"\tCurrent instruction: {self.currentInstr()}\n"
        s += f"\tTime left in current instruction: {self.cycles_left}"

        return s            
            

    