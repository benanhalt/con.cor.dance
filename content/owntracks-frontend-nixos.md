Title: Declarative Deployment of OwnTracks Frontend with NixOS
Date: 2025-04-16
Category: self-hosting
Tags: nixos, owntracks

This a followup to my [previous
post](owntracks-with-nixos-and-tailscale.html) about setting up
OwnTracks on a home server running NixOS. One step of that process was
to download the OwnTracks Frontend single page application zip archive
and copy it into `/var/www/html/owntracks` to be served by Nginx. Now
I'd like to look at replacing this procedure with a declarative
approach by defining the resource in the server's `configuration.nix`.

## An Aside: Google Drops the Ball

It turns out my concerns about Google's Map Timeline service were
prescient. Last month, a "technical issue" resulted in the [loss of
users' Timeline
data](https://arstechnica.com/gadgets/2025/03/oops-google-says-it-might-have-deleted-your-maps-timeline-data/). Luckily,
I had the back-up-to-cloud option turned on and was able to recover my
Timeline history. Once I had done that, I [exported the
data](https://www.reddit.com/r/GoogleMaps/comments/1chlsst/comment/la6n0k2/)
from the app for safekeeping. At some point I might try converting and
importing that data into OwnTracks.

## Writing a Nix Derivation

The first step to the declarative deployment is to write a Nix
derivation that packages the Frontend application. The principled
thing to do would probably be referencing the source repo and building
the application as part of the derivation. But since this is a
Javascript project built using Vite, I was afraid doing that might be
complicated. Also, I am primarily interested in a reproducible *server
deployment* rather than the reproducibility of the package itself. By
that logic I decided to base the derivation on the prebuilt artifact
from the repo's
[releases](https://github.com/owntracks/frontend/releases).

Here the goal will be to write a `owntracks-frontend.nix` derivation
and a `default.nix` to invoke it so that executing `nix-build -A
owntrack-frontend` generates a `result` link to a Nix store path
containing the contents of the OwnTracks Frontend package. To do this
I followed the nix.dev tutorial on [packaging existing
software](https://nix.dev/tutorials/packaging-existing-software).

In the first iteration I created two files with the following
contents.

```nix
# owntracks-frontend.nix
{
  stdenv,
  fetchzip
}:
stdenv.mkDerivation {
  pname = "owntracks-frontend";
  version = "v2.15.3";
  src = fetchzip {
    url = "https://github.com/owntracks/frontend/releases/download/v2.15.3/v2.15.3-dist.zip";
    sha256 = "";
  };
}
```

And,

```nix
# default.nix
let
  pkgs = import <nixpkgs> { config = {}; overlays = []; };
in
{
  owntracks-frontend = pkgs.callPackage ./owntracks-frontend.nix { };
}
```

Then executing `nix-build -A owntracks-frontend` produces the
expected error regarding the incorrect hash.

```
error: hash mismatch in fixed-output derivation '/nix/store/im2lmhh4a2h7x87plz9i1fsc5fw8vhyf-source.drv':
         specified: sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
            got:    sha256-iy+yISPcOD/2lTyJUb1eI3wufLku1mKfVDm0+Dy8OKk=
error: 1 dependencies of derivation '/nix/store/bm08ivlk0nqc61kz6vallfndbq2xn5ly-owntracks-frontend-v2.15.3.drv' failed to build
```

This error gives the correct hash so it can be put into the
derivation.

```nix
  src = fetchzip {
    url = "https://github.com/owntracks/frontend/releases/download/v2.15.3/v2.15.3-dist.zip";
    sha256 = "iy+yISPcOD/2lTyJUb1eI3wufLku1mKfVDm0+Dy8OKk=";
  };
```

Now, Nix will accept the source, and the build proceeds up to the next
error.

```
error: builder for
'/nix/store/csw1kq323p6lipcwbs9q109rf85vbx1n-owntracks-frontend-v2.15.3.drv'
failed to produce output path for output 'out' at 
'/nix/store/csw1kq323p6lipcwbs9q109rf85vbx1n-owntracks-frontend-v2.15.3.drv.chroot/root/nix/store/br9k7nxj067cmza64s5r92f2zchrj5vx-owntracks-frontend-v2.15.3'
```

This means that the derivation is not creating an output directory
which should contain the result. That's because this package isn't a
normal Autotools build. All that really needs to happen, with one
caveat I'll get to, is to copy the files that were downloaded as the
source into the output directory. That can be accomplished by
overriding the install phase as
[described](https://nix.dev/tutorials/packaging-existing-software#installphase)
in the tutorial.

```nix
# owntracks-frontend.nix
{
  stdenv,
  fetchzip
}:
stdenv.mkDerivation {
  pname = "owntracks-frontend";
  version = "v2.15.3";
  src = fetchzip {
    url = "https://github.com/owntracks/frontend/releases/download/v2.15.3/v2.15.3-dist.zip";
    sha256 = "iy+yISPcOD/2lTyJUb1eI3wufLku1mKfVDm0+Dy8OKk=";
  };

  installPhase = ''
    runHook preInstall
    cp -r . $out
    runHook postInstall
  '';
}
```

Now, `nix-build -A owntrack-frontend` is able to succeed, and the
result link points to a Nix store path containing the expected files.

```console
$ nix-build -A owntracks-frontend
this derivation will be built:
  /nix/store/n07d9lsy8g4h8q7b69i51511ddfnqpq7-owntracks-frontend-v2.15.3.drv
building '/nix/store/n07d9lsy8g4h8q7b69i51511ddfnqpq7-owntracks-frontend-v2.15.3.drv'...
Running phase: unpackPhase
unpacking source archive /nix/store/nwca1gys4hl68cnslmiakcjaqkl8v612-source
source root is source
Running phase: patchPhase
Running phase: updateAutotoolsGnuConfigScriptsPhase
Running phase: configurePhase
no configure script, doing nothing
Running phase: buildPhase
no Makefile or custom buildPhase, doing nothing
Running phase: installPhase
Running phase: fixupPhase
shrinking RPATHs of ELF executables and libraries in /nix/store/4z9iardq8amf6f54azfznphy2dbb76fh-owntracks-frontend-v2.15.3
checking for references to /build/ in /nix/store/4z9iardq8amf6f54azfznphy2dbb76fh-owntracks-frontend-v2.15.3...
patching script interpreter paths in /nix/store/4z9iardq8amf6f54azfznphy2dbb76fh-owntracks-frontend-v2.15.3
/nix/store/4z9iardq8amf6f54azfznphy2dbb76fh-owntracks-frontend-v2.15.3

$ ls -lL result
total 60
dr-xr-xr-x 2 root root  4096 Dec 31  1969 assets
dr-xr-xr-x 2 root root  4096 Dec 31  1969 config
-r--r--r-- 1 root root  1150 Dec 31  1969 favicon.ico
-r--r--r-- 1 root root  3647 Dec 31  1969 icon-180x180.png
-r--r--r-- 1 root root   718 Dec 31  1969 index.html
-r--r--r-- 1 root root   377 Dec 31  1969 manifest.json
-r--r--r-- 1 root root 36117 Dec 31  1969 OwnTracks.svg
```

The caveat I mentioned is that the `config` directory needs to include
a `config.js` file to set up the frontend app. As described in the
previous post, for my purposes it needs to contain the following:

```javascript
window.owntracks = window.owntracks || {};
window.owntracks.config = {
  api: {
    baseUrl: "http://wimpy.bleak-moth.ts.net:8083"
  },
  router: {
    basePath: "owntracks"
  }
};
```

This can be accomplished using the `pkgs.writeText` library function
which puts some arbitrary text into a file in the Nix store. That file
can then be referenced later in the derivation. So, I added such an
attribute to the `mkDerivation` call and then, in the install phase,
copied the generated file into the appropriate place in the `$out`
directory. Notice, this entails adding `writeText` to the argument
list of the function.

```nix
# owntracks-frontend.nix
{
  stdenv,
  writeText,
  fetchzip
}:
stdenv.mkDerivation {
  pname = "owntracks-frontend";
  version = "v2.15.3";
  src = fetchzip {
    url = "https://github.com/owntracks/frontend/releases/download/v2.15.3/v2.15.3-dist.zip";
    sha256 = "iy+yISPcOD/2lTyJUb1eI3wufLku1mKfVDm0+Dy8OKk=";
  };

  config = writeText "config.js" ''
    window.owntracks = window.owntracks || {};
    window.owntracks.config = {
      api: {
        baseUrl: "http://wimpy.bleak-moth.ts.net:8083"
      },
      router: {
        basePath: "owntracks"
      }
    };
  '';

  installPhase = ''
    runHook preInstall
    cp -r . $out
    cp $config $out/config/config.js
    runHook postInstall
  '';
}
```

Rebuilding the package and checking its contents shows the `config.js`
file is present and has the right content.

```console
$ nix-build -A owntracks-frontend
these 2 derivations will be built:
  /nix/store/dacc8ma93fl60qvp359nqb0b9liv5v57-config.js.drv
  /nix/store/adpvald53kxzhcfmm840xdvfydbn88yw-owntracks-frontend-v2.15.3.drv
.
.
.

/nix/store/dbml7xvlqv2lgcjfb3s0y17m5nj9bdmi-owntracks-frontend-v2.15.3

$ cat result/config/config.js 
window.owntracks = window.owntracks || {};
window.owntracks.config = {
  api: {
    baseUrl: "http://wimpy.bleak-moth.ts.net:8083"
  },
  router: {
    basePath: "owntracks"
  }
};
```

## Making Use of the Derivation

At this point I'm able to build a directory in the Nix store which
contains the SPA that I want to serve with Nginx. If done manually
this would involve updating the Nginx configuration with a *location*
block pointing to the path in the Nix store. Obviously, I want to
accomplish this declaratively through `configuration.nix` in my NixOS
server. 

I wasn't immediately sure how to go about this. I knew that I could
refer to derivations in `pkgs` using string interpolation and get the
path to a package in the Nix store. I knew Nix would make sure the
package was present in the store and build or download it if
necessary.  So if a `pkgs.owntracks-frontend` existed, I could do
something like this:

```nix
  services.nginx = {
      enable = true;
      virtualHosts."wimpy" = {
        root = "/var/www/html";
        locations."/owntracks/" = {
          alias = "${pkgs.owntracks-frontend}/";
        };
      };
    };
```

Obviously, there is no `pkgs.owntracks-fronted`. But, I do now have
`owntracks-frontend.nix` which contains a function that will produce
the same kind of derivation as those in `pkgs` if invoked correctly. I
reasoned that that is what `default.nix` is doing with the
`pkgs.callPackage` invocation, and so maybe I could just do the same
thing in my `configuration.nix`.

I copied `owntracks-frontend.nix` to be next to `configuration.nix` in
my NixOS config repo and updated the latter with the following:

```nix
  services.nginx =
    let
      owntracks-frontend = pkgs.callPackage ./owntracks-frontend.nix { };
    in {
      enable = true;
      virtualHosts."wimpy" = {
        root = "/var/www/html";
        locations."/owntracks/" = {
          alias = "${owntracks-frontend}/";
        };
      };
    };
```

And, it worked!

## Final Thoughts

I feel pretty happy with this accomplishment. It was really pretty
simple, but I feel like I'm starting to get an inkling of how things
in NixOS work.

One improvement that could be made, I think, is parameterizing the
values in the `config.js` file. Right now the `/owntracks/` base path
is duplicated in the Nginx config and `config.js`. And surfacing the base URL
for the API in the `configuration.nix` would also make more
sense. Presumably, this could be accomplished by passing the values as
parameters to the function in `owntracks-frontend.nix`. But I'll save
that for later.
