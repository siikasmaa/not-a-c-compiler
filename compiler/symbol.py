class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


INT_SIZE = 4


class Symbol(object):
    def __init__(self, name, **kwargs):
        self.name = name
        self.type = kwargs.get('type', None)
        self.scope_level = kwargs.get('scope_level', None)
        self.size = kwargs.get('size', INT_SIZE)
        self.address = kwargs.get('address', None)
        self.arguments = kwargs.get('arguments', None)

    def __str__(self):
        return "Symbol: {s.name}\n\taddress: {s.address}\n\ttype: {s.type}\n\tscope: {s.scope_level}\n".format(s=self)

    __repr__ = __str__

    def get_address(self):
        return self.address

    def set_address(self, address):
        self.address = address

    def get_scope_level(self):
        return self.scope_level

    def set_scope_level(self, level):
        self.scope_level = level

    def get_size(self):
        return self.size

    def set_size(self, size):
        self.size = size

    def get_arguments(self):
        return self.arguments

    def set_arguments(self, arguments):
        self.arguments = arguments

    def get_type(self):
        return self.type

    def set_type(self, symbol_type):
        self.type = symbol_type


class SymbolTable(object, metaclass=Singleton):
    def __init__(self, base_addr=500, temp_address_base=1000):
        self._symbols = {}
        self._var_count = 0
        self._scope_stack = []
        self._base_addr = base_addr
        self._temp_base_addr = temp_address_base
        self._temp_var_count = 0

    def __str__(self):
        header = 'Symbol table contents'
        lines = ['\n', header, '_' * len(header)]
        lines.extend(
            ('%r' % value)
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        return '\n'.join(lines)

    __repr__ = __str__

    clear = __init__

    def insert(self, new_symbol):
        symbol = new_symbol
        lookup_symbol = self.lookup(new_symbol.name)
        if lookup_symbol is not None:
            symbol = lookup_symbol
        if symbol.address == None:
            symbol.set_address(self.get_address(symbol.size))
        self._symbols[symbol.name] = symbol

    def lookup(self, name):
        return self._symbols.get(name, None)

    def lookup_with_address(self, address):
        for (x, y) in self._symbols.items():
            if y.get_address() == address:
              return y

    def get_address(self, size):
        address = self._base_addr + self._var_count * size
        self._var_count += 1
        return address

    def get_temporary_address(self, size=1):
        address = self._temp_base_addr + self._temp_var_count * INT_SIZE
        self._temp_var_count += 1
        return address

    def find_address(self, input):
        symbol = self.lookup(input)
        return symbol.get_address()
