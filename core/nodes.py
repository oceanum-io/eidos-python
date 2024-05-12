# generated by datamodel-codegen:
#   filename:  core/nodes.json
#   timestamp: 2024-05-12T22:42:44+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import ConfigDict, Field, RootModel

from eidos._basemodel import EidosModel

from ..viewnodes import document, plot, world


class EidosNodeSpecification(RootModel[Any]):
    root: Any = Field(
        ..., description='EIDOS node specifications', title='EIDOS node specification'
    )


class NodeType(str, Enum):
    world = 'world'
    plot = 'plot'
    document = 'document'
    grid = 'grid'


class GridLayout(EidosModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    w: int = Field(..., description='Width in columns')
    h: int = Field(..., description='height in rows')
    x: int = Field(..., description='Origin in columns')
    y: int = Field(..., description='Origin in rows from top')


class TabLayout(EidosModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    label: str = Field(..., description='Tab title label')
    icon: Optional[str] = Field(None, description='Tab title icon')


class GridSize(EidosModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    cols: int = Field(..., description='Number of columns in grid')
    rows: int = Field(..., description='Number of rows in grid')


class Node(EidosModel):
    id: str = Field(..., description='Unique ID of the node')
    nodeType: NodeType
    nodeSpec: Union[
        world.WorldView, plot.PlotView, document.DocumentView, GridNode, TabNode
    ] = Field(
        ..., description='Spec for node (worldview, plotable, document or grid/modal)'
    )
    gridLayout: Optional[GridLayout] = Field(
        None, description='Positioning of node in grid layout'
    )
    tabLayout: Optional[TabLayout] = Field(
        None, description='Configuration of nodes in tab layout'
    )


class Children(RootModel[List[Node]]):
    root: List[Node]


class GridNode(EidosModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    gridSize: GridSize
    children: List[Node]


class TabNode(EidosModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    activeTab: Optional[str] = None
    children: List[Node]


class ModalNode(Node):
    trigger: str = Field(..., description='event ID that triggers modal')
    height: Optional[int] = Field(100, description='Height of modal dialog (pixels)')
    width: Optional[Union[int, str]] = None
    title: Optional[str] = None


Node.model_rebuild()
ModalNode.model_rebuild()
