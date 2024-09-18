# generated by datamodel-codegen:
#   filename:  worldlayers/grid.json
#   timestamp: 2024-09-17T00:58:51+00:00

from __future__ import annotations

from typing import List, Optional

from oceanum.eidos._basemodel import EidosModel
from pydantic import ConfigDict, Field, RootModel

from ..viewnodes import world


class GridLayerDatakeys(EidosModel):
    """
    Mapping from data variables to x,y and c(scalar value)
    """

    x: str
    y: str
    c: Optional[str] = None
    d: Optional[str] = None
    m: Optional[str] = None
    u: Optional[str] = None
    v: Optional[str] = None


class Baseprops(EidosModel):
    altitude: Optional[float] = None
    zscale: Optional[float] = None
    colormap: Optional[bool] = None
    opacity: Optional[float] = 1.0
    color: Optional[world.Color] = None


class Pcolor(RootModel[Baseprops]):
    root: Baseprops


class Particles(RootModel[Baseprops]):
    root: Baseprops


class Partmesh(RootModel[Baseprops]):
    root: Baseprops


class Contour(Baseprops):
    levels: Optional[List[float]] = None
    linewidth: Optional[int] = 1


class GridLayerSpec(EidosModel):
    """
    Specification for Grid Overlay model settings
    """

    model_config = ConfigDict(
        extra='forbid',
    )
    datakeys: GridLayerDatakeys
    hoverInfo: Optional[world.HoverInfo] = None
    legend: Optional[world.Colormap] = None
    colormap: world.Colormap
    pcolor: Optional[Pcolor] = None
    particles: Optional[Particles] = None
    partmesh: Optional[Particles] = None
    contour: Optional[Contour] = None
    scale: Optional[float] = 1
    offset: Optional[float] = 1
    units: Optional[str] = None
    precision: Optional[float] = 1
    minzoom: Optional[float] = 1
    maxzoom: Optional[float] = 18
    landmask: Optional[bool] = None
    global_: Optional[bool] = Field(None, alias='global')
