# during the tests we'll be copying stuff from math_old and math_new
from .math import do_some_math  # noqa


def main():
    return do_some_math()
