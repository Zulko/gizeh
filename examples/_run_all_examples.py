"""
Run this Python script to generate all the PNGs from the examples in this folder.
"""


import os


def execfile(filename):
    exec(compile(open(filename, "rb").read(), filename, 'exec'))

examples = [f for f in os.listdir('.') if f.endswith(".py") and
                                       not f.startswith('_')]

for f in examples:
    print ("running: "+f)
    exec("import "+f[:-3])