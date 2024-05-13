import json
import glob
import os
from jsonpatch import JsonPatch
from pandas import DataFrame
from geopandas import GeoDataFrame
from xarray import Dataset
from oceanum.datamesh import Query

from .version import __version__
from .core.root import EidosSpecification
from .core.dataspec import Datasource


class EidosError(Exception):
    """Base class for eidos exceptions."""


class Eidos(EidosSpecification):
    """Eidos base class. This is the EIDOS base specification."""

    _checkpoint = None

    @classmethod
    def from_dict(cls, spec: dict):
        """Initialize Eidos class."""
        return cls(**spec)

    @classmethod
    def from_json(cls, spec: str):
        """Initialize Eidos class from json."""
        return cls.from_dict(json.loads(spec))

    def __init__(self, **spec):
        """Initialize Eidos class."""
        super().__init__(**spec)
        self._checkpoint = self.model_dump()

    def __str__(self):
        """Return string representation of Eidos class."""
        return self.model_dump_json(indent=2)

    def _change(self, update):
        """Change."""
        print(f"EIDOS spec changed: {update}")

    def diff(self):
        """Get diff since last checkpoint and reset checkpoint"""
        old = self._checkpoint
        self._checkpoint = self.model_dump()
        return (old, self._checkpoint)

    def json_diff(self):
        """Diff as JSON patch"""
        old, new = self.diff()
        return JsonPatch.from_diff(old, new)


class EidosDatasource(Datasource):
    """Convenience class for Eidos datasource from python data objects."""

    def __init__(self, id, data):
        """Initialize Eidos datasource.

        Args:
            id (str): The ID of the datasource.
            data (DataFrame, GeoDataFrame, Dataset, Query): The data to be used for the datasource.

        Raises:
            EidosError: If an invalid inline data type is provided.

        """
        if isinstance(data, DataFrame):
            data = data.to_xarray().to_dict()
            dtype = "inlineDataset"
        elif isinstance(data, GeoDataFrame):
            data = data.__geo_interface__
            dtype = "featureCollection"
        elif isinstance(data, Dataset):
            data = data.to_dict()
            dtype = "inlineDataset"
        elif isinstance(data, Query):
            dtpe = "oceanumDatamesh"
        else:
            raise EidosError("Invalid inline data type")
        super().__init__(id=id, dataType=dtype, dataSpec=data)
