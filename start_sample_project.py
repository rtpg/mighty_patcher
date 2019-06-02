# This is a sampel project I was using to test things

import os.path
from pathlib import Path
from time import sleep

from mighty_patcher.watch import AutoReloader
from sample_project.math import mul_2

i = 0


def main():
    global i
    print(mul_2(i))
    i += 1

import pdb

def main_loop():
    while True:
        try:
            main()
            sleep(2)
        except Exception as exc:
            pdb.post_mortem(exc.__traceback__)



if __name__ == '__main__':
    print("Starting autoloader and main_loop")
    path = Path(__file__).joinpath('..').resolve()
    print("watching ", path)
    reloader = AutoReloader(
        path
    )
    try:
        main_loop()
    except KeyboardInterrupt:
        reloader.observer.stop()
    reloader.observer.join()

# this is a comment
