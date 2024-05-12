# generated by datamodel-codegen:
#   filename:  core/state.json
#   timestamp: 2024-05-12T22:42:44+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field, RootModel

from eidos._basemodel import EidosModel


class EidosState(RootModel[Any]):
    root: Any = Field(..., title='Eidos state')


class CurrentTime(RootModel[str]):
    root: str = Field(..., description='Time of for current view')


class CurrentContext(EidosModel):
    pass


class TimeControl(EidosModel):
    global_: Optional[bool] = Field(
        True,
        alias='global',
        description='Sets the global time select',
        title='Set global time',
    )
    range: Optional[List[str]] = Field(
        None,
        description='Maximum time range of time contorl',
        max_length=2,
        min_length=2,
    )
    increment: Optional[float] = Field(
        None,
        description='Size in seconds of the time selector increments',
        title='TIme selector increments',
    )


class Mode(str, Enum):
    nearest = 'nearest'
    exact = 'exact'
    range = 'range'


class Aggregate(str, Enum):
    last = 'last'
    first = 'first'
    sum = 'sum'
    mean = 'mean'
    max = 'max'
    min = 'min'


class TimeSelect(EidosModel):
    mode: Mode
    toleration: Optional[str] = None
    aggregate: Optional[Aggregate] = Field(
        'last',
        description='Aggregation method for time range',
        title='Time aggregation',
    )
    groupby: Optional[str] = Field(None, description='Data field to group by')


class ContextControl(RootModel[List[Dict[str, Any]]]):
    root: List[Dict[str, Any]] = Field(
        ..., description='Context selector for current view'
    )
