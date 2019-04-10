Title: Hack Week Day 1
Date: 2019-04-09 10:12
Tags: hackweek

It's hack week at Dropbox, and I'm working on two projects:

1. GraphBook is a graph-based programmer's notebook.
2. A LoRa pager / SMS system using Adafruit feathers as a modem of sorts.

I've scheduled the LoRa modem work to start on Wednesday; Monday and
Tuesday are entirely dedicated to GraphBook.

I chose to write it in Python because it felt like it would be faster
to prototype (Go is notoriously annoying to do exploratory programming in),
with Python 3's type annotation support (and MyPy) to quickly build this
out.

Right now, this is a directory of yaml files. It's kind of disappointing
to have to use yaml, but it's the most human readable/editable format I
could think of that supports having metadata and whatnot in the file.
Making it human readable and writable lets me punt on the editor part
of this right now; it's possible in the future that I'll want to change
this up again (I kind of like the idea of just pickling everything into
one file, but I also understand how that's not great), like maybe using
the file as the contents but using SQLite for metadata. But then, how
do I distinguish the separate cells? No, it's intellectually lazy for
the purposes of hack week, so I'm punting on the representation problem
for now.

I also hacked together a micro Scheme cell last night; it's based on
the first version of Peter Norvig's Python Lisp implementation - super
fun to follow along with. For code execution VMs, I want each run to
execute in a clean env. I think I could extend the updated version of
his Scheme, but this worked for a first pass. Again, I'm punting on the
hard parts to put the framework in place to build this out.

As it stands now, I have a working `Notebook` class and about 80% coverage
across the board. I'm sure there's weird edge cases. I really just wanted
to quickly verify that basic mechanisms work.

Day 1's goal was persistence, and that I have.
