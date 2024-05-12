import json
import glob
import os
from jsonpatch import JsonPatch

from .version import __version__


class EidosError(Exception):
    """Base class for eidos exceptions."""


class Eidos(EidosSpecification):
    """Eidos class."""

    _checkpoint = None

    @classmethod
    def from_dict(cls, spec: dict):
        """Initialize Eidos class."""
        return cls(**spec)

    @classmethod
    def from_json(cls, spec: str):
        """Initialize Eidos class from json."""
        return cls.from_dict(json.loads(spec))

    def __init__(self, **data):
        """Initialize Eidos class."""
        super().__init__(**data)
        self._checkpoint = self.model_dump()

    def __str__(self):
        """Return string representation of Eidos class."""
        return self.model_dump_json(indent=2)

    def _change(self, update):
        """Change."""
        print(f"EIDOS spec changed: {update}")

    def diff(self):
        old = self._checkpoint
        self._checkpoint = self.model_dump()
        return (old, self._checkpoint)

    def json_diff(self):
        """Diff."""
        old, new = self.diff()
        return JsonPatch.from_diff(old, new)
