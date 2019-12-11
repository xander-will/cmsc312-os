# it would be remiss of me not to thank George Constantine...
# much of the framework from this comes from our RISC emulator
# project earlier this semester, which he contributed to

import wx
import os

from threading import Thread
from time import sleep

import src.commands as c

from src.globals import gui_mailbox, sim_mailbox

class frame(wx.Frame):

    def __init__(self, parent, title):
        super(frame, self).__init__(parent, title=title, size=(500, 500))
        self.proc_out = ""
        self.stats = ""
        self.InitUI()
        self.newFrame = None

    def SetStrings(self):
        self.proc_box.Clear()
        for line in self.proc_out.replace('\t','').split('\n'):
            self.proc_box.AppendText(line + '\n')
        self.stat_box.Clear()
        for stat in self.stats:
            self.stat_box.AppendText(stat)

    def InitUI(self):
        toolbar = self.CreateToolBar(style = wx.TB_TEXT | wx.TB_NOICONS)
        addtool = toolbar.AddTool(wx.ID_ANY, 'Add', wx.Bitmap())
        runtool = toolbar.AddTool(wx.ID_ANY, 'Run', wx.Bitmap())
        stoptool = toolbar.AddTool(wx.ID_ANY, 'Stop', wx.Bitmap())
        speedtool = toolbar.AddTool(wx.ID_ANY, 'Speed', wx.Bitmap())
        switchtool = toolbar.AddTool(wx.ID_ANY, 'Switch', wx.Bitmap())
        randtool = toolbar.AddTool(wx.ID_ANY, 'Rand', wx.Bitmap())
        quanttool = toolbar.AddTool(wx.ID_ANY, 'Quant', wx.Bitmap())
        toolbar.Realize()

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.HORIZONTAL)
        otherbox = wx.BoxSizer(wx.VERTICAL)

        self.stat_box = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(250, 900))
        self.proc_box = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(250, 900))

        box.Add(self.proc_box, 0, wx.EXPAND)

        otherbox.Add(self.stat_box, 1, wx.ALL|wx.EXPAND)

        box.Add(otherbox)

        panel.SetSizer(box)
        panel.Fit()

        self.Bind(wx.EVT_TOOL, self.onAdd, addtool)
        self.Bind(wx.EVT_TOOL, self.onRun, runtool)
        self.Bind(wx.EVT_TOOL, self.onStop, stoptool)
        self.Bind(wx.EVT_TOOL, self.onSpeed, speedtool)
        self.Bind(wx.EVT_TOOL, self.onSwitch, switchtool)
        self.Bind(wx.EVT_TOOL, self.onRand, randtool)
        self.Bind(wx.EVT_TOOL, self.onQuant, quanttool)

        self.SetSize((500, 300))
        self.SetTitle('OS Simulator')
        self.Centre()

    def onQuant(self, event):
        x = wx.GetNumberFromUser("OS Simulator", "What would you like the quantum to be?", 
                                    "User Entry", 10, max=1000, parent=self)
        if x < 0:
            return

        sim_mailbox.put(c.Cmd_Quantum(x))

    def onRand(self, event):
        x = wx.GetNumberFromUser("OS Simulator", "How many of this process would you like to open?", 
                                    "User Entry", 5, max=1000, parent=self)
        if x < 0:
            return

        sim_mailbox.put(c.Cmd_RandProcess(x))

    def onSwitch(self, event):
        sim_mailbox.put("switch")

    def onSpeed(self, event):
        x = wx.GetNumberFromUser("OS Simulator", "Enter a new refresh rate in hundredths of a second: ", 
                                    "User Entry", 5, max=1000, parent=self)
        if x < 1:
            return
        sim_mailbox.put(c.Cmd_ChangeSpeed(x))

    def onRun(self, event):
        sim_mailbox.put("run")

    def onStop(self, event):
        sim_mailbox.put("stop")

    def onAdd(self, event):
        wildcard = "Processes (*.json)|*.json"
        dialog = wx.FileDialog(self, "Open Process", wildcard=wildcard,
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
                               defaultDir="./processes")

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        path = dialog.GetPath()

        x = wx.GetNumberFromUser("OS Simulator", "How many of this process would you like to open?", 
                                    "User Entry", 5, max=1000, parent=self)
        if x < 1:
            return

        if os.path.exists(path):
            sim_mailbox.put(c.Cmd_CreateProcess(path, x))
        else:
            msg = wx.MessageDialog(self, "File does not exist!", style=wx.OK)
            msg.ShowModal()

    def ErrorMsg(self, s):
        msg = wx.MessageDialog(self, s, style=wx.OK)
        msg.ShowModal()
        
        

def GUI_MainThread():
    app = wx.App()
    ex = frame(None, title='Sizing')
    ex.Show()

    Thread(target=GUI_UpdateThread, args=(ex,)).start()

    app.MainLoop()
    gui_mailbox.put("close")
    sim_mailbox.put("close")
    

def GUI_UpdateThread(gui):
    while True:
        cmd = gui_mailbox.get()

        if isinstance(cmd, c.Cmd_ProcOut):
            gui.proc_out = cmd.s
            gui.SetStrings()
        elif isinstance(cmd, c.Cmd_Stats):
            gui.stats = cmd.s
            gui.SetStrings()
        elif cmd == "close":
            exit()
        elif isinstance(cmd, c.Cmd_Error):
            gui.ErrorMsg(cmd.s)