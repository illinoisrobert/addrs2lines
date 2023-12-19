# Copyright 2023 Board of Trustees of the University of Illinois
# SPDX-License-Identifier: MIT

"""
This module contains classes for translating addresses to function and
file names.
"""

import subprocess
import re

class Translator:
    """
    A wrapper around addr2line that allows for multiple addresses to be
    resolved in a single process.
    """
    def __init__(self, *args: str, offset: int = 0, name: str = ''):
        self.process = subprocess.Popen(
            ['addr2line'] + list(args),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.offset = offset
        self.name = name
        self._cache = {}

    # @cache
    def translate(self, line: str) -> str:
        """
        Write a single address to addr2line and return the result.
        """
        # memoize the result of this function
        if line in self._cache:
            return self._cache[line]

        self.process.stdin.write(line + '\n')
        self.process.stdin.flush()
        result = self.process.stdout.readline().strip()
        if '?' in result:
            result = line
        self._cache[line] = result
        return result

class ModuleDict(dict):
    """
    A multi-key dictionary that maps addresses to addr2line connections.
    """
    def __init__(self, module_file: str, module_dir: str):
        super().__init__()
        self._cache = {}

        # Regex to match 64-bit hex numbers
        addr_re = re.compile(r'\b0x[0-9a-f]{16}\b')

        with open(module_file, encoding='utf-8') as f:
            for line in f:
                # The address field is the only field that matches the regex
                addr = int(addr_re.search(line).group(), 16)

                # we know that the first two fields are the name and size
                line = line.split()
                name = line[0]
                size = int(line[1])

                # convert module name into file name
                module_dir = module_dir or '.' # default to current directory
                name = f'{module_dir}/{name}.ko'

                # Create an addr2line process for the module
                self[range(addr, addr + size)] = Translator(
                    '-C',  # demangle C++ names
                    '-e', name, # executable file
                    offset=addr, # offset of module in memory
                    name=name)

    # @cache
    def __getitem__(self, addr: int|range) -> Translator:
        """
        Return the Addr2Line object corresponding to the address.

        Either a single address or a range of addresses can be used as
        a key.
        """
        # memoize the result of this function
        if addr in self._cache:
            return self._cache[addr]
        # first compare the type of the key to the type of the keys in the dict
        # if they are the same, then we can use the super method
        if isinstance(addr, range):
            result = super().__getitem__(addr)
            self._cache[addr] = result
            return result

        # Now search for the range that contains the address.abs
        # This is a linear search, but it should be fast enough.
        for key in self:
            if addr in key:
                result = super().__getitem__(key)
                self._cache[addr] = result
                return result

        # If we get here, then the address was not found in any of the ranges.
        raise KeyError(addr)
