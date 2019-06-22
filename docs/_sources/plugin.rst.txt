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

