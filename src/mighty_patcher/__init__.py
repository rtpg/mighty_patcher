from contextlib import contextmanager

from .replacement import replace_inner_value
import mighty_patcher.reload

__version__ = '0.1'


def currently_reloading():
    return mighty_patcher.reload._reloading


@contextmanager
def actually_patch(func_to_patch, replacement):
    """
    Patch a function or a dictionary but for real (no need to worry about references)

    This function currently leaks memory and should never be used in production
    (This introduces the possibility of segfaults and general bustedness)
    """
    # replace the value
    old_func_value = replace_inner_value(
        func_to_patch,
        replacement,
    )
    try:
        yield
    finally:
        # put the thing back in
        replace_inner_value(
            func_to_patch,
            old_func_value
        )
