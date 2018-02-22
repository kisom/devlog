Prototyping databases in Prolog
###############################

:date: 2018-01-18 23:00
:tags: prolog, book, draft

This is chapter 1 of *The Practice of Prolog*.

In order to build useful databases, we need a layer of abstraction. The
*entity-relationship* (ER) approach is one successful technique for
abstracting models. In this approach, a set of entities is defined along with
the relationships between those entities. This systematic approach to defining
the relevant aspects of the world is needed to build a useful data model.

Prolog is a useful tool for prototyping databases

  Prolog is a useful database implementation language, but such an
  implementation should only be undertaken after the database is properly
  designed.

Some data:

+------+-------------------------+--------+
|  id  | title                   | format |
+======+=========================+========+
| 3264 | Raiders of the Lost Ark | DVD    |
+------+-------------------------+--------+
