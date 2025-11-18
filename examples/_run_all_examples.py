"""
Run this Python script to generate all the PNGs from the examples in this folder.
"""

import os


def execfile(filename):
    with open(filename, "rb") as f:
        exec(compile(f.read(), filename, "exec"))


examples = [f for f in os.listdir(".") if f.endswith(".py") and not f.startswith("_")]

for f in examples:
    print("running: " + f)
    execfile(f)
