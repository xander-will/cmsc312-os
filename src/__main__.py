from threading import Thread

from src.gui import GUI_MainThread
from src.simulator import Sim_MainThread

#g_thr = Thread(target=GUI_MainThread)
s_thr = Thread(target=Sim_MainThread)
s_thr.start()

GUI_MainThread()

#g_thr.start()
