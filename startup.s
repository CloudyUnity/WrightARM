.thumb
.syntax unified
.cpu cortex-m3
.fpu softvfp

.extern _load_address

.global Reset_Handler

.section .text

  .weak  Reset_Handler
  .type  Reset_Handler, %function
Reset_Handler:    
    BL Init_Mem     @ Set up memory
    BL Init_Test    @ Run test.s
    BL Main         @ Run Main
    NOP             @ Debug purposes    

Terminate:
    NOP     @ Emulation always terminates on this line
    B Terminate
  .size  Reset_Handler, .-Reset_Handler

 .type     Init_Mem, %function
Init_Mem:                   @ Copies all data from FLASH memory to RAM 
  LDR R0, =_load_address
  LDR R1, =_sdata
  LDR R2, =_edata  

copy_data:                  @ Loop to copy everything
  CMP R1, R2
  BEQ stop_copy

  LDR R3, [R0], #4          
  STR R3, [R1], #4
  B copy_data 

stop_copy:
    MOV R0, #0              @ Reset all registers back to 0
    MOV R1, #0
    MOV R2, #0
    MOV R3, #0
    BX LR

.section .data
load_address:
  .word _load_address

sdata:
  .word _sdata

edata:
  .word _edata

.end   
