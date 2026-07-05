"""Back-compatibility alias: ``oceanum.eidos`` re-exports the ``eidosxr`` package.

The EIDOS Python bindings live in the top-level ``eidosxr`` package (named to
avoid clashing with the unrelated ``eidos`` project on PyPI). This shim keeps the
legacy ``from oceanum.eidos import ...`` path working, resolving to the *same*
objects as ``eidosxr`` so pydantic model / ``isinstance`` identity is preserved.
"""
import sys as _sys

import eidosxr as _eidosxr  # noqa: F401  (imports all eidosxr submodules)
from eidosxr import *  # noqa: F401,F403

for _name, _module in list(_sys.modules.items()):
    if _name == "eidosxr" or _name.startswith("eidosxr."):
        _sys.modules["oceanum.eidos" + _name[len("eidosxr"):]] = _module

try:
    from eidosxr import __all__ as __all__  # noqa: F401
except ImportError:  # pragma: no cover
    __all__ = [n for n in dir(_eidosxr) if not n.startswith("_")]

try:
    from eidosxr.version import __version__ as __version__  # noqa: F401
except ImportError:  # pragma: no cover
    pass
