# generated by datamodel-codegen:
#   filename:  oceanql.json
#   timestamp: 2024-05-17T07:49:31+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from oceanum.eidos._basemodel import EidosModel
from pydantic import Field
from typing_extensions import Literal


class AggregateOps(str, Enum):
    mean = 'mean'
    min = 'min'
    max = 'max'
    std = 'std'
    sum = 'sum'


class BaseModel(EidosModel):
    """
    usage docs: https://docs.pydantic.dev/2.0/usage/models/

        A base class for creating Pydantic models.

        Attributes:
            __class_vars__: The names of classvars defined on the model.
            __private_attributes__: Metadata about the private attributes of the model.
            __signature__: The signature for instantiating the model.

            __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
            __pydantic_core_schema__: The pydantic-core schema used to build the SchemaValidator and SchemaSerializer.
            __pydantic_custom_init__: Whether the model has a custom `__init__` function.
            __pydantic_decorators__: Metadata containing the decorators defined on the model.
                This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
            __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
                __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
            __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
            __pydantic_post_init__: The name of the post-init method for the model, if defined.
            __pydantic_root_model__: Whether the model is a `RootModel`.
            __pydantic_serializer__: The pydantic-core SchemaSerializer used to dump instances of the model.
            __pydantic_validator__: The pydantic-core SchemaValidator used to validate instances of the model.

            __pydantic_extra__: An instance attribute with the values of extra fields from validation when
                `model_config['extra'] == 'allow'`.
            __pydantic_fields_set__: An instance attribute with the names of fields explicitly specified during validation.
            __pydantic_private__: Instance attribute with the values of private attributes set on the model instance.

    """


class CoordSelector(EidosModel):
    coord: str = Field(..., title='Coordinate name')
    values: List[Union[str, int, float]] = Field(
        ..., title='List of coordinate values to select by'
    )


class Function(EidosModel):
    id: str = Field(..., title='Function id')
    args: Dict[str, Any] = Field(..., title='function arguments')
    vselect: Optional[List[str]] = Field(None, title='Apply function to variables')
    replace: Optional[bool] = Field(False, title='Replace input dataset')


class GeoFilterType(str, Enum):
    """
    Type of the geofilter. Can be one of:
    - 'feature': Select with a geojson feature
    - 'bbox': Select with a bounding box
    - 'radius': Select within radius of point
    """

    feature = 'feature'
    radius = 'radius'
    bbox = 'bbox'


class LineString(EidosModel):
    """
    LineString Model
    """

    bbox: Optional[List] = Field(None, title='Bbox')
    type: Literal['LineString'] = Field(..., title='Type')
    coordinates: List[List] = Field(..., min_length=2, title='Coordinates')


class MultiLineString(EidosModel):
    """
    MultiLineString Model
    """

    bbox: Optional[List] = Field(None, title='Bbox')
    type: Literal['MultiLineString'] = Field(..., title='Type')
    coordinates: List[List[List]] = Field(..., title='Coordinates')


class MultiPoint(EidosModel):
    """
    MultiPoint Model
    """

    bbox: Optional[List] = Field(None, title='Bbox')
    type: Literal['MultiPoint'] = Field(..., title='Type')
    coordinates: List[List] = Field(..., title='Coordinates')


class MultiPolygon(EidosModel):
    """
    MultiPolygon Model
    """

    bbox: Optional[List] = Field(None, title='Bbox')
    type: Literal['MultiPolygon'] = Field(..., title='Type')
    coordinates: List[List[List[List]]] = Field(..., title='Coordinates')


class Point(EidosModel):
    """
    Point Model
    """

    bbox: Optional[List] = Field(None, title='Bbox')
    type: Literal['Point'] = Field(..., title='Type')
    coordinates: List = Field(..., title='Coordinates')


class Polygon(EidosModel):
    """
    Polygon Model
    """

    bbox: Optional[List] = Field(None, title='Bbox')
    type: Literal['Polygon'] = Field(..., title='Type')
    coordinates: List[List[List]] = Field(..., title='Coordinates')


class ResampleType(str, Enum):
    mean = 'mean'
    nearest = 'nearest'


class TimeFilterType(str, Enum):
    """
    Type of the timefilter. Can be one of:
    - 'range': Select within a time range
    """

    range = 'range'
    series = 'series'


class Aggregate(EidosModel):
    operations: Optional[List[AggregateOps]] = Field(
        ['mean'], title='Aggregate operations to perform'
    )
    spatial: Optional[bool] = Field(True, title='Aggregate over spatial filter')
    temporal: Optional[bool] = Field(True, title='Aggregate over temporal filter')


class Feature(EidosModel):
    """
    Feature Model
    """

    bbox: Optional[List] = Field(None, title='Bbox')
    type: Literal['Feature'] = Field(..., title='Type')
    geometry: Optional[
        Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]
    ] = Field(..., title='Geometry')
    properties: Optional[Union[Dict[str, Any], BaseModel]] = Field(
        ..., title='Properties'
    )
    id: Optional[Union[int, str]] = Field(None, title='Id')


class GeoFilter(EidosModel):
    type: Optional[GeoFilterType] = Field('bbox', title='GeoFilter type')
    geom: Union[List[float], Feature] = Field(..., title='bbox OR geojson Feature')
    resolution: Optional[float] = Field(0.0, title='Maximum spatial resolution of data')
    alltouched: Optional[bool] = Field(None, title='Include all touched grid pixels')


class TimeFilter(EidosModel):
    type: Optional[TimeFilterType] = Field('range', title='Timefilter type')
    times: List[Optional[str]] = Field(..., title='Time range or series')
    resolution: Optional[str] = Field('native', title='Temporal resolution of data')
    resample: Optional[ResampleType] = Field('mean', title='Resampling operator')


class OceanQuery(EidosModel):
    datasource: str = Field(..., title='The id of the datasource')
    parameters: Optional[Dict[str, Any]] = Field({}, title='Datasource parameters')
    description: Optional[str] = Field(None, title='Optional description of this query')
    variables: Optional[List[str]] = Field(None, title='List of selected variables')
    timefilter: Optional[TimeFilter] = Field(None, title='Time filter')
    geofilter: Optional[GeoFilter] = Field(None, title='Spatial filter or interpolator')
    coordfilter: Optional[List[CoordSelector]] = Field(
        None, title='List of additional coordinate filters'
    )
    crs: Optional[Union[int, str]] = Field(
        None, title='Spatial reference for filter and output'
    )
    aggregate: Optional[Aggregate] = Field(None, title='Aggregate operations')
    functions: Optional[List[Function]] = Field([], title='Functions')
    limit: Optional[int] = Field(None, title='Limit size of response')
    id: Optional[str] = Field(None, title='Unique ID of this query')