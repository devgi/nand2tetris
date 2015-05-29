import os

class VMBytecodeWriter(object):

    def __init__(self):
        self._bytecode = []

    def _write(self, *lines):
        self._bytecode.extend(lines)

    def save(self):
        return os.linesep.join(self._bytecode)