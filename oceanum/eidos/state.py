# generated by datamodel-codegen:
#   filename:  state.json
#   timestamp: 2025-04-01T05:05:10+00:00

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from oceanum.eidos._basemodel import EidosModel
from pydantic import Field, RootModel


class EidosState(RootModel[Any]):
    root: Any = Field(..., title='Eidos state')


class CurrentTime(RootModel[str]):
    root: str
    """
    Time of for current view
    """


class CurrentContext(EidosModel):
    """
    Context of for current view
    """


class TimeControl(EidosModel):
    global_: Optional[bool] = Field(True, alias='global', title='Set global time')
    """
    Sets the global time select
    """
    range: Optional[List[datetime]] = Field(None, max_length=2, min_length=2)
    """
    Maximum time range of time contorl
    """
    increment: Optional[float] = Field(None, title='TIme selector increments')
    """
    Size in seconds of the time selector increments
    """
    zoomToNow: Optional[bool] = Field(True, title='Zoom to now button')
    """
    Adds a button that zooms to the current time
    """
    zoomToExtent: Optional[bool] = Field(True, title='Zoom to range button')
    """
    Adds a button that zooms to the current time range
    """


class Mode(str, Enum):
    nearest = 'nearest'
    exact = 'exact'
    range = 'range'


class Aggregate(str, Enum):
    """
    Aggregation method for time range
    """

    last = 'last'
    first = 'first'
    sum = 'sum'
    mean = 'mean'
    max = 'max'
    min = 'min'


class TimeSelect(EidosModel):
    mode: Mode
    toleration: Optional[str] = None
    """
    Time toleration duration for nearest time select
    """
    aggregate: Optional[Aggregate] = Field('last', title='Time aggregation')
    """
    Aggregation method for time range
    """
    groupby: Optional[str] = None
    """
    Data field to group by
    """


class ContextControl(RootModel[List[Dict[str, Any]]]):
    """
    Context selector for current view
    """

    root: List[Dict[str, Any]]
    """
    Context selector for current view
    """
