Write You a Forth, 0x04
-----------------------

:date: 2018-02-23 19:20
:tags: wyaf, forth

So, I lied about words being next. When I thought about it some more, what I
really need to do is start adding the stack in and adding support for parsing
numerics. I'll start with the stack, because it's pretty straightforward.

I've added a new definition: ``constexpr uint8_t STACK_SIZE = 128``. This goes
in the ``linux/defs.h``, and the ``#else`` in the top ``defs.h`` will set a
smaller stack size for other targets. I've also defined a type called ``KF_INT``
that, on Linux, is a ``uint32_t``::

        index 4dcc540..e070d27 100644
        --- a/defs.h
        +++ b/defs.h
        @@ -3,6 +3,9 @@
        
        #ifdef __linux__
        #include "linux/defs.h"
        +#else
        +typedef int KF_INT;
        +constexpr uint8_t STACK_SIZE = 16;
        #endif
        
        constexpr size_t       MAX_TOKEN_LENGTH = 16;
        diff --git a/linux/defs.h b/linux/defs.h
        index 57cdaeb..3740f5a 100644
        --- a/linux/defs.h
        +++ b/linux/defs.h
        @@ -4,4 +4,7 @@
        #include <stddef.h>
        #include <stdint.h>
        
        +typedef int32_t KF_INT;
        +constexpr uint8_t      STACK_SIZE = 128;
        +
        #endif
        \ No newline at end of file

It seems useful to be able to adapt the kind of numbers supported; an AVR might do
better with 16-bit integers, for example.

``stack.h``
^^^^^^^^^^^

The stack is going to be templated, because we'll need a ``double`` stack later
for floating point and a return address stack later. This means everything will
go under ``stack.h``. This is a pretty simple implementation that's CS 101 material;
I've opted to have the interface return ``bool``\ s for everything to indicate stack
overflow and underflow and out of bounds::

        #ifndef __KF_STACK_H__
        #define __KF_STACK_H__

        #include "defs.h"

        template <typename T>
        class Stack {
        public:
                bool   push(T val);
                bool   pop(T &val);
                bool   get(size_t, T &);
                size_t size(void) { return this->arrlen; };
        private:
                T arr[STACK_SIZE];
                size_t arrlen;
        };

        // push returns false if there was a stack overflow.
        template <typename T>
        bool
        Stack<T>::push(T val)
        {
                if ((this->arrlen + 1) > STACK_SIZE) {
                        return false;
                }

                this->arr[this->arrlen++] = val;
                return true;
        }

        // pop returns false if there was a stack underflow.
        template <typename T>
        bool
        Stack<T>::pop(T &val)
        {
                if (this->arrlen == 0) {
                        return false;
                }

                val = this->arr[this->arrlen - 1];
                this->arrlen--;
        }

        // get returns false on invalid bounds.
        template <typename T>
        bool
        Stack<T>::get(size_t i, T &val)
        {
                if (i > this->arrlen) {
                        return false;
                }

                val = this->arr[i];
                return true;
        }

        #endif // __KF_STACK_H__

I'll put a ``Stack<KF_INT>`` in ``kforth.cc`` later on. For now, this gives me
an interface for the numeric parser to push a number onto the stack.

``parse_num``
^^^^^^^^^^^^^

It seems like the best place for this is in ``parser.cc`` --- though I might
move into a token processor later. The definition for this goes in ``parser.h``,
and the body is in ``parser.cc``::

        // parse_num tries to parse the token as a signed base 10 number,
        // pushing it onto the stack if needed.
        bool
        parse_num(struct Token *token, Stack<KF_INT> &s)
        {
                KF_INT	n = 0;
                uint8_t i = 0;
                bool    sign = false;

It turns out you can't parse a zero-length token as a number...
::

                if (token->length == 0) {
                        return false;
                }

I'll need to invert the number later if it's negative, but it's worth checking
the first character to see if it's negative.
::

                if (token->token[i] == '-') {
                        i++;
                        sign = true;
                }

Parsing is done by checking whether each character is within the range of the ASCII
numeral values. Later on, I might add in separate functions for processing base 10
and base 16 numbers, and decide which to use based on a prefix (like ``0x``). If the
character is between those values, then the working number is multiplied by 10 and
the digit added.
::

                while (i < token->length) {
                        if (token->token[i] < '0') {
                                return false;
                        }

                        if (token->token[i] > '9') {
                                return false;
                        }

                        n *= 10;
                        n += (uint8_t)(token->token[i] - '0');
                        i++;
                }

If it was a negative number, then the working number has to be inverted::

                if (sign) {
                        n *= -1;
                }

Finally, return the result of pushing the number on the stack. One thing that
might come back to get me later is that this makes it impossible to tell if a
failure to parse the number is due to an invalid number or due to a stack
overflow. This will be a good candidate for revisiting later.
::

                return s.push(n);
        }

``io.cc``
^^^^^^^^^^

Conversely, it'll be useful to write a number to an ``IO`` interface. It
*seems* more useful right now to just provide a number → I/O function, but
that'll be easily adapted to a number → buffer function later. This will add
a real function to ``io.h``, which will require a corresponding ``io.cc``
(which also needs to be added to the ``Makefile``)::

        #include "defs.h"
        #include "io.h"

        #include <string.h>

        void
        write_num(IO &interface, KF_INT n)
        {

Through careful scientific study, I have determined that most number of digits
that a 32-bit integer needs is 10 bytes (sans the sign!). This will absolutely
need to be changed if ``KF_INT`` is ever moved to 64-bit (or larger!) numbers.
There's a TODO in the actual source code that notes this. ::

                char buf[10];
                uint8_t i = 10;
                memset(buf, 0, 10);

Because this is going out to an I/O interface, I don't need to store the sign
in the buffer itself and can just print it and invert the number. Inverting is
important; I ran into a bug earlier where I didn't invert it and my subtractions
below were correspondingly off.
::

                if (n < 0) {
                        interface.wrch('-');
                        n *= -1;
                }

The buffer has to be filled from the end to the beginning to do the inverse of
the parsing method::

                while (n != 0) {
                        char ch = (n % 10) + '0';
                        buf[i--] = ch;
                        n /= 10;
                }

But then it can be just dumped to the interface::

                interface.wrbuf(buf+i, 11-i);
        }

``kforth.cc``
^^^^^^^^^^^^^^

And now I come to the fun part: adding the stack in. After including ``stack.h``,
I've added a stack implementation to the top of the file::

        // dstack is the data stack.
        static Stack<KF_INT>	dstack;

It's kind of useful to be able to print the stack::

        static void
        write_dstack(IO &interface)
        {
                KF_INT	tmp;
                interface.wrch('<');
                for (size_t i = 0; i < dstack.size(); i++) {
                        if (i > 0) {
                                interface.wrch(' ');
                        }

                        dstack.get(i, tmp);
                        write_num(interface, tmp);
                }
                interface.wrch('>');
        }

Surrounding the stack in angle brackets is a cool stylish sort of thing, I
guess. All this is no good if the interpreter isn't actually hooked up to the
number parser::

        // The new while loop in the parser function in kforth.cc:
        while ((result = parse_next(buf, buflen, &offset, &token)) == PARSE_OK) {
                interface.wrbuf((char *)"token: ", 7);
                interface.wrbuf(token.token, token.length);
                interface.wrln((char *)".", 1);

                if (!parse_num(&token, dstack)) {
                        interface.wrln((char *)"failed to parse numeric", 23);
                }

                // Temporary hack until the interpreter is working further.
                if (match_token(token.token, token.length, bye, 3)) {
                        interface.wrln((char *)"Goodbye!", 8);
                        exit(0);
                }
        }

But does it blend?
^^^^^^^^^^^^^^^^^^

Hopefully this works::

        ~/code/kforth (0) $ make
        g++ -std=c++14 -Wall -Werror -g -O0   -c -o linux/io.o linux/io.cc
        g++ -std=c++14 -Wall -Werror -g -O0   -c -o io.o io.cc
        g++ -std=c++14 -Wall -Werror -g -O0   -c -o parser.o parser.cc
        g++ -std=c++14 -Wall -Werror -g -O0   -c -o kforth.o kforth.cc
        g++  -o kforth linux/io.o io.o parser.o kforth.o
        ~/code/kforth (0) $ ./kforth
        kforth interpreter
        <>
        ? 2 -2 30 1000 -1010
        token: 2.
        token: -2.
        token: 30.
        token: 1000.
        token: -1010.
        ok.
        <2 -2 30 1000 -1010>
        ? bye
        token: bye.
        failed to parse numeric
        Goodbye!
        ~/code/kforth (0) $

So there's that. Okay, next time *for real* I'll do a vocabulary thing.

As before, see the tag `part-0x04 <https://github.com/kisom/kforth/tree/part-0x04>`_.

Part B
^^^^^^^

So I was feeling good about the work above until I tried to run this on my
Pixelbook::

	$ ./kforth
	kforth interpreter
	<>
	? 2
	token: 2.
	ok.
	<5>
	
WTF‽ I spent an hour debugging this to realise it was a bounds overflow in
``write_num``. This led me to ckecking the behaviour of the maximum and
minimum values of ``KF_INT`` which led to me revising ``io.cc``::

	#include "defs.h"
	#include "io.h"
	
	#include <string.h>
	
	static constexpr size_t	nbuflen = 11;
	
	void
	write_num(IO &interface, KF_INT n)
	{
	
		// TODO(kyle): make the size of the buffer depend on the size of
		// KF_INT.
		char buf[nbuflen];
		uint8_t i = nbuflen;
		memset(buf, 0, i);
		bool neg == n < 0;
	
		if (neg) {
			interface.wrch('-');
			n = ~n;
		}
	
		while (n != 0) {
			char ch = (n % 10) + '0';
			if (neg && (i == nbuflen)) ch++;
			
This was the source of the actual bug: ``buf[i]`` where ``i`` == ``nbuflen``
was stomping over the value of ``n``, which is stored on the stack, too.
::

			buf[i-1] = ch;
			i--;
			n /= 10;
		}
	
		uint8_t buflen = nbuflen - i % nbuflen;
		interface.wrbuf(buf+i, buflen);
	}

A couple of things here: first, the magic numbers were driving me crazy. It
didn't fix the problem, but I changed all but one of the uses of them at one
point and forgot one. So, now I'm doing the right thing (or the more right
thing) and using a ``constexpr``. Another thing is changing from ``n *= -1``
to ``n = ~n``. This requires the check for ``neg && (i == nbuflen)`` to add
one to get it right, but it handles the case where *n* = -2147483648::

	(gdb) p -2147483648 * -1
	$1 = 2147483648
	(gdb) p ~(-2147483648)
	$2 = 2147483647
	
Notice that *$1* will overflow a ``uint32_t``, which means it will wrap back
around to -2147483648, which means negating it this way has no effect. *~n + 1*
is a two's complement.

Finally, I made sure to wrap the buffer length so that we never try to write a
longer buffer than the one we have.

I feel dumb for making such a rookie mistake, but I suppose that's what
happens when you stop programming for a living. The updated code is under the
tag `part-0x04-update <https://github.com/kisom/kforth/tree/part-0x04-update>`_.