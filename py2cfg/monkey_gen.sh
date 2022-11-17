#!/bin/bash

for file in examples/*.py; do
    monkeytype run py2cfg/_runner.py "$file"
done
monkeytype apply py2cfg.model
monkeytype apply py2cfg.builder
