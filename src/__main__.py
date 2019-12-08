from glob import glob

from src.simulator import Simulator

filelist = glob("./processes/*.json")
s = Simulator(10, filelist)

while True:
    s.run()