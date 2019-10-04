## 
##  CMSC 312
##  Xander Will
##
##  'converter.py'
##  "Creates a bytecode representation of a json process file"
##
##  October 2019
##

import glob
import sys
import json

def walk_gen():
    for name in glob.glob("./*.json"):
        print(f"Found {name}")
        yield name

def file_gen(paths):
    for p in paths:
        try:
            print(f"Reading file {p}...")
            yield open(p, 'r')
        except FileNotFoundError:
            print(f"Could not find file {p}")

def dict_gen(files):
    for f in files:
        try:
            print(f"Loading file {f.name}...")
            yield json.load(f)
        except json.JSONDecodeError:
            print(f"{f.name} is not a valid JSON file")
        finally:
            f.close()

instruction_table = {
    "exe"       :   0,
    "calculate" :   1,
    "io"        :   2,
    "yield"     :   3,
    "out"       :   4
}
def instr_gen(instructions):
    for ins in instructions:
        try:
            b = bytearray([instruction_table.get(ins["operation"].lower())])
            if ("calculate", "io").count(ins["operation"]) == 1:
                if ins["cycles"] is None:
                    b.append(255)
                else:
                    b.append(min(ins["cycles"], 254))
            yield b
        except KeyError:
            print(f"This instruction is not valid: {ins}")

def ito2bytes(x):
    if x < 256:
        return bytearray([x])
    else:
        return bytearray([min(x/256, 255), x & 0xFF])

def bytes_gen(dicts):
    for d in dicts:
        try:
            print(f"Generating bytecode for {d['name']}...")
            b = bytearray([0x70, 0x66])  # sanity check: "pf" as first two bytes
            b.extend(d["name"].encode("utf-8"))
            b.append(0)
            b.extend(ito2bytes(d["memory"]))
            b.append(min(len(d["instructions"]), 255))
            instr_bytes = instr_gen(d["instructions"][:255])
            for ib in instr_bytes:
                b.extend(ib)

            filename = "bytecode\\" + d["name"] + ".pf"
            print(f"Writing {filename}...")
            with open(filename, "wb") as f:
                f.write(b)

            yield filename
        except KeyError:
            print("JSON file is formatted incorrectly, skipping this file")
            
print("File conversion starting!")
if len(sys.argv) < 2:
    wg = walk_gen()
else:
    wg = (name for name in sys.argv[1:])

pg = (name for name in wg if len(name.split('.')) > 1 and name.split('.')[-1] == 'json')
fg = file_gen(pg)
dg = dict_gen(fg)
bg = bytes_gen(dg)
for filename in bg:
    print(f"{filename} has been successfully written!\n") 