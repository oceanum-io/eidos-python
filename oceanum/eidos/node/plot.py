# generated by datamodel-codegen:
#   filename:  node/plot.json
#   timestamp: 2025-04-01T05:05:10+00:00

from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from oceanum.eidos._basemodel import EidosModel
from pydantic import ConfigDict

from .. import state, vegaspec


class PlotType(str, Enum):
    vega = 'vega'
    vega_lite = 'vega-lite'


class Plot(EidosModel):
    """
    Specification for plot view environmental digital twin display and interaction
    """

    model_config = ConfigDict(
        extra='forbid',
    )
    id: str
    """
    Unique id of the node
    """
    nodeType: Literal['plot'] = 'plot'
    plotType: Optional[PlotType] = None
    plotSpec: vegaspec.TopLevelSpec
    """
    Plot specification for this panel as vega spec
    """
    currentTime: Optional[state.CurrentTime] = None
    currentContext: Optional[state.CurrentContext] = None
    canExport: Optional[bool] = None
    timeControl: Optional[state.TimeControl] = None
