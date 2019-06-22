How It Works
============

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

