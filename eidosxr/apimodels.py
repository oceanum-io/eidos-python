"""Pydantic models for the EIDOS platform API responses.

These mirror the shapes returned by the ``spec-api`` and ``zarr-ingestion``
workers. Response models set ``extra='allow'`` where the endpoint is known to
return additional (sometimes undocumented) columns, so forward-compatible
fields do not break parsing.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SpecificationSummary(BaseModel):
    """An entry in ``GET /specifications`` (no ``spec`` body, no ``version``)."""

    id: str
    name: str
    description: Optional[str] = None
    account_id: Optional[str] = None
    is_public: bool
    template: bool
    created_by_user_id: str
    created_at: str
    updated_at: str


class Specification(BaseModel):
    """A full specification (``GET``/``POST /specifications/:id``)."""

    id: str
    name: str
    description: Optional[str] = None
    account_id: Optional[str] = None
    is_public: bool
    spec: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    version: int

    def to_eidos(self):
        """Parse ``spec`` into a live :class:`eidosxr.Eidos` model.

        The returned model's change checkpoint is the fetched server state, so
        editing it and calling :meth:`EidosConnection.update_specification`
        sends only the delta.
        """
        from eidosxr.base import Eidos

        return Eidos.from_dict(self.spec or {})


class SpecificationList(BaseModel):
    """The envelope returned by ``GET /specifications``."""

    specifications: List[SpecificationSummary]
    total: int
    limit: int
    offset: int


class PatchResult(BaseModel):
    """The result of ``PATCH /specifications/:id``."""

    id: str
    spec: Optional[Dict[str, Any]] = None
    version: int
    updated_at: str


class Template(BaseModel):
    """A reusable node template."""

    id: str
    name: str
    description: str = ""
    category: str
    node_type: str
    icon: Optional[str] = None
    scope: str
    account_id: Optional[str] = None
    created_by_user_id: Optional[str] = None
    spec_json: Dict[str, Any]
    created_at: str
    updated_at: str

    model_config = {"extra": "allow"}


class Dataset(BaseModel):
    """A zarr dataset in the ingestion service.

    ``is_public`` is only populated by ``GET /api/datasets/:id`` (the list
    endpoint omits it).
    """

    id: str
    original_filename: str
    name: Optional[str] = None
    description: Optional[str] = None
    coordkeys: Optional[Dict[str, str]] = None
    r2_zarr_uri: Optional[str] = None
    size_bytes: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    is_public: Optional[bool] = None

    model_config = {"extra": "allow"}


class DatasetMetadata(BaseModel):
    """Per-level grid metadata for a completed dataset."""

    levels: List[Dict[str, Any]]
    zmetadata: Dict[str, Any]


class AssetRef(BaseModel):
    """The reference returned by ``POST /api/assets``."""

    type: str
    id: str
    r2_key: str
    url: str


__all__ = [
    "SpecificationSummary",
    "Specification",
    "SpecificationList",
    "PatchResult",
    "Template",
    "Dataset",
    "DatasetMetadata",
    "AssetRef",
]
