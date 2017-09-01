Title: Building multiple Rust programs
Date: 2017-09-01 12:01
Tags: rust, build

One thing that I commonly do in Go is to structure a project such that
it encapsulates several command line programs (servers, clients,
utilites, whatever) that are front-ends for a set of libraries in the
repository. For example, my [goutils](https://github.com/kisom/goutils/)
repository is structured roughly as follows:

```
~/src/github.com/kisom/goutils
[2017-09-01T10:44:42 PDT] (0) <straka:kyle> $ tree -d
.
├── assert
│   └── assert.go
├── cmd
│   ├── atping
│   │   ├── main.go
│   │   └── README
│   ├── certchain
│   │   ├── certchain.go
│   │   └── README
│   ├── certdump
│   │   ├── certdump.go
│   │   ├── README
│   │   └── util.go
│   │...
├── dataspec
│   ├── dataspec.go
├── die
│   ├── die.go
│   └── README.md
├── doc.go
├── fileutil
│   └── fileutil.go
├── lib
│   ├── defs.go
│   ├── ftime_bsd.go
│   ├── ftime_unix.go
│   └── lib.go
|...

33 directories, 73 files
```

The `cmd` directory houses a number of small purpose-built programs
that do a specific thing, typically encapsulating specific
functionality from one of the libraries or having a common library to
share between the programs. With the default Go workflow, if I run `go
build` over this repo (e.g. via `go build ./...`), all the source
files inside the directory are build, and for command line programs,
the parent directory's base name is taken as the name for the
resulting executable.

I was trying to figure out how to do this in Rust; here's what I've
figured out.

1. You can have a `src/bin` directory; everything is build as the name
   of its `.rs` file. For example, I would have
   `src/bin/{atping,certchain,certdump}` from the above listing.
2. You can specify libraries in the `Cargo.toml` manifest.

Here's an example of a tree now:

```
~/code/rust/rust-tools
[2017-09-01T11:38:27 PDT] (0) <straka:kyle> $ tree
.
├── Cargo.lock
├── Cargo.toml
└── src
    ├── bin
    │   ├── cbacklight.rs
    │   └── netcheck.rs
    ├── lib.rs
    └── version
        └── mod.rs

3 directories, 6 files
```

I'm not sure this is the right choice. I think you can specify a
number of libraries, and maybe that's better. To use the libraries,
I added the following to the top of `src/bin/*.rs`:

```
// this is the name of the project from the Cargo manifest.
extern create rust_tools;

use rust_tools::*;
```

I had to change the name of the project from "rust-tools" to
"rust_tools" because Cargo can't import the former.

I think this effectively does what I wanted it to do.
