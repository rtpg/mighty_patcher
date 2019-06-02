from types import FunctionType

from ._better_mocking import replace_cfunction, replace_dict, replace_func, replace_type


def replace_object(fst, snd):
    # let's make a holder class for the old values
    class OldFirst:
        pass
    old_first = OldFirst()
    try:
        old_first.__class__ = fst.__class__
    except TypeError:
        raise TypeError("Object replacement failed on ", type(fst), " and ", type(snd))
    old_first.__dict__ = old_first.__dict__

    # then we'll replace fst with snd
    try:
        fst.__class__ = snd.__class__
    except TypeError:
        raise TypeError("Object replacement failed on ", type(fst), " and ", type(snd))
    fst.__dict__ = snd.__dict__

    return old_first


def replace_inner_value(fst, snd):
    if type(fst) != type(snd):
        # "Type exception"
        if type(fst) == type and type(snd) == type:
            pass
        # object exception
        elif isinstance(fst, object) and isinstance(snd, object):
            pass
        else:
            raise ValueError(
                f"""
                Currently inner value replacing requires exactly the same types
                Received types {type(fst)} and {type(snd)}
                """
            )
    if type(fst) == dict:
        return replace_dict(fst, snd)
    if type(fst) == FunctionType:
        return replace_func(fst, snd)
    if type(fst) == type(print):
        return replace_cfunction(fst, snd)
    if type(fst) == type:
        return replace_type(fst, snd)
    if isinstance(fst, (int, float, str, bytes)):
        raise ValueError(
            f"""
            There's currently no support for replacing with type {type(fst)}
            """
        )
    if isinstance(fst, object):
        # since we're working with objects we can try just swapping out the classes
        # and the instance dicts
        return replace_object(fst, snd)
    # return
    raise ValueError(
        f"""
        There's currently no support for replacing with type {type(fst)}
        """
    )
