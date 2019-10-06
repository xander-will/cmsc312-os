## XOS: Simulated Operating System for CMSC 312
#### Written by Xander Will, Fall 2019

To build, run `build`, same for `run`

This program uses the MinGW runtime and thus may work on non-Windows machines as long as gcc is used... as I do not own one I have not tested it!

Process files must be written in JSON, please check the README in the processes folder for more information.

##### Notes:
Although it was requested that user-specified processes be run, my implementation currently just loads all of the processes contained in the `./processes/bytecode` folder and then will generate a random number of each one. This should hopefully fulfills the template/random instruction generation features requested, without requiring a tedious scanf routine involving sending an array of "# of processes" to the dispatcher... aka I was in a bit of a rush and was lazy (presumably once I get the actual CLI working this would be included)

I have left my debug prints in due to not having an interface otherwise. Note that this causes some oddities such as OUT instructions printing out the PCB right after my debug prints do the same thing

I haven't extensively checked the options, though I can confirm that `-t` does work if you don't mind an off by one issue. For testing I was running `-t 2` aka 3 cycles at a time, which is why the cycle lengths in the processes are relatively short. The randomization also produces relatively low numbers tho this will be changed later. `-d` will not do anything at the moment due to the system being hardcoded for pause mode only (I believe I solved the issues but since I need to move on to working on other things I'm not going to reenable it at the moment)