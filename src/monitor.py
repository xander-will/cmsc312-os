from src.globals import DebugPrint

class Monitor:

    def __init__(self, id):
        self.id = id
        self.val = False
        self.wait = list()
        self.current = None

    def get(self):
        return self.val

    def set(self, x):
        self.val = x

    def acquire(self, proc):
        if self.current:
            DebugPrint("[Monitor] Waiting on mutex")
            self.wait.append(proc)
            return False
        else:
            DebugPrint("[Monitor] Acquiring mutex")
            self.current = proc
            proc.setMutex(self.id)
            return True 

    def release(self):
        DebugPrint("[Monitor] Releasing mutex")
        self.current.unsetMutex(self.id)
        try:
            self.current = self.wait.pop()
            self.current.setMutex(self.id)
            return self.current
        except IndexError:
            return None

