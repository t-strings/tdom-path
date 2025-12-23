# Performance Benchmarks

`tdom-path` is highly optimized for real-world usage, particularly Static Site Generation (SSG) workflows where components are reused across multiple pages. The library uses LRU caching for module loading, providing **17.9x speedup** for cached accesses.

## Quick Benchmark

```bash
# Run standalone performance benchmark
just benchmark

# Run pytest-based performance tests
just test -m slow
```

## Real-World Performance Results

Based on benchmarks simulating typical SSG workflows (120+ component tree, multiple pages):

| Operation | Cold Cache | Warm Cache | Speedup |
|-----------|------------|------------|---------|
| `make_path()` - module access | 25.8μs | 1.4μs | **17.9x faster** |
| `make_path()` - package path | ~25μs | 1.3μs | **19x faster** |
| `make_path_nodes()` - tree transform | 758μs | 758μs | (no change) |
| `render_path_nodes()` - per page | 684μs | 684μs | (no change) |

**Cache Impact:** **1688% faster (17.9x)** with warm cache ✓ EXCELLENT

## Why This Matters

**SSG Scenario:** Building 100 pages with the same component:
- **Without cache:** 100 × 25μs = 2,500μs = 2.5ms
- **With cache:** 1 × 25μs + 99 × 1.4μs = 164μs = 0.16ms
- **Savings:** **94% faster** (2.34ms saved)

For sites with 1000+ pages, the savings are even more dramatic.

## Performance Characteristics

**Excellent:**
- Path resolution (cached): 1.4μs ✓ EXCELLENT
- Module loading optimization: 17.9x speedup ✓ EXCELLENT

**Good:**
- Tree traversal: ~450μs for 120+ components ✓ GOOD
- Multi-page rendering: 684μs/page ✓ GOOD

## How the Cache Works

The library uses `@lru_cache(maxsize=128)` for module loading via `importlib.resources.files()`:

```python
from functools import lru_cache
from importlib.resources import files
from tdom_path.webpath import Traversable

@lru_cache(maxsize=128)
def _get_module_files(module_name: str) -> Traversable:
    """Cache Traversable roots to avoid repeated module loading."""
    return files(module_name)
```

**First access (cold cache):**
- Loads module metadata: ~20μs
- Sets up resource reader: ~5μs
- **Total: ~25μs**

**Subsequent accesses (warm cache):**
- Dictionary lookup: ~1.4μs
- **Total: ~1.4μs**

**Cache benefits:**
- Zero overhead on first use
- Massive speedup on repeated use
- Automatic cleanup (LRU eviction)
- Thread-safe (Python's LRU cache is lock-based)

## Running Benchmarks

### Standalone Benchmark

```bash
just benchmark
```

This runs a comprehensive benchmark suite that measures:
- Cold vs warm cache performance
- SSG workflow simulation (multi-page rendering)
- Clear performance analysis with thresholds
- Real-world usage patterns

### Pytest-Based Tests

```bash
# Run performance tests
just test -m slow

# Run with free-threaded Python (regression detection)
just test-freethreaded -m slow

# Run with parallel execution (8 threads, 10 iterations)
just test-freethreaded -m slow --threads=8 --iterations=10
```

## Benchmark Infrastructure

The test infrastructure uses:

- **pytest-benchmark** for standardized timing
- **tracemalloc** for memory profiling
- **Realistic test data** (100+ component trees)
- **Free-threaded Python compatibility**
- **Baseline metrics documented in tests**

## Free-threaded Python Testing

The library is tested with Python's free-threaded mode (GIL-less Python) to ensure:

- No threading regressions
- Thread-safe cache operations
- Consistent performance across Python versions

```bash
just test-freethreaded -m slow
```

## Performance Optimization Tips

1. **Reuse components** - Same component across pages = cache hits
2. **Build incrementally** - Keep Python process alive between builds
3. **Use package paths** - Already optimized with cache
4. **Profile your workflow** - Use `just benchmark` to measure your patterns
5. **Monitor cache** - Check `_get_module_files.cache_info()` for hit/miss ratio

The library is designed for the common case: building multiple pages with shared components. The LRU cache ensures this workflow is extremely fast.

## Profiling Tools

The library includes standalone profiling tools for performance analysis:

```bash
# Run comprehensive benchmark suite
just benchmark

# Profile specific operations
uv run python -m tdom_path.profiling.benchmark
```

**Benchmark features:**
- Cold vs warm cache comparison
- SSG workflow simulation (multi-page rendering)
- Clear performance analysis with thresholds
- Real-world usage patterns

## Optimization Details

**What was optimized:**
- Module loading via `importlib.resources.files()` (80% of transformation time)
- Added LRU cache for Traversable module roots
- One-line change at call sites

**What wasn't optimized (and why):**
- Tree traversal - already efficient (~2μs per node)
- Path calculations - necessary operations
- isinstance() checks - highly optimized in CPython

## Memory Usage

- **LRU cache:** ~128 entries × ~1KB = ~128KB max
- **Per operation:** Minimal overhead (~10-50KB)
- **Tree operations:** Linear with tree size (~1-5MB for 100+ components)

## When to Expect Peak Performance

**Best case (warm cache):**
- SSG workflows (reusing components)
- Long-running servers (modules stay loaded)
- Component libraries (shared across pages)
- Development with hot reload (cache persists)

**First-time use (cold cache):**
- Initial page build
- Fresh Python process
- New module references
- Still fast (25μs), just not cached

## Monitoring Cache Performance

You can monitor cache statistics to understand hit rates:

```python
from tdom_path.webpath import _get_module_files

# Check cache info
info = _get_module_files.cache_info()
print(f"Cache hits: {info.hits}")
print(f"Cache misses: {info.misses}")
print(f"Hit rate: {info.hits / (info.hits + info.misses):.1%}")
```

## Performance Thresholds

The library targets these performance thresholds:

| Operation | Target | Status |
|-----------|--------|--------|
| Path resolution (warm) | < 2μs | ✅ 1.4μs |
| Tree transformation | < 1ms | ✅ 758μs |
| Page rendering | < 1ms | ✅ 684μs |
| Memory overhead | < 1MB | ✅ 128KB |

## Conclusion

`tdom-path` is optimized for the common SSG use case: building multiple pages with shared components. The LRU cache provides massive speedups for repeated operations, making it ideal for:

- Static site generators
- Component libraries
- Reusable web components
- Framework-agnostic asset management

The library achieves **17.9x speedup** with warm cache while maintaining simple, clean APIs.
