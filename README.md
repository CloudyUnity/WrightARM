Finn Wright's WrightARM Emulator  

This was made to profile ARM assembly programs  
This was made for and released to the entire TCD Computing class 2023/2024  
It uses Unicorn, QEMU and Python  

cmd = Command Line Prompt  

HOW TO INSTALL (WINDOWS):  
    Make sure python is installed, otherwise:  
        type "python" into cmd. It should take you to the microsoft store where you can install it  

    Install unicorn with:
        cmd > pip install unicorn

    Make sure MinGW-w64 is installed:
        https://sourceforge.net/projects/mingw-w64/files/Toolchains%20targetting%20Win64/Automated%20Builds/
        https://www.youtube.com/watch?v=1TPmiiAqmlc

    Install ARM GNU Toolchain:
        https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads
        Download "arm-gnu-toolchain-13.2.rel1-mingw-w64-i686-arm-none-eabi.exe" and follow installation

    Make sure Python, MinGW-w64 and ARM GNU are all added to the environment path variables:
        Go to "Edit the system environment path variables" in the search bar
        Click on "Environment Variables"
        Click on "PATH" in "System Variables" and press "Edit"
        Add file paths as "New" to the "bin" subfolders in mentioned downloads
        (Python should give you the option to do this automatically when installing)

    Also add this folder (StrongARM) to environment path variables:
        See above
    
HOW TO USE (WINDOWS):  
    cmd > cd "/path/to/src"  
    For example with bitPattern on my computer:  
        cmd > cd "C:\Users\finnw\OneDrive\Documents\Trinity\CS\Computing\1791-bitpattern\src"  
        The src folder should contain both test.s and bitPattern.s  

    cmd > emulate_arm.py [FLAGS]     
    For example:   
        cmd > emulate_arm.py -p -r -i -elf -T 5  

FLAGS:  
    These flags allow you to debug your program in different ways  
    You can chain as many flags together as you want  
    "-help":  
        Get quick info on all the flags  
    "-r":  
        Check the final state of all the registers  
    "-p":  
        Check performance of your program in terms of time, instructions and cycles  
        Note that the cycles are nowhere near as large as the submitty cycles for some reason. But this program isn't to determine the exact cycle count of your assembly but instead to find changes in performance as you modify it  
    "-i":  
        See all the instructions ran by the program, their machine code and addresses  
    "-mc":  
        See the raw bytes of the assembly .bin file  
    "-elf":  
        See the ELF Symbol Table for the program. You can see the addresses of all labels and stored data  
    "-T {seconds}":  
        Changes the maximum running time to {seconds} after which the emulation force closes  
        This is 10 seconds by default. I recommend you don't make it too long in case you have an infinite loop  
    "--save_build":  
        Prevents the build being destroyed after the program finishes. Maybe you're curious what's in there  
