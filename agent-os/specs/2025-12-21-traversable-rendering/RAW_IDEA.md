# PurePosixPath Rendering - Raw Idea

## Feature Description

Write a function that is given a node tree and a `target: PurePath`. The function walks the tree looking for `PurePosixPathElement` and rewrites the value into an `Element` with a path relative to the target. Support rendering strategies: relative path (default) or custom resolver. Re-use current walking/rewriting logic (and refactor helpers as needed. Test with trees containing PurePosixPaths.

## Key Requirements

- Accept a node tree and target PurePath
- Walk tree looking for PurePosixPathElement instances
- Rewrite values into Elements with paths relative to target
- Support rendering strategies:
  - Relative path (default)
  - Custom resolver
- Re-use existing walking/rewriting logic
- Refactor helpers as needed
- Test with trees containing PurePosixPaths
