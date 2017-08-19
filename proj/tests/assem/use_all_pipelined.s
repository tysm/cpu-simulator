lbl1:	addi $s0 $0 -1
	add  $s1 $0 $s0
	lui  0x3FF
	mflo $s2 
	ori  $s2 $s2 0x3F
	bne  $s0 $s2 lbl2
	andi $s0 $s0 0
        and  $s1 $s1 $s2
     	xor  $s1 $s1 $s2
        or   $s2 $s1 $s2 
lbl2:	slt  $a0 $s2 $s1
	beq  $a0 $0  lbl3
	slti $v0 $s2 0x1
lbl3:	addi $v0 $v0 0x1F
        addi $a0 $0 7
	sll  $v0 $v0 $a0
	addi $v0 $v0 1
        mult $v0 $v0
    	mfhi $s1 
	mflo $s0
	addi $sp $0 0x8
	sh   $s0 0($sp)
	lh   $sp 0($sp)
	j    $ra lbl4
lbl4:	beq  $s0 $0 END
	sll  $s0 $0 $0
	srl  $s0 $0 $0
	jr $0  $ra -1
END:   	addi $s0 $0 1
         

