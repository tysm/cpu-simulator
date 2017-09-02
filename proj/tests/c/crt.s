.globl __crt_main
__crt_main:

# Puts $sp at the top of the memory space ($sp=0xFFFF)
# (TODO not opcode!)
addi $a0,$zero,6
ori $sp,$sp,0x3F
sll $sp,$sp,$a0
ori $sp,$sp,0x3F
sll $sp,$sp,$a0
ori $sp,$sp,0x3F

# Calls main (argc and argv not defined in our C Standard)
j $ra,main

# Put return value at $s0 and mark $ra with 0xFFFF
# Those steps will help the interpreter stop.
add $s0,$zero,$v0
add $ra,$zero,$sp  # $ra = $sp = 0xFFFF

# Finally, halts the CPU.
__crt_halt:
j $0,__crt_halt
