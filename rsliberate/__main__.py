from . import liberate    
import sys

def main():
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
        quit()
    liberate.run(sys.argv[1])

if __name__ == "__main__":
    main()
