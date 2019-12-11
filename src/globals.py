from queue import Queue

debug = False

def DebugPrint(s):
    if debug:
        print(s)

gui_mailbox = Queue()
sim_mailbox = Queue()

