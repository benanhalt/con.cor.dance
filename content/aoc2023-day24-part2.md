Title: Rocks and Hailstones
Date: 2024-03-22
Category: math
Tags: math, adventofcode

I had fun solving the second part of [Day 24 of Advent of Code this
year](https://adventofcode.com/2023/day/24). This was a more
mathematical problem than most, and by working with vectors and
matrices it can be solved with minimal faffing about at the component
level.

We are given a set of initial positions and velocities for a number, $n>
3$, of hailstones. The hailstones travel in straight lines at constant
velocities, and we are asked to find the initial position and velocity
of rock thrown so that it will impact (without then changing its
velocity) all of the given hailstones. We are told the the paths of
the hailstones are such that this is possible.

Let $\vec{r}_i$ and $\vec{v}_i$ represent the initial position and
velocity vectors of the $i$th hailstone. These are given. Let
$\vec{s}$ and $\vec{u}$ represent the initial position and
velocity vectors of the thrown rock. These are the unknowns we are
solving for. If the thrown rock impacts the $i$th hailstone at time
$t_i$, their positions at that time must be the same.

$$ \vec{u} t_i + \vec{s} = \vec{v}_i t_i + \vec{r}_i $$

$$ (\vec{u} - \vec{v}_i)t_i = \vec{r}_i - \vec{s} $$

Remembering that the cross product of parallel vectors is zero, we can
eliminate $t_i$, which is an unknown we don't care about, by taking the
cross product of both sides with $(\vec{u} - \vec{v}_i)$.

$$ (\vec{u} - \vec{v}_i)\times(\vec{u} - \vec{v}_i)t_i = (\vec{u} - \vec{v}_i)\times(\vec{r}_i - \vec{s}) $$

$$ \vec{0} = (\vec{u} - \vec{v}_i)\times(\vec{r}_i - \vec{s}) $$

Geometrically, this is saying the velocity of the thrown rock must be
parallel to the vector between its initial position and that of the
hailstone. This makes sense. We proceed by expanding out the
multiplication.

$$ \vec{0} = \vec{u} \times \vec{r}_i - \vec{u} \times \vec{s} -
\vec{v}_i \times \vec{r}_i + \vec{v}_i \times \vec{s} $$

The terms $\vec{u} \times \vec{r}_i$ and $\vec{v}_i \times \vec{s}$
are linear in the unknowns and unproblematic. The term $\vec{v}_i
\times \vec{r}_i$ is a constant formed from the givens. In contrast,
$\vec{u} \times \vec{s}$ represents products among the unknowns and
would prevent solution by standard methods for systems of linear
equations. On the other hand, this term _only_ includes properties of
the thrown rock. This means it is independent of the impacted
hailstone $i$ since all hailstones are struck by the same rock. The
choice of the $i$th hailstone in obtaining the above equation was
arbitrary. We can chose a different hailstone $j \ne i$ and get the
same equation with the $i$ subscripts replaced with $j$. Subtracting
the two equations will then eliminate the quadratic $\vec{u} \times
\vec{s}$ term.

$$
\begin{align}
\vec{u} \times \vec{r}_i - \vec{u} \times \vec{s} -
\vec{v}_i \times \vec{r}_i + \vec{v}_i \times \vec{s} &=&\vec{0} \\
\vec{u} \times \vec{r}_j - \vec{u} \times \vec{s} -
\vec{v}_j \times \vec{r}_j + \vec{v}_j \times \vec{s}  &=&\vec{0} \\
\hline \\
\vec{u} \times (\vec{r}_i - \vec{r}_j)
- \vec{v}_i \times \vec{r}_i + \vec{v}_j \times \vec{r}_j
+ (\vec{v}_i  - \vec{v}_j) \times \vec{s} &=&\vec{0}
\end{align}
$$

We rearrange the resulting equation by moving the constant terms to
the right hand side and reversing the cross product involving
$\vec{u}$. Reversing the cross product introduces a minus sign which
we absorb by reversing the subtraction in $(\vec{r}_i - \vec{r}_j)$.

$$
(\vec{v}_i  - \vec{v}_j) \times \vec{s} + (\vec{r}_j - \vec{r}_i)
\times \vec{u} 
= \vec{v}_i \times \vec{r}_i - \vec{v}_j \times \vec{r}_j
$$

This is a system of three linear equations with six unknowns. Another
three equations are required to fully determine the solution. These
can be obtained by replacing the arbitrary choice of the $j$th
hailstone with a third hailstone $k$ distinct from both $j$ and $i$ to
yield a new, independent vector equation.

$$
(\vec{v}_i  - \vec{v}_k) \times \vec{s} + (\vec{r}_k - \vec{r}_i)
\times \vec{u} 
= \vec{v}_i \times \vec{r}_i - \vec{v}_k \times \vec{r}_k
$$

To solve this linear system we need to translate the two vector
equations into one six dimensional matrix equation of the form
$\boldsymbol{Mx}=\boldsymbol{b}$.

The cross products can be represented in [matrix
form](https://en.wikipedia.org/wiki/Cross_product#Conversion_to_matrix_multiplication),
$\vec{a}\times\vec{b} = [\vec{a}]_\times\boldsymbol{b}$
where $\boldsymbol{b}$ is $\vec{b}$ as a column vector and the matrix
$[\vec{a}]_\times$ is defined as

$$
[\vec{a}]_{\times} \stackrel{\rm def}{=} \begin{bmatrix}\,\,0&\!-a_3&\,\,\,a_2\\\,\,\,a_3&0&\!-a_1\\\!-a_2&\,\,a_1&\,\,0\end{bmatrix}
$$

with $[a_1\, a_2\, a_3]^T = \boldsymbol{a}$ being the components of
$\vec{a}$. 

With this replacement the equations will take the forms

$$ [\vec{v}_i - \vec{v}_j]_\times \boldsymbol{s} + [\vec{r}_j -
\vec{r}_i]_\times \boldsymbol{u} = [\vec{v}_i]_\times \boldsymbol{r}_i -
[\vec{v}_j]_\times \boldsymbol{r}_j
$$
and
$$ [\vec{v}_i - \vec{v}_k]_\times \boldsymbol{s} + [\vec{r}_k -
\vec{r}_i]_\times \boldsymbol{u} = [\vec{v}_i]_\times \boldsymbol{r}_i -
[\vec{v}_k]_\times \boldsymbol{r}_k.
$$

We'll also need to represent all six unknowns in one column vector
$\boldsymbol{x}$ which we can define by stacking $\boldsymbol{s}$ atop
$\boldsymbol{u}$.

$$\boldsymbol{x} \stackrel{\rm def}{=} \begin{bmatrix}s_1\\ s_2\\ s_3\\ u_1\\ u_2\\ u_3\end{bmatrix}$$

Now the system of equations can be written using block matrices as

$$
\left[\begin{array}{@{}c|c@{}}
  [\vec{v}_i - \vec{v}_j]_\times &  [\vec{r}_j - \vec{r}_i]_\times \\\hline
  [\vec{v}_i - \vec{v}_k]_\times &  [\vec{r}_k - \vec{r}_i]_\times \\
\end{array}\right]\boldsymbol{x} = \begin{bmatrix}
[\vec{v}_i]_\times \boldsymbol{r}_i - [\vec{v}_j]_\times \boldsymbol{r}_j \\\hline
[\vec{v}_i]_\times \boldsymbol{r}_i - [\vec{v}_k]_\times \boldsymbol{r}_k
\end{bmatrix}.
$$

This is a six dimensional system of equations where the left hand side
consists of a $6\times6$ square matrix $\boldsymbol{M}$ times our six
component column vector of unknowns, and the right hand side is a
$6\times1$ column vector $\boldsymbol{b}$. This system can be solved
using standard methods such as Gaussian elimination. To compute
$\boldsymbol{M}$ and $\boldsymbol{b}$, we just need functions for the
cross product matrix $[\vec{v}]_\times$, for the multiplication of a
vector by a matrix, for subtracting two vectors, and for joining
matrices horizontally and vertically into block matrices.

I had hoped to use the Haskell `hmatrix` package since it includes the
necessary functions except for $[\vec{a}]_\times$ and has a `solve`
function for linear systems. Unfortunately it doesn't support
arbitrary precision rational numbers which is required to produce the
exact answer called for by AoC. I ended up writing my own
implementation of the functions and adapted a Guassian elimination
routine from
[https://haskellicious.wordpress.com/2012/11/26/the-gauss-algorithm-in-haskell/](https://haskellicious.wordpress.com/2012/11/26/the-gauss-algorithm-in-haskell/). I
won't include or discuss the code here since I just wanted to
highlight the mathematical aspects. The interested reader can find the
code in my [Advent of Code
solutions](https://github.com/benanhalt/AoC2023/blob/main/day24/solution.hs)
repository.
