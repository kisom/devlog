Title: The Chromebook replacement
Date: 2017-09-10 17:45
Tags: meta

I replaced the Acer C720 chromebook with a used Lenovo N22. Just to
compare the numbers real quick:

```
+------+------+----------------+-----+------+-------------------------------+
|      | Cost |   Condition    | RAM | Disk |             CPU               |
+------+------+----------------+-----+------+-------------------------------+
| C720 |  200 |    brand new   |  2G |  16G | Intel Celeron 2955U @ 1.40GHz |
+------+------+----------------+-----+------+-------------------------------+
|  N22 |  100 | used, like new | 4G |  32G |  Intel Celeron N3050 @ 1.60GHz |
+------+------+----------------+-----+------+-------------------------------+
```

I originally started using the C720 to work with a workflow that
focused on productivity through a form of minimalism. To that end, I
have severe constraints on computational resources with a focus on
high battery life and staying offline as much as possible. I've been
using it for the nanodegree programs with a lot of success; I find it
easier to focus on the problem at hand. With that being said, if I
could have the same specs on the N22 as I did on the Chromebook, I
might have gone for it. The biggest reason I moved is that the
keyboard on the N22 is a real keyboard, not the stunted Chromebook
keyboard. Other than that, the C720 performed more or less
fantastically.

Despite the (clock-speed-wise) faster processor, this machine is
noticeably slower. So far, that hasn't been an issue, but it is
sometimes a pain to have my nanodegree Anaconda environment take ten
seconds to load (it's essentially a `source activate aind && tmux new
ipython`). That being said, it takes about twice as long to run my
Sudoku solver over 1,000 randomly-generated "intermediate" Sudoku; I
tested the time to solve all 1,000 puzzles against four machines:

* bragi: this is the name of the N22 and the C720
* tessier: this is my gaming laptop running Ubuntu
* carbon: the Jetson TX2 "AI" board

Results:

```
+-------+-----+------+---------+--------+
Machine | N22 | C720 | tessier | carbon |
+-------+-----+------+---------+--------+
|  Time | 50s |  28s |   10s   |   32s  |
+-------+-----+------+---------+--------+
```

(What's interesting to me is how competitive the Chromebook was *on
this particular problem* with the gaming laptop.)

In some ways, this slow down is nice as a forcing function to build
more efficient programs. Sometimes, though, I just want to be lazy and
test some ideas out.

As for the rest of the laptop, it's generally pretty decent. The
construction is fairly solid and feels sturdy. The screen is decent: I
mostly limit myself to emacs (writing and some Python work), IPython,
chromium, and a few random other things here and there. At 1366x768,
it's enough screen estate to do this and though I've been keeping the
backlight at 25%, it's bright enough to use here in most
conditions. The battery seems to last pretty long, as well: `acpi` is
reporting 80% with between 8h 45m and 9h 45m remaining after having
had it on for a few hours today (though mostly offline). It's slightly
thicker, but that hasn't posed an issue yet. It fits everywhere the
C720 did.

I had to update my ansible and dotfiles repos to account for having an
actual keyboard, but now it's back to a fairly sane config that should
be transferrable to other machines. The Chromebook keyboard quirks
were one of the things keeping me from using this config in a few
other places (for example, my `xmodmap(1)` config is kept in a
dotfiles repo, and isn't managed by Salt).

Overall, for $100, it's a pretty good deal; though, if I could have
just replaced the keyboard (and yes, I'm sure I could have figured
something out, but I really didn't want to mess around taking my
laptop apart) I probably would have kept the C720 in service. I guess
there's more space for music on here...
