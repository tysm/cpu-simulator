# AC_2017.1
## Requiriments
- Java
- Python2.7
## PROJ
```
http://www-inst.eecs.berkeley.edu/~cs61c/sp17/projs/03_1/
http://www-inst.eecs.berkeley.edu/~cs61c/sp17/projs/03_2/
```
## Running Tests
### ALU and RegFile tests:
Go to 'AC_2017.1/proj/tests/tests-3-1/' and run on terminal:
```
python run-all-tests.py
python sanity_test.py
python sanity_test_personal.py
```
### CPU test:
Go to 'AC_2017.1/proj/' and run on terminal:
- Single_cycle:
```
cp back_up_single_cycle/cpu.circ cpu.circ
make cpu-single-cycle
```
- Pipelined:
```
cp back_up_pipelined/cpu.circ cpu.circ
make cpu-pipelined
```
## Checking the project
Go to 'AC_2017.1/resources/' and run on terminal:
```
java -jar Logisim-Evolution.jar
```
And open the files in their respective folders:
```
AC_2017.1/proj/alu.circ
AC_2017.1/proj/regfile.circ
AC_2017.1/proj/cpu.circ
```
### Developed by
Thalles Medrado

Vinicius Brito
