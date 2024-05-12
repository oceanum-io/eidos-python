# generated by datamodel-codegen:
#   filename:  worldlayers/sea_surface.json
#   timestamp: 2024-05-12T22:42:44+00:00

from __future__ import annotations

from typing import Any, List, Optional

from pydantic import ConfigDict, Field

from eidos._basemodel import EidosModel

from .. import features


class Offset(EidosModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    xoffset: Optional[float] = Field(0, title='X offset')
    yoffset: Optional[float] = Field(0, title='Y offset')
    pitch: Optional[float] = Field(0, title='Pitch offset')
    zoffset: Optional[float] = Field(0, title='Heave offset')
    roll: Optional[float] = Field(0, title='Roll offset')
    heading: Optional[float] = Field(0, title='Heading')
    speed: Optional[float] = Field(
        0, description='Speed of the floater in m/s', title='Speed'
    )
    scale: Optional[float] = Field(1, description='Uniform Scale factor', title='Scale')
    xscale: Optional[float] = Field(
        0, description='Scale factor in x direction', title='X scale'
    )
    yscale: Optional[float] = Field(
        0, description='Scale factor in y direction', title='Y scale'
    )
    zscale: Optional[float] = Field(
        0, description='Scale factor in z direction', title='Z scale'
    )


class SeaSurfaceLayerDatakeys(EidosModel):
    model_config = ConfigDict(
        extra='allow',
    )
    f: str = Field(..., title='Frequency')
    d: str = Field(..., title='Direction')
    efth: str = Field(..., title='Spectral variance')


class SeaSurfaceRaoDatakeys(EidosModel):
    model_config = ConfigDict(
        extra='allow',
    )
    f: str = Field(..., title='Frequency')
    d: str = Field(..., title='Direction')
    pitch_amp: Optional[str] = Field('pitch_amp', title='Amplitude response')
    Pitch_pha: Optional[str] = Field('pitch_pha', title='Phase response')
    roll_amp: Optional[str] = Field('roll_amp', title='Amplitude response')
    roll_pha: Optional[str] = Field('roll_pha', title='Phase response')
    heave_amp: str = Field(..., title='Amplitude response')
    heave_pha: str = Field(..., title='Phase response')


class Rao(EidosModel):
    model_config = ConfigDict(
        extra='allow',
    )
    datakeys: SeaSurfaceRaoDatakeys
    data: str = Field(..., description='Name of the data source', title='Data')


class Floater(EidosModel):
    id: str = Field(..., description='Unique identifier for the floater', title='ID')
    name: Optional[str] = Field(None, description='Name of the floater', title='Name')
    position: Optional[features.Point] = None
    gltf: str = Field(..., description='name or URL of GLTF model', title='GLTF model')
    style: Optional[Any] = None
    offsets: Optional[List[Offset]] = Field(
        None, description='Array of position offsets, one for each model instance'
    )
    rao: Optional[Rao] = Field(
        None, description='Response Amplitude Operator', title='RAO'
    )


class SeaSurfaceLayer(EidosModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    datakeys: SeaSurfaceLayerDatakeys
    minzoom: Optional[float] = Field(
        13, description='Minimum zoom to show sea surface', title='Minimum zoom'
    )
    zscale: Optional[float] = Field(
        1, description='Vertical scale exageration', title='Vertical scale'
    )
    elevation: Optional[float] = Field(
        0,
        description='Elevation of mean sea level in metres',
        title='Sea level elevation',
    )
    floaters: Optional[List[Floater]] = Field(
        [], description='List of floating objects', title='Floaters'
    )
