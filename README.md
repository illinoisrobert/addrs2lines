# addrs2lines

`addrs2lines` is a utility command-line program
in support of the [memorizer project][2]
at [Information Trust Institute][3] at University of Illinois.


## Usage

Assuming you have finished a memorizer run and have collected:
* vmlinux
* /proc/modules
* `cp $(find /lib/modules/${uname -r} -name '*.ko' -print) .`
* `kmap`, `allocs`, `accesses`, any or all of them.

Then a typical usage might look like this:

    addrs2lines -e vmlinux -m modules -d . < kmap > kmap.out

## License

This project is licensed under the [MIT license][4]
See [LICENSE][5] for details.

## Use of AI

Portions of this code were inspired by, adapted from,
or copied from [Github Copilot][1] suggestions.

## TODO

Faster. Maybe by making multiple copies of addr2line run in parallel.

Add tests. Currently kernel addresses are ad-hoc tested, but module addresses are untested.

## Authors

Rob Adams (<robadams@illinois.edu>)

Copyright 2023 Board of Trustees of the University of Illinois

[1]: https://docs.github.com/en/copilot/using-github-copilot/getting-started-with-github-copilot?tool=vscode
[2]: https://files.iti.illinois.edu/ring0/memorizer
[3]: https://iti.illinois.edu
[4]: https://opensource.org/license/mit/
[5]: LICENSE
