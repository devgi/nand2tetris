import collections

from jack_syntax_analyzer.consts import FIELD, STATIC

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
        self._current_subroutine_scope = None
        return class_name

    def start_subroutine(self, subroutine_name):
        """
        Declare the beginning of subroutine scope.
        :param subroutine_name: The name of the subroutine.
        :return: mangled name of the subroutine scope.
        """
        # TODO: may asset when duplicate subroutines declared?
        subroutine_scope = SubroutineSymbolTable(subroutine_name)
        self._current_subroutine_scope = subroutine_scope

        return "{class_name}.{subroutine_name}".format(
                class_name=self._current_class_scope.scope_name,
                subroutine_name=subroutine_name)

    def get(self, identifier):
        assert self._current_class_scope , "Can't query without class scope."
        result = None
        if self._current_subroutine_scope and self._current_subroutine_scope.get(identifier):
            return self._current_subroutine_scope.get(identifier)

        if self._current_class_scope.get(identifier):
           return self._current_class_scope.get(identifier)

        raise RuntimeError("Couldn't resolve identifier %s" % identifier)

    def define_symbol(self, identifier, kind, type):
        if self._current_subroutine_scope:
            self._current_subroutine_scope.define_symbol(identifier, kind, type)
        elif self._current_class_scope:
            self._current_class_scope.define_symbol(identifier, kind, type)
        else:
            raise RuntimeError("Can't find scope! %s" % identifier)


