"""Simple profiling utilities for performance analysis."""

import cProfile
import io
import pstats
from typing import Callable


def profile_function(func: Callable, *args, **kwargs):
    """Profile a function and print the top results.

    Args:
        func: Function to profile
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func

    Returns:
        The function's return value
    """
    profiler = cProfile.Profile()
    profiler.enable()

    result = func(*args, **kwargs)

    profiler.disable()

    # Print stats
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

    print(stream.getvalue())

    return result
