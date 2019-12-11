
from random import randint
from time import sleep

import src.commands as c

from src.globals import DebugPrint, sim_mailbox, gui_mailbox
from src.dispatcher import Dispatcher

def PauseExecution():
    print("Type exit to close or newline to continue")
    if input() == "exit":
        exit()

def Sim_MainThread():
    s = Simulator(10, list())
    while True:
        s.loop()

class Simulator:

    def __init__(self, quant, filelist):
        DebugPrint("[Simulator] Beginning initialization")

        self.dis = Dispatcher(quant, filelist)
        self.mode = False   # kernal mode
        self.cycles_since_pause = 0
        self.delay = 0
        self.io = False 
        self.io_cycles = 0
        self.total_cycles = 0
        self.on_flag = False
        self.refresh_time = 0.5
        self.clock_time = 0

        DebugPrint("[Simulator] Successfully initialized!")

    def checkMail(self):
        if sim_mailbox.empty():
            DebugPrint("[Simulator] No messages")
            return

        cmd = sim_mailbox.get()
        DebugPrint(f"[Simulator] Message: {cmd}")

        if cmd == "run":
            self.on_flag = True
        elif cmd == "stop":
            self.on_flag = False
        elif isinstance(cmd, c.Cmd_CreateProcess):
            for _ in range(cmd.num):
                self.dis.createProcess(cmd.filepath)
        elif isinstance(cmd, c.Cmd_Quantum):
            self.dis.quant = cmd.x
        elif cmd == "close":
            exit()
        elif isinstance(cmd, c.Cmd_ChangeSpeed):
            self.refresh_time = cmd.x
        elif cmd == "switch":
            self.dis.switch()
        elif isinstance(cmd, c.Cmd_RandProcess):
            self.dis.randomProcess(cmd.x)

    def loop(self):
        self.checkMail()
        if self.on_flag:
            self.run()
        sleep(self.refresh_time)
        self.clock_time += self.refresh_time

    def stats(self):
        return [f"Total cycles: {self.total_cycles}\n"] + self.dis.stats()

    def run(self):
        self.total_cycles += 1
        DebugPrint(f"[Simulator] Cycle {self.total_cycles}")
        
        if not self.io and randint(0, 99) < 5:
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
            self.mode = self.dis.runCurrent()
        else:           # kernal mode
            DebugPrint("[Simulator] In Kernel Mode")
            self.dis.schedule()
            self.mode = True

        if self.total_cycles % 5 == 0:
            gui_mailbox.put(c.Cmd_Stats(self.stats()))

                