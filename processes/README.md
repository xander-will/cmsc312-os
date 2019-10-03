Usage:

python converter.py [optional list of file names]

---

JSON process files can be dumped into this folder and converted
to .pf bytecode that is used by the OS simulator. 

As of October 3rd, 2019, these are the required fields for the processes:
    name - string - This is used for the filename, and is           stored in the file header
    memory - int - This is the memory used by the process,
        if larger than 0xFFFF it is floored to 0xFFFF
    instructions - array - This is the list of instructions,       the number of instructions is calculated during conversion

Each instruction requires these fields:
    operation - string - This is the operation performed by
        the instruction
    cycles - int - This is only required for calculate and io
        at the moment, is the number of cycles required
        if cycles is put as NULL, it is passed in as a magic
        number that will generate a random value once read
        into the OS, thus allowing use of these files as templates