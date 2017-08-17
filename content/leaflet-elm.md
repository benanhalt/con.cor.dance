Title: Using Leaflet maps in an Elm app
Date: 2017-08-17T16:41-0500
Category: programming
Status: draft

I recently started a project creating a web app that requires
displaying maps. This was to be a browser based app, but I wanted to
use something safer and more maintainable than Javascript. I decided
to give [Elm](http://elm-lang.org/) a try and have been fairly happy
with it. However, I couldn't find any pure Elm libraries for
displaying maps that supported WMS layers and other features that
would be needed.

So, the question became whether it would be possible to use a
Javascript mapping library with my Elm application. It turns out that
it is not too difficult to get basic rendering of maps to work using
the [Leaflet](http://leafletjs.com/) library. That will be the subject
of this post.

In the future, I will attempt to add more advanced features such as
selecting regions within a displayed map.


## Paradigm conflict

The main difficulty with using Elm and Leaflet together is that Elm is
totally based on the reactive paradigm where the entire state of your
app is captured in a single immutable data structure from which the
DOM is derived via a pure view function. Any change in what the user
sees has to be accomplished by updating the state (*Model* in Elm
parlance) in some way and allowing the DOM to be recomputed. This way
of doing things and the resulting program structure are
called
[The Elm Architecture](https://guide.elm-lang.org/architecture/), or
*TEA*.

Behind the scenes the view function actually generates *virtual* DOM
structures which are diffed to compute mutations to the real DOM. This
is so that minor changes don't cause the whole page to be
redrawn. But, this mechanism is not visible to the application
programmer.

On the other hand, Leaflet and similar Javascript map libraries make
use of mutation and side effects with full abandon. The DOM is treated
as a persistent mutable object within which some `<div>` may have a map
object attached. The map object then provides methods such as
*setView* or *addLayer* that mutate the state of the map and update
the DOM to effect the change.

## Elm interop with Javascript

The primary means of interoperating with external Javascript in Elm is
through *ports*. These allow incoming messages to be subscribed to,
and outgoing messages to be dispatched. Incoming messages result in
calls to a model update function when received. And, outgoing messages
can be generated upon model updates.

My initial approach was to use this port system to send messages out
to Javascript for actions like: "add a map to the *div* with id
'foobar'", "remove the map from the div", "add this WMS layer", etc. I
managed to get this scheme to work, but it was complicated and seemed
contrary to *TEA*. This was because I was essentially maintaining
program state in two locations, the Elm model and the Leaflet
Javascript library independently and shuttling messages back and forth
to keep them in sync.

What I really wanted was something like the way regular HTML is
rendered in Elm, where the map would just be computed purely from
the model.
