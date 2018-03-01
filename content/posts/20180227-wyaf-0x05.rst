Write You a Forth, 0x05
-----------------------

:date: 2018-02-27 08:06
:tags: wyaf, forth

NB: Today's update was pretty large, so I don't show all of the code; this is
what ``git`` is for.

Today I need to start actually doing things with tokens. This requires two
things:

1. Some idea of what a word is, and
2. A dictionary of words

I started taking some notes on this previously, and I think there are a few
kinds of words that are possible:

1. Numbers (e.g. defining a variable)
2. Built-in functions
3. Lambda functions (that is, user-defined functions).

Stage 1 really only needs to incorporate #2, so that's what I'll focus on for
now. However, to prepare for the future, I'm going to define a ``Word`` base
class and inherit from there. This interface is going to need to be
stack-aware, so what I've done is define a ``System`` struct in ``system.h``::

        #ifndef __KF_CORE_H__
        #define __KF_CORE_H__
        
        #include "defs.h"
        #include "stack.h"
        
        typedef struct _System {
                Stack<KF_INT>        dstack;
                IO                  *interface;
        } System;
        
        
        #endif // __KF_CORE_H__

This will let me later add in support for the return stack and other things
that might be useful. Other ideas: adding something like an ``errno``
equivalent to indicate the last error, and storing a dictionary of words. This
will need some restructuring, though. I've already moved the I/O into the
system as well. This took some finangling in ``kforth.cc``; I'm eliding the
diff here because it's so long, but it's basically a ``sed -i -e
's/interface./sys->interface.``.

The Word interface
^^^^^^^^^^^^^^^^^^

Now I can start defining a Word.h. Maybe this is a case of when you have an
object-oriented language, everything looks like a class, but I decided to
design an abstract class for a Word and implement the first concrete class,
**Builtin**. What I came up with was::

    class Word {
    public:
            virtual ~Word() {};
    
The *eval* method takes a ``System`` structure and executes some function.
::

            virtual bool  eval(System *) = 0;

The dictionary is a linked list, so next is used to traverse the list.
::

            virtual Word *next(void) = 0;

The ``match`` method is used to determine whether this is the word being
referred to.
::

            virtual bool  match(struct Token *) = 0;

Finally, ``getname`` will fill in a ``char[MAX_TOKEN_SIZE]`` buffer with the
word's name.
::

            virtual void  getname(char *, size_t *) = 0;
    };

With the interface defined, I can implement ``Builtins`` (I've elided the
common interface from the listing below to focus on the implementation)::

        class Builtin : public Word {
        public:
                ~Builtin() {};
                Builtin(const char *name, size_t namelen, Word *head, bool (*fun)(System *));
                
        private:
                char		 name[MAX_TOKEN_LENGTH];
                size_t		 namelen;
                Word		*prev;
                bool		(*fun)(System *);
        };

The ``bool`` works as a first pass, but I think I'm going to have add some
notion of system conditions later on to denote why execution failed. One thing
that both ``pforth`` and ``gforth`` do that I don't yet do is to clear the
stack when there's an execution failure. At least, they clear the stack with an
unrecognised word. The implementation is pretty trivial::

        #include "defs.h"
        #include "parser.h"
        #include "system.h"
        #include "word.h"

        #include <string.h>


        Builtin::Builtin(const char *name, size_t namelen, Word *head, bool (*target)(System *))
                : prev(head), fun(target)
        {
                memcpy(this->name, name, namelen);
                this->namelen = namelen;
        }
                
        bool
        Builtin::eval(System *sys)
        {
                return this->fun(sys);
        }

        Word *
        Builtin::next()
        {
                return this->prev;
        }
                
        bool
        Builtin::match(struct Token *token)
        {
                return match_token(this->name, this->namelen, token->token, token->length);
        }

        void
        Builtin::getname(char *buf, size_t *buflen)
        {
                memcpy(buf, this->name, this->namelen);
                *buflen = namelen;
        }

Right. Now to do something with this.

The system dictionary
^^^^^^^^^^^^^^^^^^^^^

The dictionary's interface is minimal::

        // dict.h
        #ifndef __KF_DICT_H__
        #define __KF_DICT_H__

        #include "defs.h"
        #include "parser.h"
        #include "system.h"
        #include "word.h"

        typedef enum _LOOKUP_ : uint8_t {
                LOOKUP_OK = 0,	     // Lookup executed properly.
                LOOKUP_NOTFOUND = 1, // The token isn't in the dictionary.
                LOOKUP_FAILED = 2    // The word failed to execute.
        } LOOKUP;

        void	init_dict(System *);
        LOOKUP	lookup(struct Token *, System *);

        #endif // __KF_DICT_H__

There's a modicum of differentiation between "everything worked" and "no it
didn't," and by that I mean the lookup can tell you if the word wasn't found
or if there was a problem executing it.

I added a ``struct Word *dict`` field to the ``System`` struct, since we're
operating on these anyways. I guess it's best to start with the lookup function
first so that when I started adding builtins later it'll be easy to just
recompile and use them.
::

        LOOKUP
        lookup(struct Token *token, System *sys)
        {
                Word	*cursor = sys->dict;
                KF_INT	 n;
                
I seem to recall from *Programming a Problem-Oriented Language* that Chuck
Moore advocated checking whether a token was a number before looking it up
in the dictionary, so that's the approach I'll take:: 

                if (parse_num(token, &n)) {
                        if (sys->dstack.push(n)) {
                                return LOOKUP_OK;
                        }
                        return LOOKUP_FAILED;
                }

The remainder is pretty much bog-standard linked list traversal::

                while (cursor != nullptr) {
                        if (cursor->match(token)) {
                                if (cursor->eval(sys)) {
                                        return LOOKUP_OK;
                                }
                                return LOOKUP_FAILED;
                        }
                        cursor = cursor->next();
                }
                
                return LOOKUP_NOTFOUND;
        }

This needs to get hooked up into the interpreter now; this is going to require
some reworking of the ``parser`` function::

        static bool
        parser(const char *buf, const size_t buflen)
        {
                static size_t		offset = 0;
                static struct Token	token;
                static PARSE_RESULT	result = PARSE_FAIL;
                static LOOKUP		lresult = LOOKUP_FAILED;
                static bool		stop = false;

                offset = 0;

                // reset token
                token.token = nullptr;
                token.length = 0;

                while ((result = parse_next(buf, buflen, &offset, &token)) == PARSE_OK) {
                        lresult = lookup(&token, &sys);
                        switch (lresult) {
                        case LOOKUP_OK:
                                continue;
                        case LOOKUP_NOTFOUND:
                                sys.interface->wrln((char *)"word not found", 15);
                                stop = true;
                                break;
                        case LOOKUP_FAILED:
                                sys.interface->wrln((char *)"execution failed", 17);
                                stop = true;
                                break;
                        default:
                                sys.interface->wrln((char *)"*** the world is broken ***", 27);
                                exit(1);
                        }
                        
                        if (stop) {
                                stop = false;
                                break;
                        }
                }

                switch (result) {
                case PARSE_OK:
                        return false;
                case PARSE_EOB:
                        sys.interface->wrbuf(ok, 4);
                        return true;
                case PARSE_LEN:
                        sys.interface->wrln((char *)"parse error: token too long", 27);
                        return false;
                case PARSE_FAIL:
                        sys.interface->wrln((char *)"parser failure", 14);
                        return false;
                default:
                        sys.interface->wrln((char *)"*** the world is broken ***", 27);
                        exit(1);
                }
        }


Now I feel like I'm at the part where I can start adding in functionality. The
easiest first builtin: addition. Almost impossible to screw this up, right?
::

        static bool
        add(System *sys)
        {
                KF_INT	a = 0;
                KF_INT	b = 0;
                if (!sys->dstack.pop(&a)) {
                        return false;
                }
                
                if (!sys->dstack.pop(&b)) {
                        return false;
                }
                
                b += a;
                return sys->dstack.push(b);
        }

Now this needs to go into the ``init_dict`` function::

        void
        init_dict(System *sys)
        {
                sys->dict = nullptr;
                sys->dict = new Builtin((const char *)"+", 1, sys->dict, add);
        }

And this needs to get added into the ``main`` function::

        int
        main(void)
        {
                init_dict(&sys);
        #ifdef __linux__
                Console interface;
                sys.interface = &interface;
        #endif
                sys.interface->wrbuf(banner, bannerlen);
                interpreter();
                return 0;
        }

The moment of truth
^^^^^^^^^^^^^^^^^^^

Hold on to your pants, let's see what breaks::

        $ ./kforth
        kforth interpreter
        <>
        ? 2 3 +
        ok.
        <5>

Oh hey, look, it actually works. Time to add a few more definitions for good
measure:

+ the basic arithmetic operators `-`, `*`, `/`
+ the classic `SWAP` and `ROT` words
+ `DEFINITIONS` to look at all the definitions in the language

These are all pretty simple, fortunately. A few things that tripped me up,
though:

+ The *a* and *b* names kind of threw me off because I fill *a* first. This
  means it's the last number on the stack; this didn't matter for addition,
  but in subtraction, it means I had to be careful to do ``b -= a`` rather
  than the other way around.

+ pforth and gfortran both support case insensitive matching, so I had to
  modify the token matcher::

        bool
        match_token(const char *a, const size_t alen,
                const char *b, const size_t blen)
        {
                if (alen != blen) {
                        return false;
                }

                for (size_t i = 0; i < alen; i++) {
                        if (a[i] == b[i]) {
                                continue;
                        }

                        if (!isalpha(a[i]) || !isalpha(b[i])) {
                                return false;
                        }
                        
The XOR by 0x20 is just a neat trick for inverting the case of a letter.
::

                        if ((a[i] ^ 0x20) == b[i]) {
                                continue;
                        }
                        
                        if (a[i] == (b[i] ^ 0x20)) {
                                continue;
                        }
                        
                        return false;
                }
                return true;
        }

+ I forgot to include the case for ``PARSE_OK`` in the result switch statement
  in the ``parser`` function, so I could get a line of code evaluated but then
  it'd die with "the world is broken."

+ When I tried doing some division, I ran into some weird issues::

        $ ./kforth 
        kforth interpreter
        <>
        ? 2 5040 /
        ok.
        <��>

It turns out that in ``write_num``, the case where *n = 0* results in nothing
happening, and therefore the buffer just being written. This is a dirty thing,
but I edge cased this::

        $ git diff io.cc 
        diff --git a/io.cc b/io.cc
        index 77e0e2a..a86156b 100644
        --- a/io.cc
        +++ b/io.cc
        @@ -24,6 +24,10 @@ write_num(IO *interface, KF_INT n)
                                n++;
                        }
                }
        +       else if (n == 0) {
        +               interface->wrch('0');
        +               return;
        +       }
        
                while (n != 0) {
                        char ch = (n % 10) + '0';

May the compiler have mercy on my soul and whatnot.

For you sports fans keeping track at home, here's the classic bugs I've
introduced so far:

1. bounds overrun
2. missing case in a switch statement

But now here I am with the interpreter in good shape. Now I can start
implementing the builtins in earnest!

As before, see the tag `part-0x05 <https://github.com/kisom/kforth/tree/part-0x05>`_.