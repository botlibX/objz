OBJECTS
=======


**NAME**


|
| ``objects`` - a clean namespace
|


**SYNOPSIS**

::

    >>> from objects import Object, dumps, loads
    >>> o = Object()
    >>> o.a = "b"
    >>> print(loads(dumps(o)))
    {'a': 'b'}


**DESCRIPTION**


``objects`` contains python3 code to program objects in a functional
way. it provides an “clean namespace” Object class that only has
dunder methods, so the namespace is not cluttered with method names.

This makes reading to/from json possible.


**INSTALL**


installation is done with pip

|
| ``$ pip install objects``
|

**AUTHOR**

|
| Bart Thate <``bthate@dds.nl``>
|

**COPYRIGHT**

|
| ``objects`` is Public Domain.
|
