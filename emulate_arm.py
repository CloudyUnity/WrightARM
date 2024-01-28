# Python 2 compatibility
from __future__ import print_function

from unicorn import *
from unicorn.arm_const import *
import os
import sys
from capstone import *
import subprocess
import shutil
import re
import time
import platform

ADDRESS = 0x8000000
RAM_ADDRESS = 0x20000000
STACK_ADDRESS = 0x2001000

MAX_RUNNING_SECONDS = 10
BUILD_NAME = "strongArmBuild"
USE_LINKER = True

QUIT_LABEL = "Terminate"
START_LABEL = "Reset_Handler"

debug_instructions = False # -i
debug_machine_code = False # -mc
debug_elf = False # -elf
debug_reg = False # -r
debug_profile = False # -p
debug_save_build = False # --debug_save_build

quit_address = None
start_address = None

# For profiling
instructions = 0
instruction_bytes = 0
cycles = 0
last_address = None

def assemble_and_link(cwd):
    global quit_address
    global start_address
    
    # Destroy exisiting build directory if existing
    buildDir = os.path.join(cwd, BUILD_NAME)
    if (os.path.exists(buildDir)):
        shutil.rmtree(buildDir)
        
    os.mkdir(buildDir)
    
    # Assemble .s files to .o files
    for file in os.listdir(cwd):
        if file.endswith('.s'):
            file_path = os.path.join(cwd, file)
            # Append newline to assembly file in case user removed it
            with open(file_path, "a") as armFile:
                armFile.write("\n")
            output_file_path = os.path.join(buildDir, f'{os.path.splitext(file)[0]}.o')
            subprocess.run(['arm-none-eabi-as', '-o', output_file_path, file_path])
            
    # Include startup.s (Found in StrongArm folder)
    startup_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "startup.s")
    startup_dest = os.path.join(buildDir, "startup.o")
    subprocess.run(['arm-none-eabi-as', '-o', startup_dest, startup_path])

    # Link .o files to .elf file
    object_files = [os.path.join(buildDir, f) for f in os.listdir(buildDir) if f.endswith('.o')]
    elf_dest = os.path.join(buildDir, 'finalBuild.elf')
    if (USE_LINKER):
        linker_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Linker.ld")
        subprocess.run(['arm-none-eabi-ld', '-T', linker_path, '-o', elf_dest, *object_files])
    else:
        subprocess.run(['arm-none-eabi-ld', '-o', elf_dest, *object_files])
    
    # Find quit address       
    command_readelf = ['readelf', '-sW', elf_dest]
    process_readelf = subprocess.Popen(command_readelf, stdout=subprocess.PIPE)
    readelf_output = process_readelf.communicate()[0].decode()    
        
    command_name_for_os = 'findstr' if platform.system() == "Windows" else 'grep'
    command_findstr = [command_name_for_os, f'{QUIT_LABEL}']
    quit_result = subprocess.run(command_findstr, input=readelf_output, shell=True, text=True, capture_output=True)        
    quit_address = int(quit_result.stdout.split()[1], 16)
    
    # Find start address
    command_findstr = [command_name_for_os, f'{START_LABEL}']
    start_result = subprocess.run(command_findstr, input=readelf_output, shell=True, text=True, capture_output=True)        
    start_address = int(start_result.stdout.split()[1], 16)
    
    if (debug_elf):
        print(readelf_output)
        print("QUIT: " + str(quit_address))
        print("START: " + str(start_address))
    
    # Convert .elf to .bin
    bin_dest = os.path.join(buildDir, 'finalBuild.bin')
    subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary', elf_dest, bin_dest])

def hook_code(uc, address, size, user_data):
    global instructions
    global instruction_bytes   
    global last_address
    global cycles      
    
    code_bytes = uc.mem_read(address, size)
    
    # Convert the bytes to a human-readable string
    instruction_str = ''.join(['%02x ' % x for x in code_bytes]).strip()

    # Disassemble the instruction using Capstone
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    disassembly = list(md.disasm(code_bytes, address))
    
    instructions += 1
    instruction_bytes += size 
    
    if (disassembly[0].mnemonic.lower().startswith("bkpt")):
        print(f"BREAKPOINT HIT! Address: 0x{address:08X}.")        
        uc.emu_stop()
    
    # Certain instructions add extra cycles
    add_cycles(disassembly, "udiv", 3)
    add_cycles(disassembly, "sdiv", 3)
    add_cycles(disassembly, "ldr", 1)
    add_cycles(disassembly, "str", 1)
    add_cycles(disassembly, "mla", 1)
    
    # Branching adds 2 extra cycles
    if (last_address != None and (address - last_address > 4 or address - last_address < 2)):
        cycles += 2
        if (debug_instructions):
            print("Branched!")
    last_address = address

    # Print the address, instruction bytes, and disassembly
    if (debug_instructions):
        trailingX = " XX XX" if size == 2 else ""
        print(f"Executing instruction at 0x{address:08X}: {instruction_str}{trailingX} | {disassembly[0].mnemonic} {disassembly[0].op_str} ({size})")  
        
def add_cycles(disassembly, check_str, cycle_bonus):
    global cycles
    if (disassembly[0].mnemonic.lower().startswith(check_str)):
        cycles += cycle_bonus 
    
def check_registers():  
    r0 = mu.reg_read(UC_ARM_REG_R0)
    r1 = mu.reg_read(UC_ARM_REG_R1)
    r2 = mu.reg_read(UC_ARM_REG_R2)
    r3 = mu.reg_read(UC_ARM_REG_R3)
    r4 = mu.reg_read(UC_ARM_REG_R4)
    r5 = mu.reg_read(UC_ARM_REG_R5)
    r6 = mu.reg_read(UC_ARM_REG_R6)
    r7 = mu.reg_read(UC_ARM_REG_R7)
    r8 = mu.reg_read(UC_ARM_REG_R8)
    r9 = mu.reg_read(UC_ARM_REG_R9)
    r10 = mu.reg_read(UC_ARM_REG_R10)
    r11 = mu.reg_read(UC_ARM_REG_R11)
    r12 = mu.reg_read(UC_ARM_REG_R12)
    sp = mu.reg_read(UC_ARM_REG_SP)
    lr = mu.reg_read(UC_ARM_REG_LR)
    pc = mu.reg_read(UC_ARM_REG_PC)
    cpsr = mu.reg_read(UC_ARM_REG_CPSR)
    spsr = mu.reg_read(UC_ARM_REG_SPSR)   
    print(f"R0:   0x{r0:08X} ({r0})")
    print(f"R1:   0x{r1:08X} ({r1})")
    print(f"R2:   0x{r2:08X} ({r2})")
    print(f"R3:   0x{r3:08X} ({r3})")
    print(f"R4:   0x{r4:08X} ({r4})")
    print(f"R5:   0x{r5:08X} ({r5})")
    print(f"R6:   0x{r6:08X} ({r6})")
    print(f"R7:   0x{r7:08X} ({r7})")
    print(f"R8:   0x{r8:08X} ({r8})")
    print(f"R9:   0x{r9:08X} ({r9})")
    print(f"R10:  0x{r10:08X} ({r10})")
    print(f"R11:  0x{r11:08X} ({r11})")
    print(f"R12:  0x{r12:08X} ({r12})")
    print(f"SP:   0x{sp:08X} ({sp})")
    print(f"LR:   0x{lr:08X} ({lr})")
    print(f"PC:   0x{pc:08X} ({pc})")
    print(f"CPSR: 0x{cpsr:08X} ({cpsr})")
    print(f"SPSR: 0x{spsr:08X} ({spsr})")

def print_help():
    print("Here's all the flags:")
    print(" General Use:")
    print("     [-p] to check the performance of the code")
    print("     [-i] to see each instruction as it is executed")
    print("     [-r] to see what is in each register after the code runs")
    print("     [-T X] (Where X is a number) to force the program to close early. X is 10 by default")
    print(" Debug Use:")
    print("     [-mc] to see the machine code")
    print("     [--debug_save_build] to prevent deletion of compiled files. They will appear next to your arm files")
    
def delete_build_dir():
    buildDir = os.path.join(cwd, BUILD_NAME)
    if (os.path.exists(buildDir)):
        shutil.rmtree(buildDir, ignore_errors=True)
        
def print_profiling():
    global instructions
    global instruction_bytes   
    global last_address
    global cycles  
    
    end_time = time.time()
    time_difference_ms = (end_time - start_time) * 1000
    cycles += instructions    
    print("\nProfiling:")
    print("Time (ms): " + str(round(time_difference_ms * 1000) / 1000))
    print("Instructions: " + str(instructions))
    print("Instruction bytes: " + str(instruction_bytes))
    print("Cycles: " + str(cycles))
    print("Cycles (modifed for submitty): " + str(cycles * 19))
    
try:
    if (len(sys.argv) - 1 == 0):
        print_help()
        sys.exit()
        
    # Manage argument flags
    for i, arg in enumerate(sys.argv[1:]):
        if (arg == "-i"):
            debug_instructions = True
        if (arg == "-mc"):
            debug_machine_code = True
        if (arg == "-elf"):
            debug_elf = True
        if (arg == "-r"):
            debug_reg = True
        if (arg == "-p"):
            debug_profile = True
        if (arg == "--debug_save_build"):
            debug_save_build = True
        if (arg == "-T"):
            MAX_RUNNING_SECONDS = float(sys.argv[i+2])   
        if (arg == "-help"):
           print_help()
    
    # Build program
    cwd = os.getcwd()
    assemble_and_link(cwd)    
    path = os.path.join(cwd, BUILD_NAME, "finalBuild.bin")
    
    with open(path, 'rb') as file:
        code = file.read()    
    file.close()
    
    if (debug_machine_code):
        print("Assembled code:")       
        print(code)
    
    # Initalise unicorn into ARM THUMB mode
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)

    # Map memory for this emulation, See linker script for more details
    mu.mem_map(ADDRESS, 128 * 1024, UC_PROT_ALL)
    mu.mem_map(RAM_ADDRESS, 8 * 1024, UC_PROT_ALL)
    mu.mem_map(STACK_ADDRESS, 4 * 1024, UC_PROT_ALL)

    # Write machine code to be emulated to memory
    mu.mem_write(ADDRESS, code)    
    mu.hook_add(UC_HOOK_CODE, hook_code)
    
    # Start emulation. Will exit if it hits quit_address (Terminate Label in startup.s) or after x seconds
    start_time = time.time()    
    secs = MAX_RUNNING_SECONDS*1000*1000
    
    print("Emulation start")
    mu.emu_start(start_address | 1, quit_address, timeout=int(secs))        
    
    if (not debug_save_build):
        delete_build_dir()
    
    if (debug_reg):
        print("\nEmulation done. Below is the CPU context")    
        check_registers()
    
    if (debug_profile):
        print_profiling()

except UcError as e:
    print("ERROR: %s" % e)    
    if (debug_reg and mu != None):
        print("There was an error, below is the CPU context")    
        check_registers()    