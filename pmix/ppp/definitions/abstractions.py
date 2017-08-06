"""Reusable function and class abstractions."""


def chain(_input, funcs):
    """Execute recursive function chain on input and return it.

    Side Effects: Mutates input, funcs.

    Args:
        _input: Input of any data type to be passed into functions.
        funcs: Ordered list of funcs to be applied to input.

    Returns:
        Recusive call if any functions remaining, else the altered input.
    """
    return chain(funcs.pop(0)(_input), funcs) if funcs else _input


def immutable_chain(_input, funcs):
    """Execute recursive function chain on input and return it.

    TODO: Import copy.copy only on first iteration by using an iterator int.

    Args:
        _input: Input of any data type to be passed into functions.
        funcs: Ordered list of funcs to be applied to input.

    Returns:
        Recusive call if any functions remaining, else the altered input.
    """
    from copy import copy
    new_functions = copy(funcs)
    new_input = new_functions.pop()(copy(_input)) if funcs else None
    return chain(new_input, new_functions) if funcs else copy(_input)
