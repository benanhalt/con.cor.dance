Title: Advent of Code 2023, Day 24, Part 2
Date: 2024-03-22

The problem can be solved without faffing about at the component level
by working with vectors and matrices.

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
hailstone $i$, since the hypothesis of the problem is that all
hailstones are struck by the same rock. The choice of the $i$th
hailstone in obtaining the above equation was arbitrary. We can chose
a different hailstone $j \ne i$ and get the same equation with
the $i$ subscripts replaced with $j$. Subtracting the two equations
will then eliminate the quadratic $\vec{u} \times \vec{s}$ term.

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
$\vec{u}$ remembering to include the resulting minus sign.

$$
(\vec{v}_i  - \vec{v}_j) \times \vec{s} - (\vec{r}_i - \vec{r}_j)
\times \vec{u} 
= \vec{v}_i \times \vec{r}_i - \vec{v}_j \times \vec{r}_j
$$

This is a system of three linear equations with six unknowns. Another
three equations are required to fully determine the solution. These
can be obtained by replacing the arbitrary choice of the $j$th
hailstone with a third hailstone $k$ distinct from both $j$ and $i$ to
yield a new independent vector equation.

$$
(\vec{v}_i  - \vec{v}_k) \times \vec{s} - (\vec{r}_i - \vec{r}_k)
\times \vec{u} 
= \vec{v}_i \times \vec{r}_i - \vec{v}_k \times \vec{r}_k
$$

To solve this linear system, we need to translate the two vector
equations into one six dimensional matrix equation. First, the cross
products are replaced with their [matrix
forms](https://en.wikipedia.org/wiki/Cross_product#Conversion_to_matrix_multiplication)
such that $\vec{a}\times\vec{b} = [\vec{a}]_\times\boldsymbol{b}$
where $\boldsymbol{b}$ is $\vec{b}$ as a column vector. The matrix
$[\vec{a}]_\times$ is defined as

$$
[\vec{a}]_{\times} \stackrel{\rm def}{=} \begin{bmatrix}\,\,0&\!-a_3&\,\,\,a_2\\\,\,\,a_3&0&\!-a_1\\\!-a_2&\,\,a_1&\,\,0\end{bmatrix}
$$

where $[a_1, a_2, a_3]^T = \boldsymbol{a}$ are the components of
$\vec{a}$ in the same coordinate system as $\boldsymbol{b}$.
