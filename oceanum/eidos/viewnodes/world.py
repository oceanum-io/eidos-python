# generated by datamodel-codegen:
#   filename:  viewnodes/world.json
#   timestamp: 2024-05-17T07:49:31+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from oceanum.eidos._basemodel import EidosModel
from pydantic import ConfigDict, Field, RootModel

from .. import features
from ..core import state
from . import document, plot


class BaselayerType(str, Enum):
    """
    Base layer type
    """

    oceanum = 'oceanum'
    terrain = 'terrain'


class LayerSpec(EidosModel):
    """
    Specification for world layer - depends on layer type
    """


class ViewType(str, Enum):
    """
    Type of world view
    """

    map = 'map'
    globe = 'globe'


class View(EidosModel):
    """
    State of the map view
    """

    viewType: Optional[ViewType] = 'map'
    """
    Type of world view
    """
    longitude: float
    """
    Longitude of view center
    """
    latitude: float
    """
    Latitude of view center
    """
    pitch: Optional[float] = 0
    """
    Pitch angle of view
    """
    bearing: Optional[float] = 0
    """
    Bearing angle of view
    """
    maxZoom: Optional[float] = 20
    """
    Maximum zoom level
    """
    zoom: Optional[float] = 0
    """
    Zoom level
    """
    maxPitch: Optional[float] = 60
    """
    Maximum pitch angle
    """


class Geometry(
    RootModel[
        Union[
            features.Point, features.LineString, features.Polygon, features.MultiPoint
        ]
    ]
):
    root: Union[
        features.Point, features.LineString, features.Polygon, features.MultiPoint
    ]


class Colormap(EidosModel):
    """
    Scale and domain argument for chroma.scale
    """

    colorscale: Optional[Union[List[str], str]] = None
    domain: Optional[List[Union[float, str]]] = None


class Color(RootModel[Union[List[float], str]]):
    root: Union[List[float], str] = Field(..., title='Color definition')


class Visibility(str, Enum):
    """
    When to show labels
    """

    always = 'always'
    click = 'click'
    hover = 'hover'


class Label(EidosModel):
    """
    Label properties
    """

    format: Optional[str] = None
    """
    Label format string as templated markdown. {{value}} if the layer value
    """
    visibility: Optional[Visibility] = None
    """
    When to show labels
    """
    activeOnly: Optional[bool] = None
    """
    Only show labels for active layer
    """


class HoverInfo(EidosModel):
    """
    Properties for tooltip shown on hover
    """

    template: str
    """
    Tooltip as Handlebars template. The picked object is passed as the render context.
    """


class StyleAccessorString(RootModel[str]):
    root: str = Field(..., title='Style accessor constant string')
    """
    Constant value
    """


class StyleAccessorNumber(RootModel[float]):
    root: float = Field(..., title='Style accessor constant number')
    """
    Constant value
    """


class StyleAccessorArray(RootModel[List[float]]):
    """
    Array of constant values
    """

    root: List[float] = Field(..., title='Style accessor constant array')
    """
    Array of constant values
    """


class StyleAccessorFunction(EidosModel):
    """
    Accessor function
    """

    function: Optional[str] = None
    """
    Accessor function identifier
    """
    args: Optional[List[str]] = None
    """
    Arguments for accessor function
    """


class Visibility1(str, Enum):
    """
    When to show panel
    """

    always = 'always'
    click = 'click'
    hover = 'hover'


class Relative(str, Enum):
    panel = 'panel'
    location = 'location'


class Position(EidosModel):
    """
    Position of panel
    """

    relative: Optional[Relative] = None
    top: Optional[float] = None
    """
    top position offset in pixels
    """
    left: Optional[float] = None
    """
    left position offset in pixels
    """
    bottom: Optional[float] = None
    """
    bottom position offset in pixels
    """
    right: Optional[float] = None
    """
    right position offset in pixels
    """


class Type(str, Enum):
    """
    Control type
    """

    points = 'points'
    polygon = 'polygon'
    bbox = 'bbox'
    pointRadius = 'pointRadius'
    dragDrop = 'dragDrop'


class CursorOffset(EidosModel):
    """
    Cursor offset
    """

    x: Optional[float] = 0
    y: Optional[float] = 0


class Icon(EidosModel):
    """
    Icon URLs
    """

    default: str
    """
    Default icon URL
    """
    hover: Optional[str] = None
    """
    Active hover icon URL
    """
    dark: Optional[str] = None
    """
    Dark theme icon URL
    """
    cursorOffset: Optional[CursorOffset] = None
    """
    Cursor offset
    """


class Control(EidosModel):
    """
    Control properties
    """

    type: Type
    """
    Control type
    """
    id: str
    """
    Control id
    """
    active: Optional[bool] = None
    """
    Control active state
    """
    state: Optional[Dict[str, Any]] = None
    """
    Control state
    """
    icon: Optional[Icon] = None
    """
    Icon URLs
    """
    tooltip: Optional[str] = None
    """
    Tooltip text
    """


class Controls(RootModel[List[Control]]):
    """
    Control array
    """

    root: List[Control] = Field(..., title='Controls definition')
    """
    Control array
    """


class Legend(EidosModel):
    """
    Legend properties
    """

    labels: Optional[Union[List[str], List[float]]] = None


class StyleAccessor(
    RootModel[
        Union[
            StyleAccessorString,
            StyleAccessorNumber,
            StyleAccessorFunction,
            StyleAccessorArray,
        ]
    ]
):
    root: Union[
        StyleAccessorString,
        StyleAccessorNumber,
        StyleAccessorFunction,
        StyleAccessorArray,
    ] = Field(..., title='Style accessor definition')
    """
    Style properties
    """


class Layer(EidosModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: str
    """
    Unique id of layer
    """
    name: Optional[str] = None
    """
    Human readable name of layer
    """
    layerType: str
    """
    Name of worldlayer type
    """
    dataId: Optional[str] = None
    """
    Name of data
    """
    label: Optional[Label] = None
    panel: Optional[Panel] = None
    visible: Optional[bool] = True
    exclusive: Optional[bool] = False
    layerSpec: Any


class WorldView(EidosModel):
    """
    Specification for world view environmental interaction and display
    """

    model_config = ConfigDict(
        extra='forbid',
    )
    layers: List[Layer]
    """
    Layers displayed on this map
    """
    baselayerType: Optional[BaselayerType] = None
    """
    Base layer type
    """
    viewState: Optional[View] = None
    currentTime: Optional[state.CurrentTime] = None
    currentContext: Optional[state.CurrentContext] = None
    timeControl: Optional[state.TimeControl] = None
    mapControls: Optional[Controls] = None


class Panel(EidosModel):
    """
    Panel properties
    """

    format: Optional[str] = None
    """
    Label format string as templated markdown. {{value}} if the layer value
    """
    visibility: Optional[Visibility1] = None
    """
    When to show panel
    """
    position: Optional[Position] = None
    """
    Position of panel
    """
    spec: Optional[Union[WorldView, plot.PlotView, document.DocumentView]] = None
    """
    EIDOS panel specification
    """


Layer.model_rebuild()
