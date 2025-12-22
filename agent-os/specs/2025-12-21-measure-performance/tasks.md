# Task Breakdown: Measure Performance

## Overview
Total Tasks: 31 sub-tasks across 4 major task groups

## Task List

### Infrastructure Setup

#### Task Group 1: Performance Testing Infrastructure
**Dependencies:** None

- [x] 1.0 Complete performance testing infrastructure
  - [x] 1.1 Add pytest-benchmark to development dependencies
    - Add "pytest-benchmark>=4.0.0" to dev dependency group in pyproject.toml
    - Follow Storyville's version pattern for consistency
    - Run `just install` to update dependencies
  - [x] 1.2 Add slow marker configuration to pytest
    - Add pytest marker configuration in pyproject.toml [tool.pytest.ini_options]
    - Define markers = ["slow: marks tests as slow (deselect with '-m \"not slow\"')"]
    - Update addopts to include '-m "not slow"' to skip slow tests by default
    - Follow Storyville's marker pattern for consistency
  - [x] 1.3 Create tests/test_performance.py file
    - Create new test file with module-level docstring explaining purpose
    - Add imports: pytest, tdom, tdom_path functions (make_path, make_path_nodes, render_path_nodes)
    - Import tree module internals (_walk_tree) for traversal benchmarks
    - Add placeholder comment for test fixtures to be implemented in next task group
  - [x] 1.4 Verify infrastructure setup
    - Run `just test -m slow` to confirm marker filtering works (should run 0 tests initially)
    - Run `just test` to confirm slow tests are skipped by default
    - Verify pytest-benchmark is available with `uv run pytest --help | grep benchmark`

**Acceptance Criteria:**
- pytest-benchmark>=4.0.0 added to pyproject.toml dev dependencies
- Slow marker configured in pytest.ini_options with default skip behavior
- tests/test_performance.py file created with proper imports
- Marker filtering works correctly (slow tests skipped by default, runnable with -m slow)

### Test Data Generation

#### Task Group 2: Performance Test Fixtures and Data Generation
**Dependencies:** Task Group 1

- [x] 2.0 Complete test data generation fixtures
  - [x] 2.1 Write 2-3 focused tests for fixture validation
    - Test that large_component_tree fixture generates at least 100 components
    - Test that large_component_tree includes both link and script elements
    - Test that generated tree has nested structure (multiple levels deep)
  - [x] 2.2 Create large_component_tree fixture
    - Generate tree with 100+ components using Element and Fragment from tdom
    - Include nested component structures (at least 3-4 levels deep)
    - Add link elements with href="static/styles.css" attributes
    - Add script elements with src="static/app.js" attributes
    - Mix of components with and without assets to simulate realistic pages
    - Use html() helper for readability where appropriate
  - [x] 2.3 Create component_with_assets fixture
    - Create single component with multiple asset references
    - Include 2-3 link tags with different CSS files
    - Include 1-2 script tags with different JS files
    - Use make_path() to create proper asset references
    - Reuse pattern from test_tree.py for consistency
  - [x] 2.4 Create path_tree_fixture for render benchmarks
    - Use large_component_tree fixture as input
    - Apply make_path_nodes() transformation to create TraversableElement nodes
    - Return tree with Traversable attributes ready for rendering
    - Use Heading component as reference component for paths
  - [x] 2.5 Ensure fixture tests pass
    - Run ONLY the 2-3 tests written in 2.1
    - Verify fixtures generate correct data structures
    - Confirm tree sizes meet minimum requirements (100+ components)
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-3 tests written in 2.1 pass
- large_component_tree fixture generates 100+ components with nested structure
- Fixtures include both link and script elements with asset paths
- path_tree_fixture returns tree with TraversableElement nodes

### Core Benchmarks

#### Task Group 3: Key Operation Benchmarks
**Dependencies:** Task Group 2

- [x] 3.0 Complete key operation benchmarks
  - [x] 3.1 Write 2-4 focused tests for benchmark validation
    - Test that make_path benchmark executes without errors
    - Test that make_path_nodes benchmark handles large trees
    - Test that render_path_nodes benchmark produces valid output
    - Test that _walk_tree benchmark completes for large trees
  - [x] 3.2 Implement make_path() execution time benchmark
    - Mark with @pytest.mark.slow decorator
    - Use benchmark fixture with pattern: benchmark(make_path, Heading, "static/styles.css")
    - Test module-relative path resolution performance
    - Add docstring explaining what operation is being measured
    - Reference Storyville's simple timing approach (no assertions needed)
  - [x] 3.3 Implement make_path_nodes() execution time benchmark
    - Mark with @pytest.mark.slow decorator
    - Use large_component_tree fixture as input
    - Benchmark with pattern: benchmark(make_path_nodes, tree, Heading)
    - Measure tree rewriting operations with 100+ components
    - Add docstring explaining tree transformation overhead
  - [x] 3.4 Implement render_path_nodes() execution time benchmark
    - Mark with @pytest.mark.slow decorator
    - Use path_tree_fixture as input (pre-transformed tree)
    - Create target path: PurePosixPath("mysite/pages/index.html")
    - Benchmark with pattern: benchmark(render_path_nodes, path_tree, target)
    - Measure relative path rendering performance
    - Add docstring explaining rendering overhead
  - [x] 3.5 Implement _walk_tree() traversal overhead benchmark
    - Mark with @pytest.mark.slow decorator
    - Use large_component_tree fixture as input
    - Create identity transform function: lambda node: node
    - Benchmark with pattern: benchmark(_walk_tree, tree, identity_fn)
    - Measure pure tree traversal without transformations
    - Add docstring explaining traversal overhead measurement
  - [x] 3.6 Add memory usage tracking for make_path()
    - Use tracemalloc module for simple memory profiling
    - Capture memory before and after make_path() call
    - Report peak memory usage in test output
    - Keep implementation simple (no external profiling tools)
    - Add comment explaining memory measurement approach
  - [x] 3.7 Add memory usage tracking for make_path_nodes()
    - Use tracemalloc for memory profiling
    - Measure memory for large tree transformations (100+ components)
    - Report peak memory usage and memory delta
    - Compare memory usage with and without tree transformations
    - Document memory overhead in test docstring
  - [x] 3.8 Add memory usage tracking for render_path_nodes()
    - Use tracemalloc for memory profiling
    - Measure memory for relative path conversion
    - Report peak memory usage for rendering operations
    - Track memory differences between input and output trees
    - Add baseline context in test docstring
  - [x] 3.9 Ensure benchmark tests pass
    - Run ONLY the tests written in 3.1 and benchmark tests from 3.2-3.8
    - Verify benchmarks execute and produce timing output
    - Confirm pytest-benchmark displays statistics table
    - Check that memory tracking tests report memory usage
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-4 tests written in 3.1 pass
- All benchmark tests marked with @pytest.mark.slow
- Benchmarks use pytest-benchmark fixture following Storyville pattern
- Memory usage tracking implemented with tracemalloc
- Benchmarks display min, max, mean, stddev statistics
- All 4 key operations benchmarked: make_path(), make_path_nodes(), render_path_nodes(), _walk_tree()

### Documentation and Integration

#### Task Group 4: Baseline Metrics, Free-threaded Notes, and Integration
**Dependencies:** Task Group 3

- [ ] 4.0 Complete baseline metrics and documentation
  - [ ] 4.1 Write 1-2 focused tests for integration validation
    - Test that slow marker filtering works correctly (slow tests run with -m slow)
    - Test that performance tests integrate with existing pytest configuration
  - [ ] 4.2 Run initial performance tests to establish baselines
    - Execute `just test -m slow` to run all performance benchmarks
    - Capture console output with timing statistics
    - Document baseline execution times for each benchmark in test comments
    - Note: Baselines are reference points only, no automated comparison yet
  - [ ] 4.3 Add baseline metrics documentation
    - Update test docstrings with baseline timing reference
    - Document baseline context: Python version, hardware, test data size
    - Add comments explaining expected performance characteristics
    - Reference baseline in each benchmark test for future comparison
    - Store baseline information in test file header comment
  - [ ] 4.4 Add free-threaded Python testing notes
    - Add module-level docstring note about free-threaded regression testing
    - Document that performance tests should be run with free-threaded builds
    - Reference pytest-freethreaded plugin already in dependencies
    - Note compatibility with "just test-freethreaded" command
    - Add comment about parallel execution with --threads=8 --iterations=10
    - Reference Python 3.14t free-threaded build requirement
  - [ ] 4.5 Document console output format
    - Confirm pytest-benchmark uses default table output
    - Verify statistics display: min, max, mean, stddev
    - Confirm operations per second (ops/sec) appears in output
    - Add comment in test file explaining output format
    - No JSON, CSV, or other export formats needed
  - [ ] 4.6 Verify integration with existing test suite
    - Confirm performance tests work with "just test -m slow"
    - Verify tests are skipped by default with "just test"
    - Test that pytest markers infrastructure works correctly
    - Ensure no conflicts with existing pytest configuration
    - Verify performance tests can run with parallel execution (just test-parallel -m slow)
  - [ ] 4.7 Run final validation of complete feature
    - Run all performance tests: `just test -m slow`
    - Verify all benchmarks execute and display results
    - Confirm memory tracking tests report usage
    - Check that baseline metrics are documented
    - Validate free-threaded compatibility notes are present
    - Run with free-threaded Python if available: `just test-freethreaded -m slow`

**Acceptance Criteria:**
- The 1-2 tests written in 4.1 pass
- Baseline metrics established and documented in test docstrings/comments
- Free-threaded regression testing notes added to module docstring
- Console output format documented (default pytest-benchmark table)
- Performance tests integrate with existing pytest configuration
- Tests runnable with "just test -m slow" and skipped by default
- Free-threaded compatibility documented with pytest-freethreaded reference

## Execution Order

Recommended implementation sequence:
1. Infrastructure Setup (Task Group 1) - Set up pytest-benchmark, markers, test file
2. Test Data Generation (Task Group 2) - Create fixtures for large component trees
3. Core Benchmarks (Task Group 3) - Implement benchmarks and memory tracking
4. Documentation and Integration (Task Group 4) - Establish baselines, add free-threaded notes

## Important Notes

**Test-Driven Development:**
- Each task group starts with writing 1-4 focused tests (x.1 sub-task)
- Tests verify infrastructure, fixtures, or benchmark behavior
- Task group ends with running ONLY newly written tests, not entire suite
- Total expected tests for this feature: approximately 8-13 tests

**Benchmark Design:**
- Follow Storyville's simple benchmark(function, *args) pattern
- Use pytest-benchmark fixture to wrap operations
- Let pytest-benchmark handle timing automatically
- No explicit assertions needed in benchmark tests (focus on timing)
- Each benchmark should have clear docstring explaining what's measured

**Memory Tracking:**
- Use Python's built-in tracemalloc module
- Keep profiling simple (no external tools like memory_profiler)
- Report peak memory usage and memory deltas
- Document memory overhead in test docstrings

**Free-threaded Python:**
- pytest-freethreaded is already in dependencies
- Performance tests should work with "just test-freethreaded -m slow"
- Document parallel execution parameters (--threads=8 --iterations=10)
- Reference Python 3.14t requirement in notes

**Marker Integration:**
- Use @pytest.mark.slow on ALL performance tests
- Default behavior: skip slow tests (addopts = '-m "not slow"')
- Run performance tests explicitly: `just test -m slow`
- Compatible with parallel execution: `just test-parallel -m slow`

**Test Data Scale:**
- Large component tree: minimum 100 components
- Include nested structures (3-4 levels deep)
- Mix components with and without static assets
- Realistic asset references: CSS, JS files

**Baseline Metrics:**
- No automated comparison or CI integration initially
- Document baselines as reference points in comments/docstrings
- Include context: Python version, hardware, test data characteristics
- Baselines serve as manual comparison points for future measurements
