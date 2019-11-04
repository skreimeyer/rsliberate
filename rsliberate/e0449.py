import re
import os
import sys
import subprocess
from typing import TextIO, List, Tuple

import pdb

def run() -> ():
    """main loop. Prints usage, drives queueing, writing and cleanup"""
    if len(sys.argv) > 1:
        show_help()
    errs = get_cargo_input()
    main_stack = make_proj_stack(errs)
    while len(main_stack) > 0:
        file_stack = make_file_stack(main_stack)
        overwrite(file_stack)

    # FIXME

def get_cargo_input() -> str:
    """runs cargo-check and reads error output into a string"""
    results = subprocess.run(["cargo", "check"], capture_output=True)
    if results.returncode == 0:
        print("Cargo check found no errors. Exiting")
        quit()
    if results.returncode != 101:
        print("Cargo check returned an unexpected error!")
        show_help()
    if b"could not find" in results.stderr:
        print("Cargo.toml not found in this directory!")
        show_help()
    return results.stderr.decode('utf-8')
    # FIXME

def make_proj_stack(err_msg: str) -> List[Tuple[str,int]]:
    """extracts file path and line number from E0449 messages into a list"""
    e0449 = re.compile(r"error(?:\[E0449\])?\: unnecessary visibility qualifier(?:\n|\r\n)\s+--> ([\w\\/\.]+)\:(\d+)")
    pstack = [(a[0],int(a[1])) for a in e0449.findall(err_msg)]
    pstack = list(set(pstack)) # This definitely feels wrong.
    pstack.sort()
    return pstack

def make_file_stack(pstack: List[Tuple[str,int]]) -> List[Tuple[str,int]]:
    """
    takes a job stack for the entire project and pops off elements into a new
    stack which represents errors  in just one file.

    Modifies input stack
    """
    fstack = []
    first = pstack.pop()
    filename = first[0]
    fstack.append(first)
    while len(pstack) > 0 and pstack[-1][0] == filename:
        fstack.append(pstack.pop())
    return fstack


def overwrite(fstack: List[Tuple[str,int]]) -> ():
    """
    opens source file, substitutes lines and writes to a tmp file. `fstack`
    will have been built from a sorted stack, so we can assume that pop will be
    performed in order.

    for error E0449, the solution is to substitute "pub " with nothing.
    """
    filename, line_num = fstack.pop()
    tmp = str() # store our new file in memory
    with open(filename, 'r') as input:
        for i,line in enumerate(input):
            if i + 1 == line_num:
                line = line.replace("pub ","",1)
                _, line_num = fstack.pop() if fstack else ('',0)
            tmp += line
    with open(filename, 'w') as newfile:
        newfile.write(tmp)


def show_help() -> ():
    print("""
Usage: python e0449.py
Or: fixE0449

This program parses the errors generated from `cargo check` and patches the
files in the current directory for E0449 `unnecessary visibility qualifier`
errors. This is fixed by a trivial file modification, so the source files will 
be overwritten with the patched files. This will only work if run from a working
 directory with a `Cargo.toml` file in it"""
    )
    quit()

if __name__ == "__main__":
    run()