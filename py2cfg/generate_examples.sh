#!/bin/bash

cd examples
rm -f ./*.svg
rm -f ./*.png
rm -f ./*.pdf

for file in *.py; do
    echo "Running: python3 ../py2cfg/_runner.py $file"
    python3 ../py2cfg/_runner.py --short "$file"
    # pycallgraph graphviz "$file"
    # mv pycallgraph.png "$file"_pycallgraph.png
    # pyreverse -o svg "$file"
    # mv classes.svg "$file"_pyreverse.svg
done
