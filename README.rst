==============
Mighty Patcher
==============

This project provides an automatic, restart-less code reloader for Python. Concretely this means that you can update the code inside a running Python program and test the new behaviour without having to go through a restart cycle.

This project is an attempt to give Python the same sort of tooling that gives Clojure `Figwheel`_ or gives Ruby `Sonic Pi`_. 

..  _Figwheel: https://figwheel.org/
..  _Sonic Pi: https://sonic-pi.net/
   
------------------
What does this do?
------------------

The Mighty Patcher provides a file-watching auto-reloader, whose instances will watch your project directory for changes to Python files on a separate thread. When changes are seen, this thread will re-import the python file and patch in the new module

============
Installation
============

This is available for installation on PyPI. This also sets up the Pytest plugin, so any project using ``pytest`` will be able to use this project's autoreloader in test runs through one configuration flag::

    pip install mighty_patcher

=====
Usage
=====

The base entry point is the ``AutoReloader`` class. Before starting up your main program loop, instantiating an instance of this class will start a separate thread that watches for Python changes::
   
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

Because of how the reloading works, some primitive data types (notably numeric datatypes) might not always reload in the expected way.
 
If your code (or a third party library) uses a registry pattern and has some validation to make sure that (for example) you don't declare two classes as having the same name, you can run into issues when reloading files.

This is notably a problem  with Django and its ORM models. This isn't a problem for the entire Django project, but files containing model definitions likely won't reload properly.

The main thing to remember is that this is changing stuff out from under CPython, and it's not the expected execution model. Don't use this on a long-running production server! Expect crashes and embrace them.

Also the implementation currently has a memory leak proportional to the number of reloads going on in a single session (old versions of objects stick around forever). This problem is solvable but requires a bit of work on the internals

=====================
Usage (Pytest plugin)
=====================

Once you install this package you can use it as a pytest plugin.

The following options are made available when running pytest:

 - ``--reload-loop``

   Running this flag starts an autoreloader when you start your tests. When you reach a test failure, you will be dropped into pdb to examine the error.

   While you are in ``pdb`` mode, you can edit your project files and the autoreloader will install the new code. After you are confident that you have fixed the issue, you can leave the debugger with the ``c`` (continue) command and the test will be run again.

 - ``--reload-dir``

   Choose what directory the autoreloader should look at. This directory is then considered the package root for puprposes of determining what package a file belongs to (and thus what directory to reload)

   This defaults to the ``pytest`` invocation directory, but you might need to point to another directory if you do things like splitting your code into ``src`` and ``tests`` (where ``src`` is the package root)


-----------------------
Caveats (Pytest plugin)
-----------------------

 - Because the debugger needs to handle standard input, currently you always need to pass in `-s` when invoking pytest to avoid the default "capture standard input and output" behaviour of pytest.

 - I have hit some issues with editing the test code itself (that is to say the actively running test class/test function rather than the application code). This requires a bit more investigation

 - As always, when in doubt, tear down the entire program and restart

--------------------------------------------------------------
Whats the big deal? Don't I already have ``importlib.reload``?
--------------------------------------------------------------

Beyond setting up the file-watching infrastructure to trigger module reloads, this project offers much deeper code replacement abilities than other tools out there.

The core issue with ``importlib.reload`` is a problem of *references*.

Assuming you had the following project::


    # some_module/math.py

    def double(n):
        return 2.1 * n

::

    # some_module/print.py

    from some_module.math import double
    from time import time

    def announce_double_time():
        print(double(time()))

::

    # main.py
    from some_module.print import announce_double_time
    import some_module.math
    from time import sleep
    from importlib import reload
    
    while True:
        print(double(4))
        sleep(10)
	# reload the math and try again
	reload(some_module.math)


Here you could be working out the kinks of your module's math and so write a reload loop specifically for it (already kinda annoying). Unfortunately if you write this, it *won't reload the actual math usage*

When you reload the module you end up replacing the values within the module object. So in a sense you end up with ``some_module.math.double = newly_loaded_double`` running on each reload.

*But* inside your dependent module (``some_module.print``), you have a qualified import statement that gets executed once here::

   from some_module.math import double
   
   # is roughly the same as

   double sys.modules['some_module.math']['double']


So until you reload ``some_module.print``, *its* refernce to ``double`` will always point to the original implementaion, no matter how many times you reload the source module.

Here you can solve the problem by doing workarounds like:

- using module-qualified imports (``from some_module import math`` then ``math.double``), since then you will point to the module, and classic module reloading actually just edits the module inplace

- making sure to reload dependencies properly. So "reload `some_module.math`, then reload `some_module.print`" (making sure to do things in the right order if you want to avoid a "stale reference" problem)

But ultimately this leads you down the road of adapting how you write your code so you can be able to use a tool. It forces you to write things un-naturally


------------------------------------------------
How the Mighty Patcher avoids reference problems
------------------------------------------------

Even if importing in a function creates another reference to it, ultimately the reference is pointing to *the same function*.

So when you first load the program you end up with the following memory layout::

  
   [some_module.math]  --"double" --> <function object>
   #                                    ^               
   #                                    |
   #                                    |
   [some_module.print] --"double" ------/


Classic module reloading will try to edit the modules to provide new definitions. But the Mighty Patcher instead opts to *replace the function object directly*, so that references are pointing to the correct object.

This isn't actually possible in pure Python, so this project has a built-in CPython extension to let us directly modify the function object, making sure that any reference to that function object will get the most up-to-date version of the object.

There are a lot of details and gotchas around this technique, but for the most part this drastically reduces turnaround time for workflows that might otherwise require a lot of restarts

