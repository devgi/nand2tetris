import collections

from jack_compiler.consts import FIELD, STATIC, FUNCTION, METHOD

Symbol = collections.namedtuple("Symbol", ["identifier", "index", "type", "kind"])

class ScopeSymbolTable(object):

    def __init__(self, scope_name, allowed_kinds):
        self.scope_name = scope_name
        self._allowed_kinds = allowed_kinds
        self._table = dict()
        self._kind_counters = dict((kind, 0) for kind in allowed_kinds)

    def define_symbol(self, identifier, kind, type):
        assert kind in self._allowed_kinds
        assert identifier not in self._table

        index = self._kind_counters[kind]
        self._kind_counters[kind] += 1

        symbol = Symbol(identifier=identifier,
                        index=index,
                        type=type,
                        kind=kind)
        self._table[identifier] = symbol

    def get(self, identifier):
        return self._table.get(identifier, None)


class SubroutineSymbolTable(ScopeSymbolTable):
    VAR="VAR"
    ARGUMENT="ARG"

    def __init__(self, subroutine_name):
        allowed_kinds = [self.VAR, self.ARGUMENT]
        super(SubroutineSymbolTable, self).__init__(subroutine_name,
                                                    allowed_kinds=allowed_kinds)

class ClassSymbolTable(ScopeSymbolTable):

    def __init__(self, class_name):
        allowed_kinds = [FIELD, STATIC]
        super(ClassSymbolTable, self).__init__(class_name,
                                               allowed_kinds=allowed_kinds)


class SymbolTable(object):

    def __init__(self):
        self._class_scopes = dict()
        self._current_class_scope = None
        self._current_subroutine_scope = None
        self.subroutine_type = None

    def start_class(self, class_name):
        """
        Declare the beginning of class scope.
        :param class_name: The name of the class.
        :return: mangled name of the class scope.
        """
        assert class_name not in self._class_scopes

        class_scope = ClassSymbolTable(class_name)
        self._class_scopes[class_name] = class_scope
        self._current_class_scope = class_scope
        self.subroutine_type = None
        self._current_subroutine_scope = None
        return class_name

    def start_subroutine(self, subroutine_name, subroutine_type):
        """
        Declare the beginning of subroutine scope.
        :param subroutine_name: The name of the subroutine.
        :return: mangled name of the subroutine scope.
        """
        # TODO: may asset when duplicate subroutines declared?
        subroutine_scope = SubroutineSymbolTable(subroutine_name)
        self._current_subroutine_scope = subroutine_scope
        self.subroutine_type = subroutine_type
        return self.create_mangled_name(subroutine_name)

    def create_mangled_name(self, subroutine_name, class_name=None):
        if not class_name:
            class_name = self._current_class_scope.scope_name
        return "{class_name}.{subroutine_name}".format(
                class_name=class_name,
                subroutine_name=subroutine_name)


    def get(self, identifier):
        assert self._current_class_scope , "Can't query without class scope."
        symbol = None
        if self._current_subroutine_scope and self._current_subroutine_scope.get(identifier):
            symbol = self._current_subroutine_scope.get(identifier)

        if not symbol and self._current_class_scope.get(identifier):
            symbol = self._current_class_scope.get(identifier)

        if symbol and self.subroutine_type == METHOD and symbol.kind == SubroutineSymbolTable.ARGUMENT:
            # when we are inside a method the first arg is "this"
            symbol = symbol._replace(index=symbol.index + 1)

        if symbol and self.subroutine_type == FUNCTION:
            assert symbol.kind != FIELD

        return symbol

    def define_symbol(self, identifier, kind, type):
        if self._current_subroutine_scope:
            self._current_subroutine_scope.define_symbol(identifier, kind, type)
        elif self._current_class_scope:
            self._current_class_scope.define_symbol(identifier, kind, type)
        else:
            raise RuntimeError("Can't find scope! %s" % identifier)


