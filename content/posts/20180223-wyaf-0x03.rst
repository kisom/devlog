Write You a Forth, 0x03
-----------------------

:date: 2018-02-23 09:36
:tags: wyaf, forth

Today, I'm working on parsing. I was talking to `steveo
<https://github.com/steveo>`_ yesterday, and he mentioned string interning, and
it sounded like a fun thing to do (and then I started thinking about ropes and
so on).

However, I'm not going to intern strings --- at least, not yet. I'm going to do
something way more primitive::

  bool match_token(const char *a, const size_t alen,
                   const char *b, const size_t blen)
  {
          if (alen != blen) {
                  return false;
          }

          return memcmp(a, b, alen) == 0;
  }

I'd also like to operate on a buffer without having to store a bunch of copies
of strings. Performance may not be the number one concern here, but I think
it'll be more fun to implement, and it will be a little easier. The parser
should return the next token that we can push off to the rest of the process.
It seems like we'll want a structure for that.

``parser.h``
^^^^^^^^^^^^

The parser seems like it really only needs a few things, so time to take a stab at
``parser.h``::

        #ifndef __KF_PARSER_H__
        #define __KF_PARSER_H__

        #include "defs.h"

A ``Token`` can be defined as just the pointer to the start of the token and
its length. There's a limit to the maximum size of the buffer, and it'll be
important to check the length of the token. For simplicity, I'm going to define
the maximum length of a token as 16, and I'll put this as a ``constexpr`` in the
``defs.h`` file.
::

        struct Token {
                char    *token;
                uint8_t  length;
        };

Next up is to define the function from before for matching tokens.
::

        bool    match_token(const char *, const size_t, const char *, const size_t);

The meat of the parser is `parse_next`, for which we'll also need some return codes.
::

        typedef enum _PARSE_RESULT_ : uint8_t {
                PARSE_OK = 0,  // token now has a valid token.
                PARSE_EOB = 1, // end of buffer, parsing a line should stop.
                PARSE_LEN = 2, // token is too long
                PARSE_FAIL = 3 // catch-all error
        } PARSE_RESULT;

        int     parse_next(const char *, const size_t, size_t *, struct Token *);

        #endif // __KF_PARSER_H__

``parser.cc``
^^^^^^^^^^^^^^

``parser.cc`` will open with a helper to reset tokens and the same
matching code I mentioned before::

        #include "defs.h"
        #include "parser.h"

        #include <string.h>

        static void
        reset(struct Token *t)
        {
                t->token = nullptr;
                t->length = 0;
        }

        bool
        match_token(const char *a, const size_t alen,
                const char *b, const size_t blen)
        {
                if (alen != blen) {
                        return false;
                }

                return memcmp(a, b, alen) == 0;
        }

At the start of the parser, I'm going to reset the token; if there's a failure,
there shouldn't be a valid token anyhow.
::

        PARSE_RESULT
        parse_next(const char *buf, const size_t length, size_t *offset,
                struct Token *token)
        {
                size_t	 cursor = *offset;

                // Clear the token.
                reset(token);

If the offset is already at the end of the buffer, there's no more work to do
on this buffer, so I'll cut out early ``PARSE_EOB``. If I was doing a more
careful job of programming this, I'd *generally* try to avoid multiple returns,
but in this case, having working code is more important than awesome code.
::
                
                if (cursor == length) {
                        return PARSE_EOB;
                }

I'm going to assume that tokens are separated by spaces or tabs. I wasn't going
to support tabs at first, but it's easy enough to do that I just included it.
::

                while (cursor <= length) {
                        if (buf[cursor] != ' ') {
                                if (buf[cursor] != '\t') {
                                        break;
                                }
                        }
                        cursor++;
                }

This part might seem superfluous, but it's important in case there's trailing
whitespace in the buffer. I haven't touched the token yet, so no need to reset
it.
::

                if (cursor == length) {
                        return PARSE_EOB;
                }

Now I can point the token to the buffer at the start of the next token and walk
through the buffer until the end of the buffer or the first whitespace
character::

                token->token = (char *)buf + cursor;
                while ((token->length <= MAX_TOKEN_LENGTH) && (cursor < length)) {
                        if (buf[cursor] != ' ') {
                                if (buf[cursor] != '\t') {
                                        cursor++;
                                        token->length++;
                                        continue;
                                }
                        }

This got me at first and took me a few minutes to figure out. If the cursor
isn't updated at the end, the next run of the parser is going to be stuck on
this word as the cursor doesn't point to whitespace anymore.
::

                        cursor++;
                        break;
                }

Finally, if the token length hasn't been exceeded, the offset can be updated
and the token returned::

                if (token->length > MAX_TOKEN_LENGTH) {
                        reset(token);
                        return PARSE_LEN;
                }

                *offset = cursor;
                return PARSE_OK;
        }

``kforth.cc``
^^^^^^^^^^^^^

That's all of ``parse.cc`` (at least for now), but this needs to be integrated
into the frontend. ``kforth.cc`` now starts off with::

        #include "io.h"
        #include "parser.h"

        #include <stdlib.h>

        #ifdef __linux__
        #include "linux.h"
        #endif // __linux__

        static char     ok[] = "ok.\n";
        static char     bye[] = "bye";

        static bool
        parser(IO &interface, const char *buf, const size_t buflen)
        {
                static size_t           offset = 0;
                static struct Token     token;
                static PARSE_RESULT     result = PARSE_FAIL;

                offset = 0;

                // reset token
                token.token = nullptr;
                token.length = 0;

                while ((result = parse_next(buf, buflen, &offset, &token)) == PARSE_OK) {
                        interface.wrbuf((char *)"token: ", 7);
                        interface.wrbuf(token.token, token.length);
                        interface.wrln((char *)".", 1);

There's no command parser right now, so I've added in this hack so it starts to
feel a little like a Forth.
::

                        if (match_token(token.token, token.length, bye, 3)) {
                                interface.wrln((char *)"Goodbye!", 8);
                                exit(0);
                        }
                }

                switch (result) {
                case PARSE_EOB:
                        interface.wrbuf(ok, 4);
                        return true;
                case PARSE_LEN:
                        interface.wrln((char *)"parse error: token too long", 27);
                        return false;
                case PARSE_FAIL:
                        interface.wrln((char *)"parser failure", 14);
                        return false;
                default:
                        interface.wrln((char *)"*** the world is broken ***", 27);
                        exit(1);
                }
        }

        static void
        interpreter(IO &interface)
        {
                static size_t buflen = 0;
                static char linebuf[81];

                while (true) {
                        interface.wrch('?');
                        interface.wrch(' ');
                        buflen = interface.rdbuf(linebuf, 80, true, '\n');

The return value is being ignored right now, but later on it might be useful.
::

                        parser(interface, linebuf, buflen);
                }
        }

But does it work?
::

        ~/code/kforth (0) $ make
        g++ -std=c++14 -Wall -Werror -g -O0   -c -o linux/io.o linux/io.cc
        g++ -std=c++14 -Wall -Werror -g -O0   -c -o parser.o parser.cc
        g++ -std=c++14 -Wall -Werror -g -O0   -c -o kforth.o kforth.cc
        g++  -o kforth linux/io.o parser.o kforth.o
        ~/code/kforth (0) $ ./kforth 
        kforth interpreter
        ? 2 3 4 + * 1 SWAP  
        token: 2.
        token: 3.
        token: 4.
        token: +.
        token: *.
        token: 1.
        token: SWAP.
        ok.
        ? thistokenistoolong!
        parse error: token too long
        bye
        token: bye.
        Goodbye!
        ~/code/kforth (0) $ 

Heyo! Now I'm getting somewhere. The next logical step (to me) is to add in a
command parser and a standard vocabulary.

The snapshot of the code from here is in the tag part-0x03_.

.. _part-0x03: https://github.com/kisom/kforth/tree/part-0x03