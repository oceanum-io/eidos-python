# generated by datamodel-codegen:
#   filename:  worldlayers/sea_surface.json
#   timestamp: 2024-09-20T00:27:05+00:00

from __future__ import annotations

from typing import Any, List, Optional

from oceanum.eidos._basemodel import EidosModel
from pydantic import ConfigDict, Field

from .. import features


class Offset(EidosModel):
    """
    Offsets for the model
    """

    model_config = ConfigDict(
        extra='forbid',
    )
    xoffset: Optional[float] = Field(0, title='X offset')
    yoffset: Optional[float] = Field(0, title='Y offset')
    pitch: Optional[float] = Field(0, title='Pitch offset')
    zoffset: Optional[float] = Field(0, title='Heave offset')
    roll: Optional[float] = Field(0, title='Roll offset')
    heading: Optional[float] = Field(0, title='Heading')
    speed: Optional[float] = Field(0, title='Speed')
    """
    Speed of the floater in m/s
    """
    scale: Optional[float] = Field(1, title='Scale')
    """
    Uniform Scale factor
    """
    xscale: Optional[float] = Field(0, title='X scale')
    """
    Scale factor in x direction
    """
    yscale: Optional[float] = Field(0, title='Y scale')
    """
    Scale factor in y direction
    """
    zscale: Optional[float] = Field(0, title='Z scale')
    """
    Scale factor in z direction
    """


class SeaSurfaceLayerDatakeys(EidosModel):
    """
    Mapping from data variables to amplitude and phase
    """

    model_config = ConfigDict(
        extra='allow',
    )
    f: str = Field(..., title='Frequency')
    d: str = Field(..., title='Direction')
    efth: str = Field(..., title='Spectral variance')


class SeaSurfaceRaoDatakeys(EidosModel):
    """
    Mapping from data variables to amplitude and phase of motions
    """

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
    """
    Response Amplitude Operator
    """

    model_config = ConfigDict(
        extra='allow',
    )
    datakeys: SeaSurfaceRaoDatakeys
    data: str = Field(..., title='Data')
    """
    Name of the data source
    """


class Floater(EidosModel):
    """
    Floating object
    """

    id: str = Field(..., title='ID')
    """
    Unique identifier for the floater
    """
    name: Optional[str] = Field(None, title='Name')
    """
    Name of the floater
    """
    position: Optional[features.Point] = None
    gltf: str = Field(..., title='GLTF model')
    """
    name or URL of GLTF model
    """
    style: Optional[Any] = None
    offsets: Optional[List[Offset]] = None
    """
    Array of position offsets, one for each model instance
    """
    rao: Optional[Rao] = Field(None, title='RAO')
    """
    Response Amplitude Operator
    """


class SeaSurfaceLayerSpec(EidosModel):
    """
    Specification for Sea surface layer
    """

    model_config = ConfigDict(
        extra='forbid',
    )
    datakeys: SeaSurfaceLayerDatakeys
    minzoom: Optional[float] = Field(13, title='Minimum zoom')
    """
    Minimum zoom to show sea surface
    """
    zscale: Optional[float] = Field(1, title='Vertical scale')
    """
    Vertical scale exageration
    """
    elevation: Optional[float] = Field(0, title='Sea level elevation')
    """
    Elevation of mean sea level in metres
    """
    floaters: Optional[List[Floater]] = Field([], title='Floaters')
    """
    List of floating objects
    """
