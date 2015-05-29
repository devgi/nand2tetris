import os

class VMBytecodeWriter(object):

    def __init__(self):
        self._bytecode = []

    def _write(self, *lines):
        self._bytecode.extend(lines)

    def save(self):
        return os.linesep.join(self._bytecode)

    def write_function_declaration(self, name, num_of_local_vars):
        self._write('function {name} {num}'.format(name=name, num=num_of_local_vars))

    def write_method_call(self, function_name, num_of_args):
        self._write('call {name} {num}'.format(name=function_name, num=num_of_args))

    def write_push(self, segment, index):
        self._write('push {segment} {index}'.format(segment=segment,index=index))

    def write_pop(self, segment, index):
        self._write('pop {segment} {index}'.format(segment=segment,index=index))

    def write_return(self):
        self._write('return')

    def write_binary_operation(self, symbol):
        symbol_to_command = {
            '+': 'add',
            '*': 'call Math.multiply 2',
            '-': 'sub',
            '/': 'call Math.divide 2',
            '&': 'and',
            '<': 'lt',
            '>': 'gt',
            '=': 'eq',
            '|': 'or',
        }
        self._write(symbol_to_command[symbol])

    def write_unary_operation(self, symbol):
        symbol_to_command = {
            '-': 'neg',
            '~': 'not'
        }
        self._write(symbol_to_command[symbol])

