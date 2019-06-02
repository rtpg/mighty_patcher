from os import path, remove
import shutil
from pathlib import Path

from mighty_patcher import replace_inner_value
from mighty_patcher.reload import really_reload


def setup_old_math_lib():
    dir_path = Path(__file__).joinpath('..').resolve()
    src_old = path.join(dir_path, 'reload_module/math_old.py')
    target = path.join(dir_path, 'reload_module/math.py')

    shutil.copy(
        src_old,
        target
    )


def update_math_py_with_new_code():
    dir_path = Path(__file__).joinpath('..').resolve()
    src_new = path.join(dir_path, 'reload_module/math_new.py')
    target = path.join(dir_path, 'reload_module/math.py')

    shutil.copy(
        src_new,
        target
    )


def test_basic_reloading():
    """
    Test that we can easily reload modules and references will reload cleanly
    """
    # first, let's use an old math lib
    setup_old_math_lib()

    # now we can import
    from .reload_module import my_prog, math

    assert my_prog.main() == 3

    assert id(my_prog.do_some_math.__code__) == id(math.do_some_math.__code__)
    # let's then update the math lib with a change to how the math works
    update_math_py_with_new_code()

    # nothing's changed yet
    assert my_prog.main() == 3

    # let's reload the math module
    really_reload(math)

    # this will have updated the math import deep inside my_prog
    assert id(my_prog.do_some_math.__code__) == id(math.do_some_math.__code__)

    assert my_prog.main() == 9


def test_failure_of_just_reload():
    """
    Test that really_reload is _actually_ needed in this test case

    This test exists to check that the test before it is
    actually testing what needs to be tested
    """

    from importlib import reload, invalidate_caches
    setup_old_math_lib()
    invalidate_caches()
    from .reload_module import my_prog, math

    assert my_prog.main() == 3
    update_math_py_with_new_code()
    #let's try using importlib
    reload(math)
    # we successfully reloaded the module, but...
    assert math.do_some_math() == 9
    # the main program is still using the old code
    assert my_prog.main() == 3
