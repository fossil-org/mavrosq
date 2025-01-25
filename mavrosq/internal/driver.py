import os
from contextlib import contextmanager

from ..parser.lens import LensParser
from ..parser.packaging import Package
from .strap import strap


@contextmanager
def create_temporary_file_from_lens(lens: LensParser, *packages: Package, dist_path: str | None = None, no_delete: bool = False) -> None:
    fn: str = dist_path or f"{lens.id}.lens"
    with open(fn, "w") as file:
        file.write(strap(lens, print, *packages))
    yield fn
    if not no_delete:
        os.remove(fn)