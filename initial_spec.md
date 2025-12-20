tl;dr A library that rewrites paths (static assets, links) in a `Node` to be relative to a target.

## Problem

My theming work involves static assets that live in a directory as part of a component (layout, view, regular
component.) Since my themes are intended to be framework-portable, I don't have access to all the helper functions (
Jinja/Flask, Django, etc.) that you put in their interpolations. Plus, their approaches don't match the tooling-oriented
DX we are looking for.

## Proposal Overview

Let's start a package and a spec called `tdom-path` which tackles this. We also use it to incept what's needed in `tdom`
itself for middleware-like utilities.

This effort is crucial to fulfill the `tdom` vision of "Big ecosystem of quality, interoperable themes, components, and
tooling."

## Scenario

Let's say I'm in `src/storyville/components/header/`. My logic/template is in `header.py` as `Header`. But it has some
CSS and an image. Where do I put these files?

Then, later, when rendering, how do we calculate the correct `href` path? If I is an SSG (or there is some system that
prepares static assets), how do I provide these files to a build step?

## Goals

In some order of importance...a laundry list, but all things I've tackled at some point in the last 7 years.

## Great DX via actual paths

Ideally, the static assets for `Header` would be in `header/static/style.css` for example. Header's t-string would
include `<link rel="stylesheet" href="./static/styles.css">`. This is great for several reasons:

- Assets are local to the component, not over in some other garbage barge global `static` directory
- Smart editors can autocomplete the path reference, as it points to an actual path on disk
- Equally: squiggle if you got the path wrong
- Refactorings (e.g. file rename) could find all usages and fix
- Other static analysis tools could do things such as this, but possibly more

## Portable

The moment we start writing `url_for('static', filename="styles.css")`, we lose the "big ecosystem" vision. We also lose
what was just described: unless your editor/tooling is taught that specific frameworks syntax/meaning, you'll get no
tooling support.

We could partially solve this by having some standard callable in a SOA (service oriented architecture) that called into
per-framework implementation. But while that might be a fallback choice, we likely will lose other goals. Most of those
were created before the days of Python tooling.

## Locality

Having asset files local to the component fulfills a number of goals.

## Dynamic and SSG

We have approaches for this now in Django and Flask (dynamic), in Sphinx and Pelican (static), etc. Ideally we come up
with a solution that works in either case (that likely means generating relative paths.)

## Part of a build system

This system should anticipate (though perhaps not solve) all the parts of the build process:

- Definition time when the template is first rendered (or even parsed)
- Application time, when the component is used as part of a render at a URL
- Build time, when an SSG (or static prep system) is optimizing static assets and writing to output directory

## Good error messages

This is a very fiddly part of doing web development. Lots of magic, lots of mystery. We now have new powers, mainly
through static analysis tooling and t-strings as an in-language feature. What new approaches can we do, beyond "pretty
tracebacks"?

## Optimized performance

Other systems take trips from string to parse then back to string, multiple times (e.g. WSGI middleware.) We are
building a middleware ecosystem that anticipates handing around `Node`. That's already a win.

But we can go further. Can we collect component path information as part of the `Node` structure? Even crazier, could we
put a closure in the parse representation that had the data needed for path-on-disk?

Can we collect information to make the build output generation part super-optimized?

## Other paths

We are focused on paths for static assets. But we also have `<a href>` links to other resources. Perhaps in the header
nav of a component. But perhaps in the body of a Markdown document. We'd like those to also be re-written. Even better,
some systems (Sphinx) know when a target doesn't exist and you can emit a warning. Those systems should be able to plug
into link generation to warn/fail early.

## Site prefix

For SSGs, the build directory on disk might be deployed to the hosted site under a static prefix. We should anticipate
that. (If we use relative paths everywhere, that isn't a problem.)

## Convention over configuration

This is popular but I'm not a fan, as "convention" is a romance word for "impossible to static analyze". 😉 Perhaps we
should make it possible to "just drop in a folder named static" but that should be a layer over a declarative,
tooling-friendly system.

## Pluggable

There might be better implementations. Or, people might prefer their battle-tested. If we design this as SOA with a
`Protocol` or something, we could allow alternate implementations to be "registered."

## Analysis

Let's look at how we might do this. We might first start with a survey of a bunch of systems, collecting common patterns
and needs.

## `tdom` context object

I've implemented some feature-complete versions of this, starting perhaps in 2019. Recently I implemented this on a
`tdom` branch for context objects: `html(t'<link href="static/styles.css">', context=this_context)`:

- This context was passed down through the rendering
- Components could optionally ask for it
- The component rendering lifecycle would look inside for custom factories, e.g. my old Hopscotch DI system
- I could also register middleware that would run before/after

This worked really well, but surfaced a number of issues:

- What is the type information of `context` if it is custom?
- Should there be well-known plug points?
- Stated differently, should we define a minimum rendering lifecycle?

## Component information

This was my biggest problem. Once a component renders to a `Node`, I no longer have information about its path on disk.
I can't then resolve file paths to `static/styles.css`. We could define an `annotations` on `Node` where "the system"
could stash data. But perhaps `TNode` and parse time could do it. Perhaps even with a callable closure to make it
flexible.

## PurePath

My older system leaned heavily on `PurePath` which is mainly known through the Posix implementations. But it doesn't
have to. What if we used the interface of `PurePath` but backed with our own concept of a tree? (That's what my thing
did.) We then type into tons of tooling and expectations if `static/styles.css` is a variant of `PurePath`.

## Two-layer and free threaded

My latest effort was a `ChainMap` with the system context as an immutable and the per-render as a writable that gets
reset. It would be nice though if we made decisions that were free-threaded friendly. Can we make a render "bag of data"
concurrent?

## Route-based dynamic servers

When resolving to a path, what does this mean for Django/Flask/FastAPI who define static assets at routes?