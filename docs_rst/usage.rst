=====
Usage
=====

The base entry point is the :py:class:`~mighty_patcher.watch.AutoReloader` class. Before starting up your main program loop, instantiating an instance of this class will start a separate thread that watches for Python changes::

    from some_module.print import announce_double_time
    import some_module.math
    from time import sleep

    from mighty_patcher.watch import AutoReloader

    reloader = AutoReloader(
        path="/path/to/my/project/src/"
    )

    while True:
        print(double(4))
        sleep(10)

By default the reloader will print information related to errors on code reloading, but tries to be tolerant to errors so that your program doesn't crash because you saved halfway through typing a file.

The reloader path is considered a module root, and the relative path of modified python files are used to determine what module they represent:

For example, here ``"/path/to/my/project/src/some_module/math.py"`` would map to ``some_module.math``

Because of how modules work, this will mostly be what you want. But if your project has various lookup paths set up (for example if some code refers to the math module as ``src.some_module.math``), then the file might not map over properly.

----------------------------
Changing behaviour on reload
----------------------------

If you are working on something that has global state that you don't want to have thrown away on every reload, you can modify what your code does depending on whether it's the initial load of the code or whether you are reloading this code::


     # some_file.py
     from mighty_patcher import currently_reloading
     import time

     # this dictionary will get reset to an empty state
     _my_cache = {}

     if not currently_reloading():
         # this will get run on the first import of this file, but not on subsequent reloads
	 program_run_start = time.time()
         number_of_restarts = 0

     if currently_reloading():
         # this block will only run on reloads
	 number_of_restarts += 1
	 print("Reloaded!")


-------
Caveats
-------

- Because of how the reloading works, some primitive data types (notably numeric datatypes) might not always reload in the expected way.

- If your code (or a third party library) uses a registry pattern and has some validation to make sure that (for example) you don't declare two classes as having the same name, you can run into issues when reloading files.

- This is notably a problem  with Django and its ORM models. This isn't a problem for the entire Django project, but files containing model definitions likely won't reload properly.

- The main thing to remember is that this is changing stuff out from under CPython, and it's not the expected execution model. Don't use this on a long-running production server! Expect crashes and embrace them.

- Also the implementation currently has a memory leak proportional to the number of reloads going on in a single session (old versions of objects stick around forever). This problem is solvable but requires a bit of work on the internals

