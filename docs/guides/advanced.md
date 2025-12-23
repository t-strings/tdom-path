# Advanced Usage

This guide covers advanced usage patterns and complex scenarios for tdom-path.

## Custom Rendering Strategies

While tdom-path provides `RelativePathStrategy` for relative path rendering, you can implement custom strategies:

```python
>>> from pathlib import PurePosixPath
>>> from importlib.resources.abc import Traversable
>>> from tdom_path.tree import RenderStrategy
>>> class CDNStrategy:
...     """Render all paths as CDN URLs."""
...
...     def __init__(self, cdn_base_url: str):
...         self.cdn_base_url = cdn_base_url.rstrip('/')
...
...     def calculate_path(self, source: Traversable, target: PurePosixPath) -> str:
...         # Get the resource path relative to package
...         resource_path = str(source).replace('/', ':')
...         return f"{self.cdn_base_url}/{resource_path}"
>>> # Usage
>>> strategy = CDNStrategy("https://cdn.example.com/assets")
>>> rendered = render_path_nodes(path_tree, target, strategy=strategy)  # doctest: +SKIP
```

## Complex Tree Transformations

For advanced tree transformations, you can create custom tree walking functions:

```python
>>> from tdom_path.tree import _walk_tree
>>> def custom_transform(node):
...     """Custom transformation function for _walk_tree."""
...     if hasattr(node, 'attrs') and 'href' in node.attrs:
...         # Custom logic for href attributes
...         href = node.attrs['href']
...         if href.startswith('static/'):
...             node.attrs['href'] = f"/assets/{href}"
...     return node
>>> # Apply custom transformation
>>> transformed_tree = _walk_tree(original_tree, custom_transform)  # doctest: +SKIP
```

## Performance Optimization Patterns

### Caching Traversable Instances

```python
>>> from functools import lru_cache
>>> from tdom_path import make_path
>>> @lru_cache(maxsize=128)
... def cached_make_path(component, asset_path):
...     return make_path(component, asset_path)
>>> # Usage
>>> from mysite.components.heading import Heading
>>> css_path = cached_make_path(Heading, "static/styles.css")
```

### Batch Processing

```python
>>> def batch_process_components(components, asset_paths):
...     """Process multiple components and asset paths efficiently."""
...     results = {}
...     for component, asset_path in zip(components, asset_paths):
...         results[(component, asset_path)] = make_path(component, asset_path)
...     return results
```

## Integration with Build Systems

### Static Site Generation

```python
>>> from pathlib import PurePosixPath
>>> from tdom_path import make_path_nodes, render_path_nodes
>>> def generate_static_page(component, template, output_path):
...     """Generate a static HTML page with optimized asset paths."""
...     # Create tree from template
...     tree = make_path_nodes(template, component)
...
...     # Render with target path
...     target = PurePosixPath(output_path)
...     rendered = render_path_nodes(tree, target)
...
...     # Save to file
...     with open(output_path, 'w') as f:
...         f.write(str(rendered))
```

### Asset Collection for Build Tools

```python
>>> from tdom_path.tree import AssetReference, _walk_tree
>>> from pathlib import PurePosixPath
>>> def collect_assets(tree, component):
...     """Collect all asset references for build tool processing."""
...     assets = set()
...
...     def collect_fn(node):
...         if hasattr(node, 'attrs'):
...             for attr_name, attr_value in node.attrs.items():
...                 if isinstance(attr_value, Traversable):
...                     module_path = PurePosixPath(str(attr_value))
...                     ref = AssetReference(source=attr_value, module_path=module_path)
...                     assets.add(ref)
...         return node
...
...     _walk_tree(tree, collect_fn)
...     return assets
```

## Debugging and Troubleshooting

### Asset Validation

```python
>>> from tdom_path import make_path
>>> def validate_all_assets(component, asset_paths):
...     """Validate that all assets exist before deployment."""
...     missing_assets = []
...     for asset_path in asset_paths:
...         try:
...             path = make_path(component, asset_path)
...             if not path.is_file():
...                 missing_assets.append(asset_path)
...         except Exception as e:
...             missing_assets.append(f"{asset_path} ({str(e)})")
...
...     if missing_assets:
...         raise FileNotFoundError(f"Missing assets: {', '.join(missing_assets)}")
```

### Performance Profiling

```python
>>> import cProfile
>>> from tdom_path import make_path_nodes
>>> def profile_tree_transformation(tree, component):
...     """Profile tree transformation performance."""
...     profiler = cProfile.Profile()
...     result = profiler.runcall(make_path_nodes, tree, component)
...     profiler.print_stats(sort='cumulative')
...     return result
```

These advanced patterns demonstrate how to extend tdom-path for complex use cases while maintaining performance and flexibility.
