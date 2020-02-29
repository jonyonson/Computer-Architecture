#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

def main(argv):

    cpu = CPU()

    cpu.load(argv[1])
    cpu.run()

    return 0


main(sys.argv)

