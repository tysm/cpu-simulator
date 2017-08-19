
cpu-single-cycle:
	cp alu.circ tests/single-cycle
	cp regfile.circ tests/single-cycle
	cp mem.circ tests/single-cycle
	cp cpu.circ tests/single-cycle
	cd tests/single-cycle && python2.7 autograder_cpu.py -here
	mv tests/single-cycle/TEST_LOG TEST_LOG_SINGLE_CYCLE

cpu-pipelined:
	cp alu.circ tests/pipelined
	cp regfile.circ tests/pipelined
	cp mem.circ tests/pipelined
	cp cpu.circ tests/pipelined
	cd tests/pipelined && python2.7 autograder_cpu.py -here
	mv tests/pipelined/TEST_LOG TEST_LOG_PIPELINED