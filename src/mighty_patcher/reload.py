import copy
from collections import defaultdict
from importlib import reload

from mighty_patcher import replace_inner_value

# This is memory leak city! At least untill I fix it
# this will hold onto every old reference to older module values
# [module_name][module_elt] gets you to a list of older references
_module_cache = defaultdict(
    lambda: defaultdict(list)
)

# this value is used to track if something is currently reloading
_reloading = False


def really_reload(module):
    """
    Take a module, and try to reload it while
    replacing all of its values
    """
    global _reloading
    _reloading = True
    # first, store old references
    for k in dir(module):
        _module_cache[module.__name__][k].append(getattr(module, k))
    new_module = reload(module)
    # Try to replace all the elements in the module
    for elt in dir(new_module):
        # we are going to exclude dunder stuff because
        # I'm pretty sure that replacing them all the time would be
        # not a great idea
        if elt[:2] == '__':
            continue
        # pytest generates some weird symbols that I don't want to replace
        if elt[:1] == '@':
            continue
        print("REPLACING ELT ", elt)
        errors = []
        if elt in _module_cache[module.__name__]:
            # we need to replace all the old references
            for old_reference in _module_cache[module.__name__][elt]:
                try:
                    replace_inner_value(
                        old_reference,
                        getattr(new_module, elt)
                    )
                except Exception as exc:
                    errors.append([elt, exc])
        # write to the old module object just in case we have existing people
        # holding onto this
        # TODO replace all module references through inner_module_replace
        setattr(module, elt, getattr(new_module, elt))

    _reloading = False
    if len(errors):
        raise ValueError("Failed reload on the following:", errors)
