import re
import os
import sys
from typing import TextIO

FN = re.compile(r"^( ){0,24}fn ")
MOD = re.compile(r"^( ){0,24}mod ")
ENUM = re.compile(r"^( ){0,24}enum ")
STRUCT = re.compile(r"^( ){0,24}struct .*\{$")

def run(dirname: str) -> ():
    """main loop. Walks directory and creates file readers/writers"""
    top, base = os.path.split(dirname)
    if base == '':
        base = top
    for root, _, files in os.walk(dirname):
        newdir = root.replace(base,f"pub{base}") # we might have nested folders
        os.makedirs(newdir)
        srcfiles = [f for f in files if f.endswith(".rs")]
        for src in srcfiles:
            if prep(os.path.join(root,src)) is not 0:
                pass # source is probably invalid. Just skip
            newfile = open(os.path.join(newdir,src),"w")
            oldfile = open(os.path.join(root,src),"r")
            try:
                scan(oldfile, newfile)
            except Exception as e:
                print(f"failed to rewrite {src} with error:\n{e}")
            finally:
                newfile.close()
                oldfile.close()


def prep(filepath: str) -> int:
    """
    Runs rustfmt on files before processing. Given that Rust formatting is not
    semantically meaningful, authors can do cute things like write everything on
    a single line. This is a remote possibility, but prep ensures that the
    scanner will encounter sane newlines and white space.

    Signals failure with non-zero result
    """
    return os.system(f"rustfmt {filepath}")

def scan(rdr: TextIO, w: TextIO) -> str:
    """
    Iterate over lines in a file and return a line to be written which may be
    modified
    """
    for line in rdr:
        new_line = line
        if FN.match(new_line):
            new_line = new_line.replace("fn", "pub fn", 1)
        if MOD.match(new_line):
            new_line = new_line.replace("mod", "pub mod", 1)
        if ENUM.match(new_line):
            new_line = new_line.replace("enum", "pub enum", 1)
        if STRUCT.match(new_line):
            new_line = new_line.replace("struct", "pub struct", 1)
            new_line += struct_handler(rdr)
        w.write(new_line)
        

def struct_handler(rdr: TextIO) -> str:
    """advance reader to the end of the struct and make fields public"""
    # What is the indent level?
    line = rdr.readline()
    spaces = 0
    for c in line:
        if c != ' ':
            break
        spaces += 1
    if spaces < 4: # this would be a false positive exit early
        return line
    # define an exit condition
    end = re.compile(f"^( ){ {spaces - 4} }}}$")
    # define a regex for fields
    priv_field = re.compile(f"^( ){ {spaces} }(?!pub )(\w+)\:")
    result = ""
    while not end.match(line):
        field_match = priv_field.match(line)
        if field_match:
            line = line[:spaces]+"pub "+line[spaces:]
        result += line
        line = rdr.readline()
    result += line # catch the terminal brace
    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("""Usage: liberate.py SOURCEFOLDER
        
Liberate will scan all '.rs' files within a folder and create a modified source
folder where all modules, functions and struct fields have been declared public.

example:

    liberate.py /home/user/rustprojects/mycrate/src

would yield:

    /home/user/rustprojects/mycrate/pubsrc

Sometimes library authors' ideas of what elements of the library API you should
not be allowed to use are incompatible with your objectives. This script is for
those situations.
""")
    run(sys.argv[1])