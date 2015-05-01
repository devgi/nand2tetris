import sys
from hack_assembler.assembler import compile_file, write_output_to_file

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: %s <asm.file>" % sys.argv[0]
        sys.exit(1)

    path = sys.argv[-1]
    write_output_to_file(path, compile_file(path))