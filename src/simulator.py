
from random import randint

from src.globals import DebugPrint
from src.dispatcher import Dispatcher

def PauseExecution():
    print("Type exit to close or newline to continue")
    if input() == "exit":
        exit()

class Simulator:

    def __init__(self, quant, filelist):
        DebugPrint("[Simulator] Beginning initialization")

        self.dis = Dispatcher(quant, filelist)
        self.mode = False   # kernal mode
        self.cycles_since_pause = 0
        self.delay = 2
        self.io = False 
        self.io_cycles = 0
        self.total_cycles = 0

        DebugPrint("[Simulator] Successfully initialized!")

    def run(self):
        self.total_cycles += 1
        DebugPrint(f"[Simulator] Cycle {self.total_cycles}")
        
        if not self.io and randint(0, 99) < 1:
            self.io = True 
            self.io_cycles = randint(25, 50)
            self.dis.setIO(True)
            DebugPrint("[Simulator] IO event")
        elif self.io:
            if self.io_cycles <= 0:
                self.io = False
                self.dis.setIO(False)
            else:
                self.io_cycles -= 1

        if self.mode:   # user mode
            DebugPrint("[Simulator] In User Mode")
            self.mode = self.dis.runCurrProc()
        else:           # kernal mode
            DebugPrint("[Simulator] In Kernel Mode")
            self.dis.schedule()
            self.mode = True

        if self.cycles_since_pause == self.delay:
            self.cycles_since_pause = 0
            PauseExecution()
        else:
            self.cycles_since_pause += 1

        print("\n")
        