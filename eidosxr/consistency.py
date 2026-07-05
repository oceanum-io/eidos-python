"""Zarr consistency checks for dataset-cache writes.

The EIDOS dataset cache stores zarr **v2** archives with ``compressor: null``
(uncompressed) and a consolidated ``.zmetadata`` manifest. These helpers let a
client verify, before writing, that:

- a store it is about to upload is internally consistent
  (:func:`check_store_consistency`);
- a store is *coordinate-consistent* with an existing dataset for the intended
  write verb (:meth:`eidosxr.EidosConnection.check_put_consistency`):

  * ``replace`` (PUT) — identical coordinate structure; every coordinate must match.
  * ``append`` (PATCH) — the append-axis coordinates extend the existing ones,
    monotonic and non-overlapping; other coordinates must match.
  * ``clobber`` (POST) — no check (complete replacement).

A "store" is any mapping of zarr key -> object bytes (e.g. what the client PUTs).
"""

from __future__ import annotations

import json
import math
from typing import Callable, Dict, List, Mapping, Optional

import numpy as np

from .exceptions import EidosError

ZMETADATA_KEY = ".zmetadata"

Getter = Callable[[str], Optional[bytes]]


class ConsistencyError(EidosError):
    """A zarr store is internally inconsistent, or incompatible with an existing
    dataset for the requested write verb."""


# -- consolidated metadata ------------------------------------------------
def load_consolidated_metadata(getter: Getter) -> Dict[str, dict]:
    """Load and parse the consolidated ``.zmetadata`` manifest.

    ``getter(path)`` returns the object bytes (or ``None`` if absent). Returns
    the flat ``metadata`` mapping (``"<array>/.zarray"`` -> zarray dict, etc.).
    """
    raw = getter(ZMETADATA_KEY)
    if raw is None:
        raise ConsistencyError(
            f"{ZMETADATA_KEY} not found — not a consolidated zarr store"
        )
    try:
        doc = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise ConsistencyError(f"{ZMETADATA_KEY} is not valid JSON") from exc
    meta = doc.get("metadata", doc) if isinstance(doc, dict) else None
    if not isinstance(meta, dict):
        raise ConsistencyError(f"{ZMETADATA_KEY} has no metadata object")
    return meta


def array_names(meta: Mapping[str, dict]) -> List[str]:
    """Names of the arrays declared in a consolidated metadata mapping."""
    return sorted(k[: -len("/.zarray")] for k in meta if k.endswith("/.zarray"))


def _zarray(meta: Mapping[str, dict], name: str) -> dict:
    return meta[f"{name}/.zarray"]


def _dims(meta: Mapping[str, dict], name: str) -> Optional[List[str]]:
    attrs = meta.get(f"{name}/.zattrs")
    if isinstance(attrs, dict) and "_ARRAY_DIMENSIONS" in attrs:
        return list(attrs["_ARRAY_DIMENSIONS"])
    return None


def _grid(zarray: dict) -> List[int]:
    return [
        max(1, math.ceil(s / c)) if c else 1
        for s, c in zip(zarray["shape"], zarray["chunks"])
    ]


def _full_chunk_bytes(zarray: dict) -> int:
    n = np.dtype(zarray["dtype"]).itemsize
    for c in zarray["chunks"]:
        n *= c
    return n


# -- integrity ------------------------------------------------------------
def check_store_consistency(store: Mapping[str, bytes]) -> None:
    """Validate that a local zarr store (``path -> bytes``) is internally
    consistent: metadata parses, every declared array has a ``.zarray``, every
    chunk object maps to a declared array and lies within its grid, and (for the
    uncompressed EIDOS stores) each chunk is the full expected byte size.

    Raises :class:`ConsistencyError` on the first violation.
    """
    meta = load_consolidated_metadata(store.get)
    names = array_names(meta)
    if not names:
        raise ConsistencyError(f"{ZMETADATA_KEY} declares no arrays")

    # longest-prefix match so nested names and both "." / "/" separators work.
    names_by_len = sorted(names, key=len, reverse=True)
    for name in names:
        if f"{name}/.zarray" not in meta:
            raise ConsistencyError(f"array '{name}' has no .zarray in {ZMETADATA_KEY}")

    for key, value in store.items():
        base = key.rsplit("/", 1)[-1]
        if base.startswith("."):  # metadata object (.zarray/.zattrs/.zgroup/.zmetadata)
            continue
        owner = next(
            (n for n in names_by_len if key == n or key.startswith(n + "/")), None
        )
        if owner is None:
            raise ConsistencyError(
                f"orphan object '{key}' belongs to no array declared in {ZMETADATA_KEY}"
            )
        za = _zarray(meta, owner)
        grid = _grid(za)
        sep = za.get("dimension_separator", ".")
        index_str = key[len(owner) + 1 :]
        try:
            index = [int(p) for p in index_str.split(sep)]
        except ValueError as exc:
            raise ConsistencyError(f"malformed chunk key '{key}'") from exc
        if len(index) != len(grid):
            raise ConsistencyError(
                f"chunk '{key}' has {len(index)} dims, array '{owner}' has {len(grid)}"
            )
        for dim, (i, g) in enumerate(zip(index, grid)):
            if not 0 <= i < g:
                raise ConsistencyError(
                    f"chunk '{key}' index {i} out of range for dim {dim} (0..{g - 1})"
                )
        if za.get("compressor") is None and value is not None:
            expected = _full_chunk_bytes(za)
            if len(value) != expected:
                raise ConsistencyError(
                    f"chunk '{key}' is {len(value)} bytes, expected {expected} "
                    f"(uncompressed {za['dtype']} chunks {za['chunks']})"
                )


# -- coordinate decoding --------------------------------------------------
def decode_coordinate(getter: Getter, name: str, zarray: dict) -> np.ndarray:
    """Decode a 1-D uncompressed coordinate array to a numpy array.

    Concatenates the array's chunks in order and trims to its declared length.
    Only supports 1-D, uncompressed (``compressor: null``) arrays — the EIDOS
    dataset-cache format.
    """
    if len(zarray["shape"]) != 1:
        raise ConsistencyError(
            f"coordinate '{name}' is not 1-D (shape {zarray['shape']})"
        )
    if zarray.get("compressor") is not None or zarray.get("filters"):
        raise ConsistencyError(
            f"coordinate '{name}' is compressed/filtered — unsupported for the "
            "coordinate check (EIDOS stores are uncompressed)"
        )
    dtype = np.dtype(zarray["dtype"])
    sep = zarray.get("dimension_separator", ".")
    n_chunks = _grid(zarray)[0]
    buf = bytearray()
    for i in range(n_chunks):
        chunk = getter(f"{name}/{i}" if sep != "/" else f"{name}/{i}")
        if chunk is None:
            raise ConsistencyError(f"coordinate '{name}' chunk {i} missing")
        buf.extend(chunk)
    values = np.frombuffer(bytes(buf), dtype=dtype)
    return np.asarray(values[: zarray["shape"][0]])


# -- structural + coordinate compatibility --------------------------------
_STRUCT_FIELDS = (
    "dtype",
    "chunks",
    "order",
    "fill_value",
    "compressor",
    "filters",
    "dimension_separator",
    "zarr_format",
)


def _compare_structure(
    name: str, old: dict, new: dict, append_dim_axis: Optional[int]
) -> None:
    for field in _STRUCT_FIELDS:
        if old.get(field) != new.get(field):
            raise ConsistencyError(
                f"array '{name}': {field} differs "
                f"(existing {old.get(field)!r} vs new {new.get(field)!r})"
            )
    old_shape, new_shape = list(old["shape"]), list(new["shape"])
    if len(old_shape) != len(new_shape):
        raise ConsistencyError(
            f"array '{name}': rank differs ({len(old_shape)} vs {len(new_shape)})"
        )
    for axis, (o, n) in enumerate(zip(old_shape, new_shape)):
        if axis == append_dim_axis:
            continue
        if o != n:
            raise ConsistencyError(
                f"array '{name}': non-append dim {axis} differs ({o} vs {n})"
            )


def compare_stores(
    existing_meta: Mapping[str, dict],
    new_meta: Mapping[str, dict],
    existing_get: Getter,
    new_get: Getter,
    *,
    mode: str,
    append_dim: Optional[str] = None,
) -> None:
    """Check a new store is consistent with an existing archive for ``mode``.

    ``mode`` is ``"replace"`` (coords must match exactly) or ``"append"`` (the
    ``append_dim`` coordinate extends monotonically without overlap; other
    coordinates match).
    """
    if mode not in ("replace", "append"):
        raise ValueError("mode must be 'replace' or 'append'")
    if mode == "append" and not append_dim:
        raise ValueError("append_dim is required for mode='append'")

    existing_arrays = set(array_names(existing_meta))
    new_arrays = set(array_names(new_meta))
    shared = existing_arrays & new_arrays
    if not shared:
        raise ConsistencyError("new store shares no arrays with the existing dataset")
    if mode == "replace" and existing_arrays != new_arrays:
        raise ConsistencyError(
            "replace requires the same arrays; differs by "
            f"{sorted(existing_arrays ^ new_arrays)}"
        )

    for name in sorted(shared):
        old_za, new_za = _zarray(existing_meta, name), _zarray(new_meta, name)
        dims = _dims(existing_meta, name)
        axis = dims.index(append_dim) if (dims and append_dim in dims) else None
        _compare_structure(name, old_za, new_za, axis if mode == "append" else None)

    # coordinate arrays: 1-D arrays whose single dimension is their own name.
    coord_names = [
        n
        for n in sorted(shared)
        if len(_zarray(existing_meta, n)["shape"]) == 1
        and (_dims(existing_meta, n) in (None, [n]))
    ]
    for name in coord_names:
        old = decode_coordinate(existing_get, name, _zarray(existing_meta, name))
        new = decode_coordinate(new_get, name, _zarray(new_meta, name))
        if mode == "replace" or name != append_dim:
            if old.shape != new.shape or not np.array_equal(old, new):
                raise ConsistencyError(
                    f"coordinate '{name}' differs — a {mode} must preserve it"
                )
        else:  # append along this coordinate
            _check_append_axis(name, old, new)


def _check_append_axis(name: str, old: np.ndarray, new: np.ndarray) -> None:
    if old.size == 0 or new.size == 0:
        raise ConsistencyError(f"coordinate '{name}': empty append axis")
    old_inc = bool(old[-1] >= old[0])
    new_inc = bool(new[-1] >= new[0])
    old_mono = np.all(np.diff(old) > 0) if old_inc else np.all(np.diff(old) < 0)
    new_mono = np.all(np.diff(new) > 0) if new_inc else np.all(np.diff(new) < 0)
    if not old_mono:
        raise ConsistencyError(f"coordinate '{name}': existing axis is not monotonic")
    if not new_mono:
        raise ConsistencyError(f"coordinate '{name}': appended axis is not monotonic")
    if old_inc != new_inc:
        raise ConsistencyError(
            f"coordinate '{name}': append direction differs from existing"
        )
    if old_inc and not (new[0] > old[-1]):
        raise ConsistencyError(
            f"coordinate '{name}': appended values overlap existing "
            f"(new starts {new[0]}, existing ends {old[-1]})"
        )
    if not old_inc and not (new[0] < old[-1]):
        raise ConsistencyError(
            f"coordinate '{name}': appended values overlap existing "
            f"(new starts {new[0]}, existing ends {old[-1]})"
        )


__all__ = [
    "ConsistencyError",
    "check_store_consistency",
    "compare_stores",
    "load_consolidated_metadata",
    "array_names",
    "decode_coordinate",
]
