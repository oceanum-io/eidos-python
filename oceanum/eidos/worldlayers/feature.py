# generated by datamodel-codegen:
#   filename:  worldlayers/feature.json
#   timestamp: 2024-05-28T21:53:23+00:00

from __future__ import annotations

from typing import Any, Dict, List, Optional

from oceanum.eidos._basemodel import EidosModel
from pydantic import ConfigDict, Field

from ..core import state
from ..viewnodes import world


class FeatureDatakeys(EidosModel):
    """
    Mapping from data variables to x,y and c(scalar value)
    """

    t: Optional[str] = None
    z: Optional[str] = None


class FeatureStyle(EidosModel):
    """
    Style properties for Feature Layer features
    """

    model_config = ConfigDict(
        extra='forbid',
    )
    opacity: Optional[float] = None
    """
    Opacity of the layer. Default: 1.
    """
    pointType: Optional[str] = None
    """
    How to render Point and MultiPoint features in the data. Supported types are 'circle', 'icon', 'text'. To use more than one type, join the names with '+', for example 'icon+text'. Default: 'circle'.
    """
    filled: Optional[bool] = None
    """
    Whether to draw filled polygons (solid fill) and points (circles). Default: true.
    """
    getFillColor: Optional[world.StyleAccessor] = None
    """
    The solid color of the polygon and points (circles) in the format [r, g, b, [a]]. Default: [0, 0, 0, 255].
    """
    stroked: Optional[bool] = None
    """
    Whether to draw an outline around polygons and points (circles). Default: true.
    """
    getLineColor: Optional[world.StyleAccessor] = None
    """
    The rgba color of a line in the format [r, g, b, [a]]. Default: [0, 0, 0, 255].
    """
    getLineWidth: Optional[world.StyleAccessor] = None
    """
    The width of a line in units specified by lineWidthUnits. Default: 1.
    """
    lineWidthUnits: Optional[str] = None
    """
    The units of the line width, one of 'meters', 'common', and 'pixels'. Default: 'meters'.
    """
    lineWidthScale: Optional[float] = None
    """
    A multiplier that is applied to all line widths. Default: 1.
    """
    lineWidthMinPixels: Optional[float] = None
    """
    The minimum line width in pixels. Default: 0.
    """
    lineWidthMaxPixels: Optional[float] = None
    """
    The maximum line width in pixels. Default: 9007199254740991.
    """
    lineCapRounded: Optional[bool] = None
    """
    Type of line caps. If true, draw round caps. Otherwise draw square caps. Default: false.
    """
    lineJointRounded: Optional[bool] = None
    """
    Type of line joint. If true, draw round joints. Otherwise draw miter joints. Default: false.
    """
    lineMiterLimit: Optional[float] = None
    """
    The maximum extent of a joint in ratio to the stroke width. Default: 4.
    """
    lineBillboard: Optional[bool] = None
    """
    If true, extrude the line in screen space (width always faces the camera). Default: false.
    """
    extruded: Optional[bool] = None
    """
    Extrude Polygon and MultiPolygon features along the z-axis if set to true. Default: false.
    """
    wireframe: Optional[bool] = None
    """
    Whether to generate a line wireframe of the hexagon. Default: false.
    """
    getElevation: Optional[world.StyleAccessor] = None
    """
    The elevation of a polygon feature (when extruded is true). Default: 1000.
    """
    elevationScale: Optional[float] = None
    """
    Elevation multiplier. The final elevation is calculated by elevationScale * getElevation(d). Default: 1.
    """
    material: Optional[Dict[str, Any]] = None
    """
    An object that contains material props for lighting effect applied on extruded polygons. Default: {}.
    """
    field_full3d: Optional[bool] = Field(None, alias='_full3d')
    """
    Experimental property. When true, polygon tessellation will be performed on the plane with the largest area, instead of the xy plane. Default: false.
    """
    getPointRadius: Optional[world.StyleAccessor] = None
    """
    Radius of points when pointType is 'circle'. Default: 1.
    """
    pointRadiusUnits: Optional[str] = None
    """
    Units for point radius when pointType is 'circle'. Default: 'meters'.
    """
    pointRadiusScale: Optional[float] = None
    """
    Scale for point radius when pointType is 'circle'. Default: 1.
    """
    pointRadiusMinPixels: Optional[float] = None
    """
    Minimum point radius in pixels when pointType is 'circle'. Default: 0.
    """
    pointRadiusMaxPixels: Optional[float] = None
    """
    Maximum point radius in pixels when pointType is 'circle'. Default: 9007199254740991.
    """
    pointAntialiasing: Optional[bool] = None
    """
    Whether to use antialiasing for points when pointType is 'circle'. Default: true.
    """
    pointBillboard: Optional[bool] = None
    """
    If true, point is billboarded when pointType is 'circle'. Default: false.
    """
    iconAtlas: Optional[str] = None
    """
    URL of the icon atlas image when pointType is 'icon'. Default: null.
    """
    iconMapping: Optional[Dict[str, Any]] = None
    """
    Mapping of icon names to positions in the atlas when pointType is 'icon'. Default: {}.
    """
    getIcon: Optional[world.StyleAccessor] = None
    """
    Accessor for icon names when pointType is 'icon'. Default: f => f.properties.icon.
    """
    getIconSize: Optional[world.StyleAccessor] = None
    """
    Size of icons when pointType is 'icon'. Default: 1.
    """
    getIconColor: Optional[world.StyleAccessor] = None
    """
    Color of icons when pointType is 'icon'. Default: [0, 0, 0, 255].
    """
    getIconAngle: Optional[world.StyleAccessor] = None
    """
    Rotation angle of icons when pointType is 'icon'. Default: 0.
    """
    getIconPixelOffset: Optional[world.StyleAccessor] = None
    """
    Pixel offset of icons when pointType is 'icon'. Default: [0, 0].
    """
    iconSizeUnits: Optional[str] = None
    """
    Units for icon size when pointType is 'icon'. Default: 'pixels'.
    """
    iconSizeScale: Optional[float] = None
    """
    Scale for icon size when pointType is 'icon'. Default: 1.
    """
    iconSizeMinPixels: Optional[float] = None
    """
    Minimum icon size in pixels when pointType is 'icon'. Default: 0.
    """
    iconSizeMaxPixels: Optional[float] = None
    """
    Maximum icon size in pixels when pointType is 'icon'. Default: 9007199254740991.
    """
    iconBillboard: Optional[bool] = None
    """
    If true, icons are billboarded when pointType is 'icon'. Default: true.
    """
    iconAlphaCutoff: Optional[float] = None
    """
    Alpha cutoff for icons when pointType is 'icon'. Default: 0.05.
    """
    getText: Optional[world.StyleAccessor] = None
    """
    Accessor for text content when pointType is 'text'. Default: f => f.properties.text.
    """
    getTextColor: Optional[world.StyleAccessor] = None
    """
    Color of text when pointType is 'text'. Default: [0, 0, 0, 255].
    """
    getTextAngle: Optional[world.StyleAccessor] = None
    """
    Rotation angle of text when pointType is 'text'. Default: 0.
    """
    getTextSize: Optional[world.StyleAccessor] = None
    """
    Size of text when pointType is 'text'. Default: 32.
    """
    getTextAnchor: Optional[world.StyleAccessor] = None
    """
    Anchor position of text when pointType is 'text'. Default: 'middle'.
    """
    getTextAlignmentBaseline: Optional[world.StyleAccessor] = None
    """
    Alignment baseline of text when pointType is 'text'. Default: 'center'.
    """
    getTextPixelOffset: Optional[world.StyleAccessor] = None
    """
    Pixel offset of text when pointType is 'text'. Default: [0, 0].
    """
    getTextBackgroundColor: Optional[world.StyleAccessor] = None
    """
    Background color of text when pointType is 'text'. Default: [255, 255, 255, 255].
    """
    getTextBorderColor: Optional[world.StyleAccessor] = None
    """
    Border color of text when pointType is 'text'. Default: [0, 0, 0, 255].
    """
    getTextBorderWidth: Optional[world.StyleAccessor] = None
    """
    Border width of text when pointType is 'text'. Default: 0.
    """
    textSizeUnits: Optional[str] = None
    """
    Units for text size when pointType is 'text'. Default: 'pixels'.
    """
    textSizeScale: Optional[float] = None
    """
    Scale for text size when pointType is 'text'. Default: 1.
    """
    textSizeMinPixels: Optional[float] = None
    """
    Minimum text size in pixels when pointType is 'text'. Default: 0.
    """
    textSizeMaxPixels: Optional[float] = None
    """
    Maximum text size in pixels when pointType is 'text'. Default: 9007199254740991.
    """
    textCharacterSet: Optional[str] = None
    """
    Character set for text when pointType is 'text'. Default: 'ASCII chars 32-128'.
    """
    textFontFamily: Optional[str] = None
    """
    Font family for text when pointType is 'text'. Default: 'Monaco, monospace'.
    """
    textFontWeight: Optional[str] = None
    """
    Font weight for text when pointType is 'text'. Default: 'normal'.
    """
    textLineHeight: Optional[float] = None
    """
    Line height for text when pointType is 'text'. Default: 1.
    """
    textMaxWidth: Optional[float] = None
    """
    Maximum width for text when pointType is 'text'. Default: -1.
    """
    textWordBreak: Optional[str] = None
    """
    Word break setting for text when pointType is 'text'. Default: 'break-word'.
    """
    textBackground: Optional[bool] = None
    """
    Whether text has a background when pointType is 'text'. Default: false.
    """
    textBackgroundPadding: Optional[List[float]] = None
    """
    Padding for text background when pointType is 'text'. Default: [0, 0].
    """
    textOutlineColor: Optional[world.StyleAccessor] = None
    """
    Outline color for text when pointType is 'text'. Default: [0, 0, 0, 255].
    """
    textOutlineWidth: Optional[float] = None
    """
    Outline width for text when pointType is 'text'. Default: 0.
    """
    textBillboard: Optional[bool] = None
    """
    If true, text is billboarded when pointType is 'text'. Default: true.
    """
    textFontSettings: Optional[Dict[str, Any]] = None
    """
    Additional font settings for text when pointType is 'text'. Default: {}.
    """


class FeatureLayerSpec(EidosModel):
    """
    Specification for Feature overlay layer
    """

    model_config = ConfigDict(
        extra='forbid',
    )
    hoverInfo: Optional[world.HoverInfo] = None
    timeSelect: Optional[state.TimeSelect] = None
    geometry: Optional[world.Geometry] = None
    colormap: Optional[world.Colormap] = None
    legend: Optional[world.Legend] = None
    datakeys: Optional[FeatureDatakeys] = None
    style: FeatureStyle
