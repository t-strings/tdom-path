# Guides

Comprehensive guides for using tdom-path in your projects.

## Core Documentation

```{toctree}
:maxdepth: 2

core-concepts
cookbook
advanced
performance
```

## Overview

tdom-path provides a clean API for resolving component assets in web applications:

1. **Path Resolution** (`make_path`) - Convert asset strings to Traversable instances
2. **Tree Transformation** (`make_path_nodes`) - Automatically rewrite VDOM trees
3. **Path Rendering** (`render_path_nodes`) - Convert to relative path strings

## Quick Navigation

### For New Users

1. Start with [Core Concepts](core-concepts.md) to understand the architecture
2. Review [Cookbook Patterns](cookbook.md) for practical examples

### For Experienced Users

1. Explore [Advanced Usage](advanced.md) for custom strategies
2. Review [Performance](performance.md) for optimization techniques
3. Implement custom RenderStrategy for your use case

## Key Features

- **Package Asset Support** - Reference assets from installed packages
- **Relative Path Rendering** - Calculate relative paths for HTML output
- **Framework Independence** - Same components work everywhere
- **Type Safety** - Comprehensive type hints with IDE support
- **Asset Validation** - Fail-fast validation with clear error messages
- **SSG Integration** - Asset collection for static site generators

## Next Steps

Choose a guide based on your needs:

- New to tdom-path? Start with [Core Concepts](core-concepts.md)
- Building components? See [Cookbook Patterns](cookbook.md)
- Need advanced features? Review [Advanced Usage](advanced.md)
- Optimizing performance? See [Performance](performance.md)
