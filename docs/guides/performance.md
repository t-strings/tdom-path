# Performance Benchmarks

:::{include} ../../README.md
:start-after: "## Performance Benchmarks"
:end-before: "### Running Benchmarks"
:::

## Running Benchmarks

```bash
# Run all performance benchmarks
just test -m slow

# Run with free-threaded Python for threading regression detection
just test-freethreaded -m slow

# Run with parallel execution (8 threads, 10 iterations)
just test-freethreaded -m slow --threads=8 --iterations=10
```

## Benchmark Results

:::{include} ../../README.md
:start-after: "### Benchmark Results"
:end-before: "### Performance Characteristics"
:::

## Performance Characteristics

:::{include} ../../README.md
:start-after: "### Performance Characteristics"
:end-before: "### Benchmark Infrastructure"
:::

## Benchmark Infrastructure

:::{include} ../../README.md
:start-after: "### Benchmark Infrastructure"
:end-before: "### Free-threaded Python Testing"
:::

## Free-threaded Python Testing

:::{include} ../../README.md
:start-after: "### Free-threaded Python Testing"
:end-before: "### Performance Optimization Tips"
:::

## Performance Optimization Tips

:::{include} ../../README.md
:start-after: "### Performance Optimization Tips"
:end-before: "The benchmark suite provides"
:::
