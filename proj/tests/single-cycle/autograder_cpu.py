#!/usr/bin/env python

import autograder_base
import os.path

from autograder_base import file_locations, AbsoluteTestCase, FractionalTestCase, main

tests = [
  ("CPU sll test",FractionalTestCase(os.path.join(file_locations,'CPU-sll.circ'),os.path.join(file_locations,'reference-output/CPU-sll.out'),1)),
  ("CPU add/lui test",FractionalTestCase(os.path.join(file_locations,'CPU-add_lui.circ'),os.path.join(file_locations,'reference-output/CPU-add_lui.out'),1)),
  ("CPU branches test",FractionalTestCase(os.path.join(file_locations,'CPU-branches.circ'),os.path.join(file_locations,'reference-output/CPU-branches.out'),1)),
  ("CPU jump test",FractionalTestCase(os.path.join(file_locations,'CPU-jump.circ'),os.path.join(file_locations,'reference-output/CPU-jump.out'),1)),
  ("CPU mem test",FractionalTestCase(os.path.join(file_locations,'CPU-mem.circ'),os.path.join(file_locations,'reference-output/CPU-mem.out'),1)),
  ("CPU use all test",FractionalTestCase(os.path.join(file_locations,'CPU-use_all.circ'),os.path.join(file_locations,'reference-output/CPU-use_all.out'),1))
]

if __name__ == '__main__':
  main(tests)
