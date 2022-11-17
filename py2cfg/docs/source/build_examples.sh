#!/bin/bash
EXAMPLES=../../examples

echo building examples
py2cfg $EXAMPLES/fib.py
py2cfg $EXAMPLES/speed_sort.py