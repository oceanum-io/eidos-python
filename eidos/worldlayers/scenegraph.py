# generated by datamodel-codegen:
#   filename:  worldlayers/scenegraph.json
#   timestamp: 2024-05-15T05:06:01+00:00

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import ConfigDict, Field

from eidos._basemodel import EidosModel

from .. import features
from ..core import state
from ..viewnodes import world


class Gltf(EidosModel):
    """
    name or URLs of GLTF model keyed to data property
    """

    model_config = ConfigDict(
        extra='allow',
    )
    field_default: str = Field(..., alias='_default')


class Scenegraph(EidosModel):
    key: Optional[str] = Field(None, title='Scenegraph key')
    """
    Data field to use as key for scenegraph model
    """
    gltf: Gltf = Field(..., title='GLTF models')
    """
    name or URLs of GLTF model keyed to data property
    """


class ScenegraphLayerDatakeys(EidosModel):
    """
    Mapping from data variables to geometry
    """

    model_config = ConfigDict(
        extra='allow',
    )
    x: str
    y: str
    z: Optional[str] = 'z'
    roll: Optional[str] = 'roll'
    pitch: Optional[str] = 'pitch'
    yaw: Optional[str] = 'yaw'
    xoffset: Optional[str] = 'xoffset'
    yoffset: Optional[str] = 'yoffset'
    zoffset: Optional[str] = 'zoffset'
    xscale: Optional[str] = 'xscale'
    yscale: Optional[str] = 'yscale'
    zscale: Optional[str] = 'zscale'


class ScenegraphLayer(EidosModel):
    """
    Specification for Scenegraph layer
    """

    model_config = ConfigDict(
        extra='forbid',
    )
    dataKeys: ScenegraphLayerDatakeys
    hoverInfo: Optional[world.HoverInfo] = None
    timeSelect: Optional[state.TimeSelect] = None
    geometry: Optional[features.Feature] = None
    colormap: Optional[world.Colormap] = None
    scenegraph: Optional[Scenegraph] = None
    style: Optional[Dict[str, Any]] = None