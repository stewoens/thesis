#! /bin/bash
(cd docs && make html) # build the docs
HTML_DIRECTORY="docs/build/html"
python3 -m http.server --directory $HTML_DIRECTORY