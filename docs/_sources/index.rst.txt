.. Mighty Patcher documentation master file, created by
   sphinx-quickstart on Sat Jun 22 12:16:53 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Mighty Patcher's documentation!
==========================================

This project provides an automatic, restart-less code reloader for Python. Concretely this means that you can update the code inside a running Python program and test the new behaviour without having to go through a restart cycle.

This project is an attempt to give Python the same sort of tooling that gives Clojure `Figwheel`_ or gives Ruby `Sonic Pi`_.

..  _Figwheel: https://figwheel.org/
..  _Sonic Pi: https://sonic-pi.net/

------------------
What does this do?
------------------

The Mighty Patcher provides a file-watching auto-reloader, whose instances will watch your project directory for changes to Python files on a separate thread. When changes are seen, this thread will re-import the python file and patch in the new module


.. toctree::
   :maxdepth: 1
   :hidden:
   
   introduction
   usage
   plugin
   api
   how


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
