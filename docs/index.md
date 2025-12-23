# tdom-path

Easily rewrite the static asset paths in your tdom-based markup. Works great for static-site generators.


```{include} ../README.md
:start-after: "## Installation"
:end-before: "## <!-- README-only --> Path Syntax Reference"
```

## Path Rewriting Lifecycle

The complete lifecycle from component to rendered HTML:

```mermaid
flowchart TD
    A[Component with Asset References] --> B[make_path_nodes]
    B --> C[Tree with Traversable Instances]
    C --> D[render_path_nodes]
    D --> E[Tree with Relative Path Strings]
    E --> F[HTML Output]

    style A fill:#e1f5ff
    style C fill:#fff4e1
    style E fill:#e7f5e1
    style F fill:#ffe1e1
```

## Function Relationships

How data flows between the three core functions:

```mermaid
flowchart LR
    subgraph Input
        STR[String Paths<br/>static/styles.css]
    end

    subgraph Phase1[Phase 1: Path Resolution]
        MP[make_path]
        STR --> MP
        MP --> TRAV[Traversable Instance]
    end

    subgraph Phase2[Phase 2: Tree Transformation]
        MPN[make_path_nodes]
        TREE1[VDOM Tree<br/>with String Paths] --> MPN
        MPN --> TREE2[VDOM Tree<br/>with Traversable]
        TRAV -.used by.-> MPN
    end

    subgraph Phase3[Phase 3: Path Rendering]
        RPN[render_path_nodes]
        TREE2 --> RPN
        TARGET[Target Path<br/>pages/about.html] --> RPN
        RPN --> TREE3[VDOM Tree<br/>with Relative Paths]
    end

    subgraph Output
        TREE3 --> HTML[HTML String<br/>../static/styles.css]
    end

    style STR fill:#e1f5ff
    style TRAV fill:#fff4e1
    style TREE2 fill:#fff4e1
    style TREE3 fill:#e7f5e1
    style HTML fill:#ffe1e1
```

```{toctree}
:maxdepth: 2
:hidden:

guides/index
reference/index
```

## Next Steps

- Read [Core Concepts](guides/core-concepts.md) to understand the architecture
- Explore [Cookbook Patterns](guides/cookbook.md) for common use cases
- Check [API Reference](reference/api-reference.md) for detailed function documentation
- Learn about [Advanced Usage](guides/advanced.md) for custom strategies and extensions
