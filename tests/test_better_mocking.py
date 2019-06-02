from unittest.mock import patch

import mighty_patcher
import pytest
import tests.some_module.math
from mighty_patcher import replace_inner_value
from tests.some_module.a import add as add_from_a
from tests.some_module.a import return_add_2_2
from tests.some_module.math import add as add_from_math


def test_name_replacing():
    one_dictionary = {'a': 1}
    another_dictionary = {'a': 2}
    assert one_dictionary['a'] == 1
    return_value = replace_inner_value(one_dictionary, another_dictionary)
    assert return_value == 'success'
    # this should mean that `one_dictionary` is now pointing at a different value
    assert one_dictionary['a'] == 2


def test_advanced_replacing():
    one_dictionary = {'a': 1}
    another_dictionary = {'a': 2}

    assert one_dictionary != another_dictionary

    def do_black_magic(fst, snd):
        return replace_inner_value(fst, snd)

    do_black_magic(one_dictionary, another_dictionary)
    assert one_dictionary == another_dictionary


def test_replace_funcs():
    def f():
        return 1

    def g():
        return 2

    assert f() == 1
    return_of_replace = replace_inner_value(f, g)
    assert f() == 2
    assert f.__name__ == 'g'

    # the return holds the old reference though
    assert return_of_replace() == 1


# from math.py
"""
def add(a, b):
    return a + b
"""

# from a.py
"""
from tests.some_module.math import add

def return_add_2_2():
    return add(2, 2)
"""


@pytest.mark.skip("This is an example of how not to mock")
def test_basic_mocking():
    assert return_add_2_2() == 4
    with patch(tests.some_module.math.add) as mocked_method:
        return_add_2_2()
        assert mocked_method.call_count == 1

        mocked_method.return_value = 3
        assert return_add_2_2() == 3


@pytest.mark.skip("This is another example of how not to mock")
def test_basic_mocking_again():
    assert return_add_2_2() == 4
    with patch('tests.some_module.math.add') as mocked_method:
        return_add_2_2()
        assert mocked_method.call_count == 1

        mocked_method.return_value = 3
        assert return_add_2_2() == 3


def test_basic_mocking_right():
    assert return_add_2_2() == 4
    with patch('tests.some_module.a.add') as mocked_method:
        return_add_2_2()
        assert mocked_method.call_count == 1

        mocked_method.return_value = 3
        assert return_add_2_2() == 3


def test_actual_mocking():
    """
    Actually patch the method with something that works
    """

    assert return_add_2_2() == 4

    def mock_add(*args):
        return 3.5

    with mighty_patcher.actually_patch(add_from_math, mock_add):
        assert return_add_2_2() == 3.5

    # patching getting undone should get the right value
    assert return_add_2_2() == 4

    # we can patch from any reference to the function
    with mighty_patcher.actually_patch(add_from_a, mock_add):
        assert return_add_2_2() == 3.5

    # patching still gets undone
    assert return_add_2_2() == 4


def test_throwing_mock():
    def throwing_mock(*args):
        raise ValueError("Dunno")

    with pytest.raises(ValueError):
        with mighty_patcher.actually_patch(add_from_a, throwing_mock):
            return_add_2_2()
    # by the time we get back to the top level we should have
    # patched to the right value again
    assert return_add_2_2() == 4
