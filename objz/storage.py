# This file is placed in the Public Domain.


"disk"


from .serials import dump, load
from .        import Object, update


def cdir(path):
    pth = pathlib.Path(path)
    pth.parent.mkdir(parents=True, exist_ok=True)


def read(obj, path):
    with open(path, "r", encoding="utf-8") as fpt:
        try:
            update(obj, load(fpt))
        except json.decoder.JSONDecodeError as ex:
            ex.add_note(path)
            raise ex


def write(obj, path):
    cdir(path)
    with open(path, "w", encoding="utf-8") as fpt:
        dump(obj, fpt, indent=4)
    return path


def __dir__():
    return (
        'read',
        'write'
    )


__all__ = __dir__()
