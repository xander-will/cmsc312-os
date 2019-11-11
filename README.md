## XOS: Simulated Operating System for CMSC 312
#### Written by Xander Will, Fall 2019

To build, run `build`, same for `run`

This program uses the MinGW runtime and thus may work on non-Windows machines as long as gcc is used... as I do not own one I have not tested it!

Process files must be written in JSON, please check the README in the processes folder for more information.

##### Notes:
Although it was requested that user-specified processes be run, my implementation currently just loads all of the processes contained in the `./processes/bytecode` folder and then will generate a random number of each one. This should hopefully fulfills the template/random instruction generation features requested, without requiring a tedious scanf routine involving sending an array of "# of processes" to the dispatcher... aka I was in a bit of a rush and was lazy (presumably once I get the actual CLI working this would be included)

I have left my debug prints in due to not having an interface otherwise. Note that this causes some oddities such as OUT instructions printing out the PCB right after my debug prints do the same thing

I haven't extensively checked the options, though I can confirm that `-t` does work if you don't mind an off by one issue. For testing I was running `-t 2` aka 3 cycles at a time, which is why the cycle lengths in the processes are relatively short. The randomization also produces relatively low numbers tho this will be changed later. `-d` will not do anything at the moment due to the system being hardcoded for pause mode only (I believe I solved the issues but since I need to move on to working on other things I'm not going to reenable it at the moment)

	Project 2:
	
I frankly don't know if this works or not. I was in crunch time pre-midnight (like, 11:45) and ran across a final bug where the program crashed in what I assumed to be memory deallocation. I went ahead and added a debug print to find the exact spot of the crash (probably some pointer thing) when suddenly my program stopped working.
The program crashes at some point during initialization, though the exact spot varies. I have singled out two cases that seem to indicate the issue:
1) In the middle of l_init() (which is the constructor for my generic list type)
	Specifically, it crashes right after the malloc() call. That indicates something right off the bat.
2) Right after the dispatcher finishes initialization (in the constructor for the simulator)
	The only danger point here is the free-ing of the filename strings immediately afterwards. This code was written during part 1 and has
	no reason to be not working now, considering that not a single line of code was added to the simulator top-level class nor the main.c file
	that contains the file scraper
	
Somewhere in here my heap is getting corrupted, and I have no idea where. I generally consider myself pretty rigorous about maintaing memory properly and it is confusing how a segment of code that has been working for over a month now suddenly crashed. I am not sure if I managed to mess up something important with an erratic pointer dereference or if there's just general heap corruption going on somewhere in my program. Finding this will take sitting down with a memory manager debugger and I frankly don't have the time or energy for that right now. At the very least I'm going to restart my computer and see if that changes anything.

Regardless, the code here is very solid and should prove that I have been working on it. It may even work properly on your machine!! (though expect process deallocation to throw some errors, I'm sure I messed up some memory management in there, specifically with the simulator's memory deallocation routine most likely)