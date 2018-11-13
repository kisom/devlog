Title: On matrix transforms
Date: 2018-11-13 07:35
Tags: maths, linear-algebra

Last night, I got through the linear algebra refresher in the AI
Programming with Python class. It's done by the same person behind
[3 blue 1 brown](http://www.3blue1brown.com/), and he focuses on
visualising the implications of the maths in the 2D space before
explaining the mathematical definitions of things. I found this approach
very helpful, and I think I'm much closer to really understanding matrix
transformations. What really made things click was when I decided to
explore some of the ideas on my own on graph paper.

I started with thinking about rotations, because they're easy to
visualise and reason about, at least for me. I really came away
with two insights: the first is that multiplying matrices together
is a way to compose the transformations they encode.

So, starting with the unit vectors:

```
i = [1, 0]
j = [0, 1]
```

This says graphically that the i unit vector has a length of 1 in the x
axis and no length in the y axis, while the j unit vector has no length in
the x axis but a length of 1 in the y axis. We write vectors in columnar
for, which means these would be written like

```
    |1|      |0|
i = |0|  j = |1|
```

(So those are a little imbalanced, but it's what I have to work with
right now...)

If we want to encode the unit vector as a transformation matrix, we
place them side-by-side:

```
       |1 0|
unit = |0 1|
```

If we draw out arrows for these on graph paper and rotate them (try
doing it physically), we find that the unit vectors for a 90º clockwise
rotation are

```
i = [0, -1]
j = [1, 0]
```

I think for a while, I equated *i* with the *x* axis and *j* with
the *y* axis, and so I never really understood the transform
part of it. However, if we think of the unit vectors as the
*[basis](https://en.wikipedia.org/wiki/Basis_(linear_algebra))*, it
means that we draw our vectors normally such that they're based on
the positive x, positive y coordinate system. The rotated unit vectors
provide a new reference frame: the vectors we draw are still the same
(just a magnitude and direction), where they end up depends heavily
on our frame of reference, or basis. An easy way to visualise this
is with some vector that lies entirely on the y axis:

```
v = [0; 4]
```

If we rotate it by 90º, it ends up falling entirely on the positive
side of the x axis:

```
octave:1> [0, 1; -1, 0] * [0; 4]
ans =

   4
   0
```

If we wanted to rotate this again by 90º, we could do another 90º
rotation:

```
octave:2> [0, 1; -1, 0] * ans
ans =

   0
  -4
```

Indeed, rotating again by 90º gives us a line that's now in the negative
y-axis. It's a bit cumbersome to just keep rotating by 90º, though. If
we think about how we accomplished this, what we did according to the
rules of distributivity is

```
rotation * rotation * vector = (rotation * rotation) * vector
```

This means we could compose our two rotations into one transformation
matrix and do everything in one multiplication. Multiplying the 90º
rotation by itself:

```
octave:3> [0, 1; -1, 0] * [0, 1; -1, 0]
ans =

  -1   0
   0  -1
```

If we look at where the unit vectors end up when rotated 180º it makes
sense (try drawing it out on graph paper). This new matrix gives us the
same answer for our rotated line:

```
octave:4> [-1, 0; 0, -1] * [0; 4]
ans =

   0
  -4
```

Here's the thing: we've just seen that transformations, which can just
be represented as matrices, are composable by multiplication. Let's think
about another transformation: doubling the size of our vectors. We want
to multiply them by 2, e.g.

```
octave:5> v = [0; 4]
v =

   0
   4

octave:6> v * 2
ans =

   0
   8
```

If we represent this as a transformation matrix, we could do this by
looking at the effect on our basis vectors:

```
octave:7> [1, 0; 0, 1] * 2
ans =

   2   0
   0   2
```

We could stretch our vector, then rotate it by composing a 90º rotation
with our stretch transformation, which is a pretty simple transform:

```
octave:8> [2, 0; 0, 2] * [0, 1; -1, 0]
ans =

   0   2
  -2   0
```

These simple, visually verifiable transformations helped me to make
sense of how these work in a general sense.

An insight that's specific to rotation transformations is a general
form for a 2D matrix:

```

Rot(θ) = | cos(θ)  sin(θ) |
         |-sin(θ) -cos(θ) |
```

I [wrote](https://p.kyleisom.net/matrix_rotation_transforms.py.html)
up some of this in a Python demo.
