class Cmd_CreateProcess:
    def __init__(self, filepath, num):
        self.filepath = filepath
        self.num = num

class Cmd_Quantum:
    def __init__(self, x):
        self.x = x

class Cmd_Stats:
    def __init__(self, s):
        self.s = s

class Cmd_ProcOut:
    def __init__(self, s):
        self.s = s

class Cmd_ChangeSpeed:
    def __init__(self, x):
        self.x = x / 100

class Cmd_Error:
    def __init__(self, s):
        self.s = s

class Cmd_RandProcess:
    def __init__(self, x):
        self.x = x  