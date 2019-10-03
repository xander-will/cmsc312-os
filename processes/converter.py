import json

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
            yield { "name": f.name.strip('.'), "json": json.load(f) }
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
            b = bytearray([instruction_table.get(ins["operation"])])
            if ins["operation"] != "exe":
                if ins["cycles"] is None:
                    b.append([255])
                else:
                    b.append(max(ins["cycles"], 254))
            yield b
        except KeyError:
            print(f"This instruction is not valid: {ins}")

def ito2bytes(x):
    if x < 256:
        return bytearray([x])
    else:
        return bytearray([max(x/256, 255), x & 0xFF])

def bytes_gen(dicts):
    for d in dicts:
        try:
            b = bytearray([0x70, 0x66])  # sanity check: "pf" as first two bytes
            b.append(d["name"].encode("utf-8"))
            b.append(ito2bytes(d["memory"]))
            b.append(max(len(d["instructions"], 255)))
            instr_bytes = instr_gen(d["instructions"][:255])
            for ib in instr_bytes:
                b.append(ib)

            filename = "bytecode\\" + d["name"] + ".pf"
            with open(filename, "wb") as f:
                f.write(b)

            yield filename
        except KeyError:
            print("JSON file is formatted incorrectly, skipping this file")
        except: # this needs to be for the file io is fucked
            pass 

# todo: 
#   check the command line for arguments
#   if args: parse just those files
#   else: scan directory for all .json files
#
#   initalize generators
#   the loop should be over bytes_gen
#   all it needs to do is print out each
#   successful filename as it finishes
            
        