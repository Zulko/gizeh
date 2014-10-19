"""
Run this Python script to generate all the PNGs from the examples in this folder.
"""


import os
examples = [f for f in os.listdir('.') if f.endswith(".py")
                                       and not f.startswith('_')]
for f in examples:
    execfile(f)