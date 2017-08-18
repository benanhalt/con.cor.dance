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
as a persistent mutable object within which some div may have a map
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
program state in two separate locations, the Elm model and the Leaflet
interface, and shuttling messages back and forth
to keep them in sync.

What I really wanted was something like the way regular HTML is
rendered in Elm, where the map could just be computed purely from
the model.

## Enter mutation observers

Ideally, it would be possible to tie-in to or extend the Elm virtual DOM
system. There is an undocumented Elm feature called *Native Modules* that
might make that possible, but I haven't investigated that very much.

Instead, I have currently settled on a solution that involves adding a HTML5
data attribute with the map state to the to-be Leaflet container divs. These
divs are also given the class `leaflet-map`.

```elm
view : List WMSInfo -> Html msg
view wmsInfo =
    div
        [ class "leaflet-map"
        , attribute "data-leaflet" (serialize wmsInfo)
        ]
        []
```

Currently, the only map state I care about is a list of WMS layers to add
to the map. The *serialize* function just makes JSON out of the layer information.

```elm
import Json.Encode exposing (..)


type alias WMSInfo =
    { mapName : String
    , layers : List String
    , endPoint : String
    }


serialize : List WMSInfo -> String
serialize =
    List.map
        (\info ->
            object
                [ ( "mapName", string info.mapName )
                , ( "endPoint", string info.endPoint )
                , ( "layers", info.layers |> List.map string |> list )
                ]
        )
        >> list
        >> encode 0
```

Now, on the Javascript side I can watch for mutations to the DOM
involving elements with the `leaflet-map` class and invoke the necessary
Leaflet methods to match the state in the data attribute. The relevant DOM 
mutations are when elements with the `leaf-map` class
are added or removed anywhere in the page body and when the `data-leaflet`
attribute changes on any element.

There is a Web API for doing such things called
[MutationObserver](https://developer.mozilla.org/en-US/docs/Web/API/MutationObserver).
The way it is used is to create an observer instance with a callback function
that receives mutation events, and then activate the observer with some filters about
what kinds of mutations to look for.

```javascript
var observer = new MutationObserver(processMutations);

observer.observe(document.body, {
    subtree: true,
    childList: true,
    attributes: true,
    attributeFilter: ["data-leaflet"]
});
```

The `subtree` flag means to watch for mutations anywhere in the descendents of
the observed element which is the entire page body in this case. The `childList`
flag will catch additions or removals of elements. The `attributes` flag indicates
that changes to element attributes are of interest, but the `attributeFilter` allows
the parameter allows that observation to be limited to only the `data-leaflet`
attribute that contains the map information.

## Mutating the map

Using this mechanism to oserve relevant mutations to the DOM, the corresponding
calls to the Leaflet library can be made to make it match the desired state.

```javascript
function processMutations(mutations) {
    mutations.forEach(function(m) {
        processAddedNodes(m.addedNodes);
        processRemovedNodes(m.removedNodes);
        
        if (m.type == "attributes") {
            updateMap(m.target);
        }
    });
}
```

The mutation observer invokes its callback with a list of mutations. Each mutation
object has a list added child nodes and a list of removed child nodes that may be empty.
There is also a type attribute that indicates the type of mutation. Since there is only 
one attribute that matches the attribute filter, any mutation of the type "attributes"
means the element that was mutated, `m.target`, is a map container div that needs its map
to be updated.

Taking added nodes first, each added node is examined for any elments with class
"leaflet-map". In general the added node may contain an entire subtree with
multiple maps. For each matching element, the Leaflet map constructor is invoked.
Leaflet set an undocumented attribute, `_leaflet_id`, on the container element. This
unique (within the page) id is used as the key in a global dictionary, `maps`,
so that the Leaflet map object can be accessed. Finally, `updateMap` is called
that handles setting the map state and will be discussed shortly.

```javascript
function processAddedNodes(addedNodes) {
  addedNodes.forEach(function(n) {
      if (n.getElementsByClassName == null) return;

      var elements = n.getElementsByClassName("leaflet-map");
      Array.prototype.forEach.call(elements, function(element) {
          var map = L.map(element, {crs: L.CRS.EPSG4326}).setView([0, 0], 1);
          maps[element._leaflet_id] = map;  
          console.log("added leaflet id", element._leaflet_id);
          updateMap(element);
      });
  });
}
```

If a map is added or the "data-leaflet" attribute is changed, the map needs
to be updated with current state. The Leaflet map object instance is
obtained from the global `maps` dictionary according to the `_leaflet_id`
attribute mentioned above. A separate global `mapLayers` dictionary
keeps track of the layers that have been added to the map. All existing
layers are removed. The `element.dataset.leaflet` property contains
the value of the "data-leaflet" attribute as described in the
[HTML api](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/dataset).
This will be the JSON data from the Elm application. It is parsed
and used to add layers to map with each created layer object being added
to the `mapLayers` global so they can be removed later.

```javascript
function updateMap(element) {
    var map = maps[element._leaflet_id];
    if (map == null) return;
    console.log("updating leaflet id", element._leaflet_id);

    var layers = mapLayers[element._leaflet_id];
    if (layers != null) {
        layers.forEach(function(layer) {  map.removeLayer(layer); });
    }

    var wmsInfos = JSON.parse(element.dataset.leaflet);

    mapLayers[element._leaflet_id] = wmsInfos.map(function(wmsInfo) {
        return L.tileLayer.wms(wmsInfo.endPoint, {
            mapName: wmsInfo.mapName,
            format: 'image/png',
            version: '1.1.0',
            transparent: true,
            layers: wmsInfo.layers.join(',')
        }).addTo(map);
    });
}
```

When nodes are removed, the node's descendants are again searched
for the "leaflet-map" class. Each such element is inspected for the `_leaflet_id`
attribute described above. If the `_leaflet_id` attribute is present, the `processAddedNodes`
function must have added the map. This means the `_leaflet_id` value should
be in the global `maps` dictionary pointing to the corresponding Leaflet map
instance which has its `remove()` method invoked. The corresponding `maps` and
`mapLayers` entries are then nulled out.

```javascript
  removedNodes.forEach(function(n) {
            if (n.getElementsByClassName == null) return;

            var elements = n.getElementsByClassName("leaflet-map");
            Array.prototype.forEach.call(elements, function(element) {
                if (element._leaflet_id != null) {
                    console.log("removing map with leaflet id", element._leaflet_id);
                    maps[element._leaflet_id].remove();
                    maps[element._leaflet_id] = null;
                    mapLayers[element._leaflet_id] = null;
                }
            });
        });
```
