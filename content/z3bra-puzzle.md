Title: Z3bra Puzzle
Date: 2024-05-24
Category: programming
Tags: math, programming, logic, z3

I occasionally encounter problems akin to [logic grid
puzzles](https://en.wikipedia.org/wiki/Logic_puzzle#Logic_grid_puzzles)
in programming challenges or other contexts. I usually approach them
through some ad hoc backtracking algorithm. Recently I decided to try
and develop a systematic approach for solving such problems without
reinventing the wheel each time.

These puzzles fall into the category of [constraint satisfaction
problems](https://en.wikipedia.org/wiki/Constraint_satisfaction_problem). I
knew that tools like the
[SMT](https://en.wikipedia.org/wiki/Satisfiability_modulo_theories)
solver, [Z3](https://en.wikipedia.org/wiki/Z3_Theorem_Prover), could
be used to solve such problems, but it wasn't immediately obvious to
me how to go about it.

I encountered some difficulty finding examples or tutorials on
this. But, I did find [this
post](https://davidsherenowitsa.party/2018/09/19/solving-logic-puzzles-with-z3.html)
by David Cook which, along with [the associated
code](https://gist.github.com/divergentdave/13a2a557c26146fc3e3b15a398f8428b),
was very helpful in getting started.

## Background

First of all, what are the characteristics of logic grid puzzles, and
how can they be described in a way that facilitates a systematic
approach to solving them?

Broadly speaking, a logic grid puzzle can be characterized as a set of
dimensions, each of which has a number of discreet values. If the
puzzle is solvable, there are unique correspondences between the
values of each of the dimensions. The goal is to explicitly determine
the correspondences given a list of clues amounting to assertions that
most hold.

The pen and paper approach involves representing the puzzle as a grid
and proceeds by marking correspondences as either established or
excluded using check marks and cross marks. For an SMT solution, a
means of encoding the puzzle using the abstractions provided by the
SMT solver must be sought.

## The Zebra Puzzle

A classic example of this sort of puzzle is the [Zebra
Puzzle](https://en.wikipedia.org/wiki/Zebra_Puzzle). Quoting from the
Wikipedia article:

>The following version of the puzzle appeared in Life International in 1962:
>
>    1. There are five houses.
>    2. The Englishman lives in the red house.
>    3. The Spaniard owns the dog.
>    4. Coffee is drunk in the green house.
>    5. The Ukrainian drinks tea.
>    6. The green house is immediately to the right of the ivory house.
>    7. The Old Gold smoker owns snails.
>    8. Kools are smoked in the yellow house.
>    9. Milk is drunk in the middle house.
>    10. The Norwegian lives in the first house.
>    11. The man who smokes Chesterfields lives in the house next to the man with the fox.
>    12. Kools are smoked in the house next to the house where the horse is kept.
>    13. The Lucky Strike smoker drinks orange juice.
>    14. The Japanese smokes Parliaments.
>    15. The Norwegian lives next to the blue house.
>
>    Now, who drinks water? Who owns the zebra?
>
>    In the interest of clarity, it must be added that each of the
>    five houses is painted a different color, and their inhabitants
>    are of different national extractions, own different pets, drink
>    different beverages and smoke different brands of American
>    cigarets [sic]. One other thing: in statement 6, right means
>    your right.

### Z3 Sorts

In this puzzle there are five dimensions. The colors of the houses,
the nationality of their inhabitants, the species of pets in the
houses, and the beverage and cigarette preferences of the
inhabitants. In Python Z3 each of these dimensions can be expressed as
an **_EnumSort_**.

```python
House, (red_house, green_house, ivory_house, yellow_house, blue_house) = \
    EnumSort("House", "red green ivory yellow blue".split())

Nation, (england, spain, ukraine, norway, japan) = \
    EnumSort("Nation", "england spain ukraine norway japan".split())

Beverage, (coffee, tea, milk, juice, water) = \
    EnumSort("Drink", "coffee tea milk juice water".split())

Pet, (dog, snails, fox, horse, zebra) = \
    EnumSort("Pet", "dog snails fox horse zebra".split())

Smoke, (oldgold, kools, chesterfields, luckystrikes, parliaments) = \
    EnumSort("Smoke", "oldgold kools chesterfields luckystrikes parliaments".split())
```

An **_EnumSort_** defines a new Z3 **_sort_**, similar to a type,
consisting of the specific given values and returns references to the
sort itself and constants for each of the values. The arguments are
the name of the sort in Z3 and the names of the values.

### Z3 Function Declarations

The puzzle makes clear that correspondences amongst the dimensions are
all one-to-one.

> In the interest of clarity, it must be added that each of the five
> houses is painted a different color, and their inhabitants are of
> different national extractions, own different pets, drink different
> beverages and smoke different brands of American cigarets [sic].

This means any of the dimensions could be thought of as a function of
any of the others. For this approach, however, it is useful to pick
one dimension as an independent variable and treat the other
dimensions as dependent variables that are functions of it.

Many of the clues are stated in terms of the color of the houses, so
I'll use that as the independent variable. That's why I've used colors
as the values of the **_House_** sort. For each of the other
dimensions, a function is declared from the **_House_** sort to the
sort corresponding to that dimension. The **_Function_** constructor
takes the name of the function, the domain sort, and the codomain sort
as arguments.

```python
nationality = Function("nationality", House, Nation)

drinks = Function("drinks", House, Beverage)

pet = Function("pet", House, Pet)

smokes = Function("smokes", House, Smoke)
```

Some of the clues involve the ordering of the houses. This is handled
by declaring a function from the **_House_** sort to the integers,
**_IntSort_**.

```python
house_number = Function("house_number", House, IntSort())
```

### Constraints

With the sorts and functions declared, the constraints of the problem
can be added as assertions. This is done by creating a **_Solver_**
instance and using the **_add_** method which can accept multiple
assertions as arguments.

```python
solver = Solver()
solver.add(...)
```

The constraints will come from the clues and from the requirement that
the functions be one-to-one. To start with a simple assertion, clue 2
states, "The Englishman lives in the red house." This can be directly
translated into a Z3 constraint by asserting that the
**_nationality_** function evaluated at the **_red_house_** value of
the **_House_** sort must give the **_england_** value of the
**_Nation_** sort.

```python
solver.add(
    # 2. The Englishman lives in the red house.
    nationality(red_house) == england
)
```

Clues 4 and 8 are also straightforward since they involve statements
about specific colors of houses, the independent variable.

```python
solver.add(
    # 4. Coffee is drunk in the green house.
    drinks(green_house) == coffee,

    # 8. Kools are smoked in the yellow house.
    smokes(yellow_house) == kools,
)
```

#### Relationships between two dependent variables

When a clue involves a relationship between two dependent variables,
the situation is a bit more complicated. Clue 3, "The Spaniard owns
the dog," is an example. There is no function from **_Nation_** to
**_Pet_** or vice-versa to characterize this statement. Nor is there
is an inverse from either to the independent variable that would
permit `pet(nationality_inverse(spain)) == dog`. Instead, a universal
quantifier can be used to introduce a variable, **_h_**, of the
**_House_** sort. Now it can be asserted that anytime `nationality(h)`
is **_spain_**, `pet(h)` must be **_dog_**.

The universal quantifier takes the form `ForAll(vars, assertion)`,
where **_vars_** can be single variable or a list of variables. Owing to
how the language is represented in Python, each variable has to be
represented using a predefined constant to specify the sort. This
is a bit confusing since the variable inside the quantifier bears no
relationship to the constant other than the sort. With this in mind,
clue 3 can be encoded as follows:

```python
h = Const('h', House) # A dummy constant.
solver.add(
    # 3. The Spaniard owns the dog.
    ForAll(h, (nationality(h) == spain) == (pet(h) == dog))
)
```

The expressions `nationality(h) == spain` and `pet(h) == dog` both
evaluate to values of **_BoolSort_**, either true or false. By equating
them, the quantifier requires both to evaluate to the same truth value
for a given **_h_**. Meaning, for any given house "the occupant is
Spanish" is equivalent to "the house has a dog".  For clarity I think
it is worth defining a helper function for logical equivalence.

```python
def Iff(a, b):
    return a == b
```

This provides a nice parallel with the provided **_Implies_** function
that will be used later. With the **_ForAll_** and **_Iff_**
functions, clues 3, 5, 7, 13, and 14 can be encoded.

```python
h = Const('h', House) # A dummy constant.
solver.add(
    # 3. The Spaniard owns the dog.
    ForAll(h, Iff(nationality(h) == spain, pet(h) == dog)),

    # 5. The Ukrainian drinks tea.
    ForAll(h, Iff(nationality(h) == ukraine, drinks(h) == tea)),

    # 7. The Old Gold smoker owns snails.
    ForAll(h, Iff(smokes(h) == oldgold, pet(h) == snails)),
    
    # 13. The Lucky Strike smoker drinks orange juice.
    ForAll(h, Iff(smokes(h) == luckystrikes, drinks(h) == juice)),

    # 14. The Japanese smokes Parliaments.
    ForAll(h, Iff(nationality(h) == japan, smokes(h) == parliaments)),
)
```

Note that the same dummy constant **_h_** can be used in all of the
assertions.

The function **_house_number_** has been declared from houses to
integers, but it is under specified. If the houses are numbered from
one to five, left to right, clues 1, 6, 9, and 10 can be formulated.

```python
solver.add(
    # 1. There are five houses.
    ForAll(h, And(house_number(h) >= 1, house_number(h) <= 5)),

    # 6. The green house is immediately to the right of the ivory house.
    house_number(green_house) == house_number(ivory_house) + 1,

    # 9. Milk is drunk in the middle house.
    ForAll(h, Iff(house_number(h) == 3, drinks(h) == milk)),

    # 10. The Norwegian lives in the first house.
    ForAll(h, Iff(nationality(h) == norway, house_number(h) == 1)),
)
```

The assertion for the first rule is really requiring the house numbers
to go from 1 to 5. The definition of the **_House_** sort already fixed
the cardinality at five.

#### Constraints involving two variables

Clue 11 states, "The man who smokes Chesterfields lives in the house
next to the man with the fox." This is a statement about two houses
neither specified in terms of the independent variable, color. This
can be handled by using a universal quantifier over two house
variables, **_h_** and **_g_**, with predicates `smokes(h) ==
chesterfields` and `pet(g) == fox`. When the predicates hold, the
houses must have consecutive house numbers.

```python
h, g = Consts('h g')

def next_to(h, g):
    return Or(
        house_number(h) == house_number(g) + 1,
        house_number(h) == house_number(g) - 1,
    )
    
solver.add(
    # 11. The man who smokes Chesterfields lives in the house next
    # to the man with the fox.
    ForAll([h, g], Implies(
        And(smokes(h) == chesterfields, pet(g) == fox),
        next_to(h, g)
    )),
)
```

Here **_Implies_** is used instead of **_Iff_** since the implication
is in one direction only. Two houses may be next to each other without
the two predicates holding.

Clues 12 and 15 are handled similarly.

```python
solver.add(
    # 12. Kools are smoked in the house next to the house where the horse is kept.
    ForAll([h, g], Implies(
        And(smokes(h) == kools, pet(g) == horse),
        next_to(h, g)
    )),

    # 15. The Norwegian lives next to the blue house.
    ForAll(h, Implies(
        nationality(h) == norway,
        next_to(h, blue_house)
    )),
)
```

#### Bijectivity constraints


Finally, constraints need to be added regarding the one-to-one
correspondence amongst all the dimensions. This requires all of the
functions **_house_number_**, **_nationality_**, **_pet_**,
**_drinks_**, and **_smokes_** to be injective. Given any two houses,
**_h_** and **_g_**, if they are distinct, their images under each of
the functions must be distinct. Because the house color has been used
as the independent variable, it doesn't appear in the
expression. Instead there is a requirement that the house numbers be
distinct.

```python
solver.add(
    # In the interest of clarity, it must be added that each of the five
    # houses is painted a different color, and their inhabitants are of
    # different national extractions, own different pets, drink different
    # beverages and smoke different brands of American cigarets [sic].
    ForAll([h, g], Implies(
        h != g,
        And(
            house_number(h) != house_number(g),
            nationality(h) != nationality(g),
            pet(h) != pet(g),
            drinks(h) != drinks(g),
            smokes(h) != smokes(g),
        )
    ))
)
```

### Solution

With all of the constraints added to the solver, the satisfiability of
the system can be checked. If the system can be satisfied, the solver
can provide a *model* which does so.

```python
assert solver.check() == sat

model = solver.model()
```

Such a model provides explicit definitions of all the declared
functions and can evaluate arbitrary expressions. 

```
In [1]: model.eval(house_number(red_house))
Out[1]: 3

In [2]: model.eval(smokes(ivory_house))
Out[2]: luckystrikes
```

The puzzle asks, "who drinks water? Who owns the zebra?" These
questions can be answered by declaring two constants of the
**_House_** sort which are constrained to meet the two predicates.

```python
# Now, who drinks water? Who owns the zebra?

the_water_house = Const("the_water_house", House)
the_zebra_house = Const("the_zebra_house", House)

solver.add(
    drinks(the_water_house) == water,
    pet(the_zebra_house) == zebra
)

assert solver.check() == sat

model = solver.model()
```

The resulting model can then return explicit values for the two
constants.

```
In [3]: model.eval(the_water_house)
Out[3]: yellow

In [4]: model.eval(the_zebra_house)
Out[4]: green
```

If "who" means the nationality of the inhabitants, that can be
answered, too.

```
In [5]: model.eval(nationality(the_water_house))
Out[5]: norway

In [6]: model.eval(nationality(the_zebra_house))
Out[6]: japan
```

The Norwegian drinks the water, and the person with the zebra is
Japanese.

### Code

The full [code for this
example](https://github.com/benanhalt/logic-puzzles/blob/main/zebra.py)
can be found in [my github
repository](https://github.com/benanhalt/logic-puzzles) which also
contains other examples and approaches.

