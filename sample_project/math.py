"""
This file is used for testing patching functionality

"""
from mighty_patcher import currently_reloading


def mul_2(n):
    return c.count()*n


class Counter:
    i = 0

    def count(self):
        self.i += 1
        print(">>>", self.i)
        return self.i


if not currently_reloading():
    c = Counter()
