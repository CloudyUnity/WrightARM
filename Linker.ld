/* Highest address of the user mode stack */
_estack = ORIGIN(RAM) + LENGTH(RAM);    /* end of RAM */

/* Generate a link error if the stack does't fit into RAM */
_Min_Stack_Size = 0x400; /* required amount of stack */

/* Specify the memory areas */
MEMORY
{
RAM (rw)      : ORIGIN = 0x20000000, LENGTH = 8K
FLASH (rx)      : ORIGIN = 0x8000000, LENGTH = 128K
}

/* Define output sections */
SECTIONS
{
  /* The program code and other data goes into FLASH */
  .text :
  {
    *(.text*)                  /* .text sections (code) */
  } >FLASH

  /* Constant data goes into FLASH */
  .rodata :
  {
    . = ALIGN(4);
    *(.rodata*)                /* .rodata sections (constants, strings, etc.) */
  } >FLASH

  /* Not currently used for bare betal but define for future use */
  .bss :
  {
    . = ALIGN(4);
    _sbss = . ;
    *(.bss .bss.*)
    *(COMMON)
    _ebss = . ;
  } >RAM

  /* Initialized data sections goes into RAM, load LMA copy after RODATA */
  .data : 
  {
    PROVIDE(_load_address = LOADADDR(.data));
    . = ALIGN(4);
    _sdata = .;
    KEEP(*(.data.test))       /* .data sections for test.s should go before student data */
    . = ALIGN(4);
    KEEP(*(.data*))           /* .data sections for student */
    _edata = .;
  } >RAM AT>FLASH
}
