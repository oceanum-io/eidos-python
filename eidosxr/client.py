"""Client for the EIDOS platform API.

:class:`EidosConnection` is a thin, typed transport over the two EIDOS platform
workers:

* **spec-api** (``https://api.eidosxr.com``) — specification and template CRUD,
  and RFC-6902 JSON-Patch updates.
* **zarr-ingestion-service** — zarr dataset and asset storage.

Both authenticate with a single bearer token, which may be a Supabase user JWT
**or** an ``ek_`` Oceanum API key.

The client speaks the :class:`eidosxr.Eidos` model natively. The intended edit
loop is::

    conn = EidosConnection(token="ek_...")
    record = conn.get_specification(spec_id)     # -> Specification (has .version)
    spec = record.to_eidos()                     # -> live Eidos model
    spec.root.title = "Updated"                  # edit the model
    conn.update_specification(spec_id, spec, if_match=record.version)

``update_specification`` calls ``spec.patch()`` to compute the JSON Patch — note
that is *destructive* (it advances the model's change checkpoint), so it is
called exactly once per update.
"""

from __future__ import annotations

import os
from typing import Any, BinaryIO, Dict, List, Mapping, Optional, Union

import requests

from .apimodels import (
    AssetRef,
    Dataset,
    DatasetMetadata,
    PatchResult,
    Specification,
    SpecificationList,
    Template,
)
from .base import Eidos
from .consistency import (
    compare_stores,
    load_consolidated_metadata,
)
from .exceptions import EidosError, NotFound, error_from_response

DEFAULT_SERVICE = "https://api.eidosxr.com"

#: max body accepted by a single ingestion zarr PUT (server-enforced).
ZARR_OBJECT_MAX_BYTES = 64 * 1024 * 1024

JsonPatch = List[Dict[str, Any]]


class EidosConnection:
    """A connection to the EIDOS platform API.

    Args:
        token: bearer token — a Supabase JWT or an ``ek_`` API key. Falls back
            to the ``EIDOS_TOKEN`` environment variable.
        service: base URL of the spec-api. Falls back to ``EIDOS_SERVICE`` then
            ``https://api.eidosxr.com``.
        ingestion_service: base URL of the zarr-ingestion service. Falls back to
            ``EIDOS_INGESTION_SERVICE``. Required only for dataset/asset calls.
        session: an optional pre-configured :class:`requests.Session`.
    """

    def __init__(
        self,
        token: Optional[str] = None,
        *,
        service: Optional[str] = None,
        ingestion_service: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.token = token or os.environ.get("EIDOS_TOKEN")
        if not self.token:
            raise ValueError(
                "An EIDOS API token is required — pass token= or set EIDOS_TOKEN."
            )
        self.service = (
            service or os.environ.get("EIDOS_SERVICE") or DEFAULT_SERVICE
        ).rstrip("/")
        _ingestion = ingestion_service or os.environ.get("EIDOS_INGESTION_SERVICE")
        self.ingestion_service = _ingestion.rstrip("/") if _ingestion else None
        self._session = session or requests.Session()

    # -- internal --------------------------------------------------------
    def _headers(self, extra: Optional[Mapping[str, str]] = None) -> Dict[str, str]:
        headers = {"Authorization": f"Bearer {self.token}"}
        if extra:
            headers.update(extra)
        return headers

    def _request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Mapping[str, str]] = None,
        json_body: Any = None,
        data: Any = None,
        files: Any = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> requests.Response:
        response = self._session.request(
            method,
            url,
            headers=self._headers(headers),
            json=json_body,
            data=data,
            files=files,
            params=params,
        )
        if not response.ok:
            raise error_from_response(response)
        return response

    def _ingestion_url(self, path: str) -> str:
        if not self.ingestion_service:
            raise EidosError(
                "ingestion_service is not configured — pass ingestion_service= or "
                "set EIDOS_INGESTION_SERVICE to use dataset/asset endpoints."
            )
        return f"{self.ingestion_service}{path}"

    @staticmethod
    def _drop_none(mapping: Mapping[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in mapping.items() if v is not None}

    # -- specifications --------------------------------------------------
    def list_specifications(
        self, limit: int = 50, offset: int = 0
    ) -> SpecificationList:
        """List the caller's specifications plus all public ones."""
        response = self._request(
            "GET",
            f"{self.service}/specifications",
            params={"limit": limit, "offset": offset},
        )
        return SpecificationList.model_validate(response.json())

    def create_specification(
        self,
        spec: Union[Eidos, Mapping[str, Any], None] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        account_id: Optional[str] = None,
    ) -> Specification:
        """Create a specification.

        ``spec`` may be an :class:`eidosxr.Eidos`, a plain dict, or ``None``. When
        it is an ``Eidos`` and ``name`` is not given, the spec's own ``name`` is
        used.
        """
        spec_doc: Optional[Dict[str, Any]]
        if isinstance(spec, Eidos):
            spec_doc = spec.spec()
            name = name or spec.name
        elif spec is None:
            spec_doc = None
        else:
            spec_doc = dict(spec)
        if not name:
            raise ValueError("A specification name is required.")
        body = self._drop_none(
            {
                "name": name,
                "description": description,
                "account_id": account_id,
                "spec": spec_doc,
            }
        )
        response = self._request(
            "POST", f"{self.service}/specifications", json_body=body
        )
        return Specification.model_validate(response.json())

    def get_specification(self, spec_id: str) -> Specification:
        """Fetch a full specification (including ``spec`` and ``version``)."""
        response = self._request("GET", f"{self.service}/specifications/{spec_id}")
        return Specification.model_validate(response.json())

    def get_specification_model(self, spec_id: str) -> Eidos:
        """Fetch a specification and return its ``spec`` as a live
        :class:`eidosxr.Eidos` model, checkpointed at the server state."""
        return self.get_specification(spec_id).to_eidos()

    def patch_specification(
        self,
        spec_id: str,
        operations: JsonPatch,
        *,
        if_match: Optional[Union[int, str]] = None,
    ) -> PatchResult:
        """Apply a raw RFC-6902 JSON Patch to a specification.

        Pass ``if_match`` (the version from a prior read) for optimistic
        concurrency; a mismatch raises :class:`PreconditionFailed` (412).
        """
        headers = {}
        if if_match is not None:
            headers["If-Match"] = f'"{if_match}"'
        response = self._request(
            "PATCH",
            f"{self.service}/specifications/{spec_id}",
            json_body=operations,
            headers=headers or None,
        )
        return PatchResult.model_validate(response.json())

    def update_specification(
        self,
        spec_id: str,
        spec: Eidos,
        *,
        if_match: Optional[Union[int, str]] = None,
    ) -> Optional[PatchResult]:
        """Persist local edits to an :class:`eidosxr.Eidos` model.

        Computes the JSON Patch from the model's change checkpoint via
        ``spec.patch()`` (called once — it is destructive) and PATCHes it.
        Returns ``None`` if the model has no pending changes.
        """
        operations = spec.patch()
        if not operations:
            return None
        return self.patch_specification(spec_id, operations, if_match=if_match)

    def delete_specification(self, spec_id: str) -> None:
        """Delete a specification."""
        self._request("DELETE", f"{self.service}/specifications/{spec_id}")

    # -- templates -------------------------------------------------------
    def list_templates(
        self,
        *,
        node_type: Optional[str] = None,
        owned: Optional[bool] = None,
    ) -> List[Template]:
        """List templates visible to the caller (excludes archived)."""
        params = self._drop_none(
            {
                "node_type": node_type,
                "owned": None if owned is None else str(owned).lower(),
            }
        )
        response = self._request(
            "GET", f"{self.service}/templates", params=params or None
        )
        return [Template.model_validate(item) for item in response.json()]

    def create_template(
        self,
        *,
        name: str,
        node_type: str,
        spec_json: Mapping[str, Any],
        description: Optional[str] = None,
        category: Optional[str] = None,
        icon: Optional[str] = None,
        scope: Optional[str] = None,
        account_id: Optional[str] = None,
    ) -> Template:
        """Create a template from an explicit ``spec_json`` node subtree."""
        body = self._drop_none(
            {
                "name": name,
                "node_type": node_type,
                "spec_json": dict(spec_json),
                "description": description,
                "category": category,
                "icon": icon,
                "scope": scope,
                "account_id": account_id,
            }
        )
        response = self._request("POST", f"{self.service}/templates", json_body=body)
        return Template.model_validate(response.json())

    def create_template_from_node(
        self,
        *,
        name: str,
        node_type: str,
        node_data: Mapping[str, Any],
        description: Optional[str] = None,
        category: Optional[str] = None,
        icon: Optional[str] = None,
        scope: Optional[str] = None,
        account_id: Optional[str] = None,
    ) -> Template:
        """Create a template from a live node (``node_data``); the server strips
        the node's ``id`` and stores the rest as ``spec_json``."""
        body = self._drop_none(
            {
                "name": name,
                "node_type": node_type,
                "node_data": dict(node_data),
                "description": description,
                "category": category,
                "icon": icon,
                "scope": scope,
                "account_id": account_id,
            }
        )
        response = self._request(
            "POST", f"{self.service}/templates/from-node", json_body=body
        )
        return Template.model_validate(response.json())

    def update_template(
        self,
        template_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Template:
        """Update a template's ``name``/``description`` (the only mutable fields)."""
        body = self._drop_none({"name": name, "description": description})
        if not body:
            raise ValueError("Provide at least one of name/description to update.")
        response = self._request(
            "PATCH", f"{self.service}/templates/{template_id}", json_body=body
        )
        return Template.model_validate(response.json())

    def archive_template(self, template_id: str) -> None:
        """Soft-delete (archive) a template."""
        self._request("POST", f"{self.service}/templates/{template_id}/archive")

    def delete_template(self, template_id: str) -> None:
        """Permanently delete a template."""
        self._request("DELETE", f"{self.service}/templates/{template_id}")

    # -- datasets (ingestion) --------------------------------------------
    def list_datasets(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dataset]:
        """List the caller's zarr datasets."""
        params = self._drop_none({"status": status, "limit": limit, "offset": offset})
        response = self._request(
            "GET", self._ingestion_url("/api/datasets"), params=params
        )
        return [Dataset.model_validate(item) for item in response.json()]

    def get_dataset(self, dataset_id: str) -> Dataset:
        """Fetch a single dataset (public datasets are readable anonymously)."""
        response = self._request(
            "GET", self._ingestion_url(f"/api/datasets/{dataset_id}")
        )
        return Dataset.model_validate(response.json())

    def update_dataset(
        self,
        dataset_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        coordkeys: Optional[Mapping[str, str]] = None,
    ) -> Dataset:
        """Update a dataset's ``name``/``description``/``coordkeys``."""
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if coordkeys is not None:
            body["coordkeys"] = dict(coordkeys)
        if not body:
            raise ValueError("Provide at least one field to update.")
        response = self._request(
            "PATCH",
            self._ingestion_url(f"/api/datasets/{dataset_id}"),
            json_body=body,
        )
        return Dataset.model_validate(response.json())

    def create_empty_dataset(
        self,
        original_filename: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Allocate an empty dataset row (step 1 of client-direct ingestion).

        Returns ``{"dataset_id": ..., "status": "processing"}``.
        """
        body = self._drop_none(
            {
                "original_filename": original_filename,
                "name": name,
                "description": description,
            }
        )
        response = self._request(
            "POST", self._ingestion_url("/api/datasets/empty"), json_body=body
        )
        return response.json()

    def put_zarr_object(self, dataset_id: str, object_path: str, data: bytes) -> None:
        """Write one object into a dataset's zarr store (step 2 of ingestion).

        ``object_path`` is a store-relative key such as ``.zmetadata`` or
        ``0/hs/0.0``. Bodies are capped at 64 MiB.
        """
        if len(data) > ZARR_OBJECT_MAX_BYTES:
            raise ValueError(
                f"zarr object exceeds the {ZARR_OBJECT_MAX_BYTES}-byte limit; "
                "split it into smaller chunks."
            )
        self._request(
            "PUT",
            self._ingestion_url(f"/api/datasets/{dataset_id}/zarr/{object_path}"),
            data=data,
            headers={
                "Content-Type": "application/octet-stream",
                "Content-Length": str(len(data)),
            },
        )

    def finalize_dataset(
        self,
        dataset_id: str,
        *,
        size_bytes: int,
        coordkeys: Optional[Mapping[str, str]] = None,
    ) -> Dict[str, Any]:
        """Finalize a client-direct dataset (step 3): run the quota check and
        mark it ``completed``."""
        body: Dict[str, Any] = {"size_bytes": size_bytes}
        if coordkeys is not None:
            body["coordkeys"] = dict(coordkeys)
        response = self._request(
            "POST",
            self._ingestion_url(f"/api/datasets/{dataset_id}/finalize"),
            json_body=body,
        )
        return response.json()

    def get_dataset_metadata(self, dataset_id: str) -> DatasetMetadata:
        """Fetch per-level grid metadata for a completed dataset."""
        response = self._request(
            "GET", self._ingestion_url(f"/api/datasets/{dataset_id}/metadata")
        )
        return DatasetMetadata.model_validate(response.json())

    def get_zarr_object(self, dataset_id: str, object_path: str) -> bytes:
        """Read one object from a completed dataset's zarr store."""
        response = self._request(
            "GET",
            self._ingestion_url(f"/api/datasets/{dataset_id}/zarr/{object_path}"),
        )
        return response.content

    # -- assets ----------------------------------------------------------
    def upload_asset(
        self, file: Union[BinaryIO, bytes], *, filename: str = "asset"
    ) -> AssetRef:
        """Upload an asset (multipart ``file`` field). Returns its reference."""
        response = self._request(
            "POST",
            self._ingestion_url("/api/assets"),
            files={"file": (filename, file)},
        )
        return AssetRef.model_validate(response.json()["ref"])

    def get_asset(self, asset_id: str) -> bytes:
        """Download an asset's bytes."""
        response = self._request("GET", self._ingestion_url(f"/api/assets/{asset_id}"))
        return response.content

    # -- consistency -----------------------------------------------------
    def check_put_consistency(
        self,
        dataset_id: str,
        store: Mapping[str, bytes],
        *,
        mode: str = "replace",
        append_dim: Optional[str] = None,
    ) -> None:
        """Verify a zarr ``store`` is consistent with an existing dataset for the
        intended write verb, before uploading it.

        Args:
            dataset_id: the existing (completed) dataset to check against.
            store: the zarr store to write, as a mapping of ``key -> bytes``.
            mode: ``"replace"`` (PUT — coordinate structure must match exactly),
                ``"append"`` (PATCH — the ``append_dim`` coordinate must extend
                the existing axis monotonically and without overlap; other
                coordinates must match), or ``"clobber"`` (POST — no check).
            append_dim: the dimension being appended (required for ``append``).

        Raises:
            ConsistencyError: if the store is incompatible for ``mode``.
        """
        if mode == "clobber":
            return

        def existing_get(path: str) -> Optional[bytes]:
            try:
                return self.get_zarr_object(dataset_id, path)
            except NotFound:
                return None

        existing_meta = load_consolidated_metadata(existing_get)
        new_meta = load_consolidated_metadata(store.get)
        compare_stores(
            existing_meta,
            new_meta,
            existing_get,
            store.get,
            mode=mode,
            append_dim=append_dim,
        )


__all__ = ["EidosConnection", "ZARR_OBJECT_MAX_BYTES"]
