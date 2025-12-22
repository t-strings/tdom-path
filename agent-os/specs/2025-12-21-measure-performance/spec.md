# Specification: Measure Performance

## Goal
Establish performance measurement infrastructure for tdom-path library operations to track execution time, memory usage, and tree traversal overhead, with baseline metrics and free-threaded regression detection.

## User Stories
- As a developer, I want to measure key path operation performance so that I can detect regressions before they impact production
- As a maintainer, I want to benchmark tree traversal with hundreds of components so that I understand scaling behavior and identify bottlenecks

## Specific Requirements

**Performance Test Infrastructure**
- Add pytest-benchmark to development dependencies in pyproject.toml
- Create new test file tests/test_performance.py for all performance tests
- Mark all performance tests with @pytest.mark.slow to separate from normal test runs
- Use existing "just test" command with marker filtering for execution
- Tests should use pytest-benchmark fixture following Storyville's simple timing approach

**Key Operation Benchmarks**
- Measure make_path() execution time for module-relative path resolution
- Measure make_path_nodes() execution time for tree rewriting operations
- Measure render_path_nodes() execution time for relative path rendering
- Measure tree traversal overhead using _walk_tree() internal function
- Each benchmark should use the benchmark fixture to wrap the operation under test

**Test Data Generation**
- Create fixture that generates test trees with hundreds of components (minimum 100)
- Include components with static assets (CSS, JS files) in test data
- Generate nested component structures to test realistic hierarchies
- Use Element and Fragment from tdom to build representative DOM trees
- Include link and script tags with href/src attributes pointing to static assets

**Memory Usage Tracking**
- Track memory usage for make_path() operations with many components
- Track memory usage for make_path_nodes() tree rewriting with large trees
- Track memory usage for render_path_nodes() relative path conversion
- Use simple memory profiling approach without external profiling tools

**Baseline Metrics Establishment**
- Run initial performance tests to establish baseline execution times
- Document baseline metrics in test output as reference points
- Store baseline context in test comments or docstrings
- No automated comparison or CI integration in initial implementation

**Free-threaded Python Considerations**
- Add note in test docstrings about free-threaded regression testing
- Document that performance tests should be run with free-threaded Python builds
- Include reference to pytest-freethreaded plugin already in dependencies
- Tests should be compatible with "just test-freethreaded" command for parallel execution

**Console Output Format**
- Use pytest-benchmark's default console table output
- Display statistics including min, max, mean, stddev for each benchmark
- Show operations per second (ops/sec) for throughput metrics
- No JSON, CSV, or other export formats required

**Integration with Existing Test Suite**
- Performance tests integrate with existing pytest configuration
- Use existing pytest markers infrastructure from pyproject.toml
- Tests should work with "just test -m slow" to run only performance tests
- Tests should be skipped by default with "just test" (using "-m not slow")

## Visual Design
No visual assets provided.

## Existing Code to Leverage

**Storyville test_examples.py benchmark pattern**
- Use simple benchmark(function, *args) pattern from test_huge_build_performance
- Pass function reference and arguments to benchmark fixture
- Let pytest-benchmark handle timing automatically without explicit validation
- Keep benchmarks focused on timing, not functional assertions

**Storyville pyproject.toml pytest-benchmark dependency**
- Add "pytest-benchmark>=4.0.0" to dev dependency group
- Follow same version pattern as Storyville for consistency
- No additional benchmark configuration needed in pytest.ini_options

**Existing tree.py tree traversal functions**
- Use _walk_tree() to measure tree traversal overhead
- Use make_path_nodes() with realistic component trees
- Use render_path_nodes() with RelativePathStrategy for rendering benchmarks
- Leverage existing AssetReference and _TraversableWithPath for asset handling

**Existing test fixtures and patterns**
- Use Heading component from mysite.components.heading as test component
- Use make_path() to create asset references in test data
- Follow existing test structure from test_tree.py and test_asset_collection.py
- Use Element, Fragment, html from tdom for DOM construction

**Existing pytest marker infrastructure**
- Use @pytest.mark.slow decorator following Storyville pattern
- Leverage existing markers configuration in pyproject.toml
- Follow "-m not slow" default behavior from Storyville's addopts

## Out of Scope
- New Justfile commands for running performance tests
- Export formats for results (JSON, CSV, etc.)
- Advanced profiling tools beyond simple timing measurements
- Automated performance regression detection in CI
- Performance comparison against previous commits
- Historical performance tracking or trend analysis
- Integration with external monitoring or alerting systems
- Performance optimization implementation (only measurement)
- Detailed flame graphs or call stack profiling
- Database or persistent storage of benchmark results
