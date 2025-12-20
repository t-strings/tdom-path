# Core Path API - Raw Idea

## Feature Description

Implement `PurePath`-compatible path classes that represent component-relative paths, support basic path operations (join, resolve, relative), and provide type hints for IDE integration. Include unit tests covering path arithmetic, edge cases, and cross-platform compatibility.

## Phase Information

This is Phase 1 from the product roadmap.

## Context

- This is part of the `tdom-path` library which rewrites paths (static assets, links) in a `Node` to be relative to a target
- The goal is to provide great DX via actual paths that work with IDE tooling (autocomplete, refactoring, squiggles)
- Must be framework-portable (not tied to Flask, Django, etc.)
- Should use PurePath interface for tooling compatibility
- Needs to support both dynamic servers and SSG (static site generators)

## Key Requirements

- `PurePath`-compatible path classes
- Component-relative path representation
- Basic path operations: join, resolve, relative
- Type hints for IDE integration
- Unit tests covering:
  - Path arithmetic
  - Edge cases
  - Cross-platform compatibility
