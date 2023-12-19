# Copyright 2023 Board of Trustees of the University of Illinois
# SPDX-License-Identifier: MIT

"""
This module contains classes for translating addresses to function and
file names.
"""

import sys
import argparse
import re

from .translate import Translator, ModuleDict

def run_filter(kernel: str, modules: str, module_dir: str) -> None:
    """
    Read addresses in csv file format on stdin and write
    the corresponding line, with any address replaced
    by the function and file name.

    The addresses are extracted from stdin by applying a regex
    to each line. The regex matches fields from the csv file that
    are 64-bit hex numbers.

    If either `kernel` or `modules` is None, then the corresponding
    file is not used. If `module_dir` is None, then the current
    directory is used.

    If both `kernel` and `modules` are None, then no addresses
    are translated.
    """

    if modules is None:
        ko_dict = ModuleDict('/dev/null', '/tmp')
    else:
        ko_dict = ModuleDict(modules, module_dir)

    # magic number where the kernel is loaded on x86_64
    # see https://www.kernel.org/doc/html/v6.6/arch/x86/x86_64/mm.html
    if kernel is not None:
        kernel_range = range(0xffffffff80000000, 0xffffffffa0000000)
        ko_dict[kernel_range] = Translator('-C', '-e', kernel, offset=0, name=kernel)

    # Regex to match 64-bit hex numbers
    addr_re = re.compile(r'\b[0-9a-f]{16}\b')

    for line in sys.stdin:
        # Extract addresseses from line
        addrs = addr_re.findall(line)

        # Replace addresses with function and file names
        for addr in addrs:
            iaddr = int(addr, 16)

            # translate the address using the appropriate addr2line process
            # if the address is not found, then just use the address
            try:
                new_addr = f'"{ko_dict[iaddr].translate(addr)}"'
            except KeyError:
                new_addr = addr

            # replace the address in the line
            line = line.replace(addr, new_addr)

        # The line is now ready to be printed. It might
        # contain no differences, differences in a single
        # address, or differences in multiple addresses.
        sys.stdout.write(line)


def main():
    """
    Read addresses in csv file format on stdin and write
    the the corresponding line, with the address replaced
    by the function and file name.

    Usage: python3 runme.py -k kernel -m module_file
    """
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-e', '--kernel', help='kernel file', default=None)
    argparser.add_argument('-m', '--module', help='module file', default=None)
    argparser.add_argument('-d', '--module_dir', help='module directory', default='.')
    args = argparser.parse_args()

    run_filter(args.kernel, args.module, args.module_dir)

if __name__ == '__main__':
    main()
