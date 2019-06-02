import sys

from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer
from watchdog import events

from mighty_patcher.reload import really_reload


class ReloadingEventHandler(events.FileSystemEventHandler):
    def __init__(self, reloader):
        self.reloader = reloader

    def on_modified(self, event):
        return self.on_potential_modified(event)

    def on_created(self, event):
        # some IDEs will do a delete/create instead of a modify
        return self.on_potential_modified(event)

    def on_potential_modified(self, event):
        # TODO take these events and figure out what module to reload
        file_path = event.src_path
        if file_path[-3:] != '.py':
            return
        print("modified " + file_path)
        self.reloader.on_pyfile_change(file_path)


def path_to_module(path: str):
    """
    Try to figure out the module a path would import into

    >>> path_to_module("foo/bar.py")
    "foo.bar"
    >>> path_to_module("foo/__init__.py")
    "foo"
    """
    if path[-3:] != '.py':
        raise ValueError("Not a python module path ", path)
    path_minus_py = path[:-3]
    path_w_dots = path_minus_py.replace("/", ".")
    # if there was an __init__ then strip that
    if path_w_dots[-9:] == ".__init__":
        path_w_dots = path_w_dots[:-9]
    return path_w_dots


class AutoReloader:
    """
    An automatic code watcher and reloader. When a reloader is created, it watches the directory provided to it for file changes (in *.py files)

    Once a change is detected, the reloader re-imports the related module and then does an in-place replacement of this module (so code dependent on
    the changes also begin pointing to the new code). 

    The path that is provided to the reloader is considered a package root
    """

    def __init__(self, path):
        """
        :param path: The directory to watch for changes. When python files in this directory changes, they will get reloaded
        """
        self.observer = Observer()
        self.base_path = path
        print("OBSERVER TYPE IS ", self.observer)
        self.handler = ReloadingEventHandler(self)
        print("PATH IS ", path)
        # self.handler = LoggingEventHandler()
        self.observer.schedule(
            self.handler,
            path,
            recursive=True
        )
        self.observer.start()

    def path_to_possible_modules(self, path_minus_prefix):
        return [path_to_module(path_minus_prefix)]

    def on_pyfile_change(self, path: str):
        if path[:len(self.base_path)] != self.base_path:
            raise ValueError("got invalid path ", path)

        path_minus_prefix = path[len(self.base_path):]

        # time to figure out what module this is
        possible_module_names = self.path_to_possible_modules(path_minus_prefix)
        module_name = None
        for name in possible_module_names:
            if name in sys.modules:
                module_name = name
                break

        # then to reload it if it exists
        if module_name is not None:
            module = sys.modules[module_name]
            try:
                really_reload(module)
            except Exception as exc:
                # when we hit an exception, we want to avoid bringing down the entire watch
                print("Hit the following exception on reload:")
                print(exc)
                return
        else:
            print(possible_module_names, " were not loaded")
