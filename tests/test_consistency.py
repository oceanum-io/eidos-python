"""Tests for the zarr dataset-cache consistency checks."""

import json

import numpy as np
import pytest

from eidosxr import ConsistencyError, check_store_consistency
from eidosxr.consistency import compare_stores, load_consolidated_metadata


def _zarray(shape, chunks, dtype, dims):
    return {
        "shape": list(shape),
        "chunks": list(chunks),
        "dtype": dtype,
        "compressor": None,
        "fill_value": None,
        "filters": None,
        "order": "C",
        "zarr_format": 2,
        "dimension_separator": ".",
    }


def make_store(time_vals, x_vals=(10, 20)):
    """A tiny valid zarr v2 store: data 'hs'(time,x) + coords 'time','x'."""
    time = np.asarray(time_vals, dtype="<i8")
    x = np.asarray(x_vals, dtype="<i8")
    nt, nx = time.size, x.size
    meta = {
        ".zgroup": {"zarr_format": 2},
        "time/.zarray": _zarray([nt], [nt], "<i8", ["time"]),
        "time/.zattrs": {"_ARRAY_DIMENSIONS": ["time"]},
        "x/.zarray": _zarray([nx], [nx], "<i8", ["x"]),
        "x/.zattrs": {"_ARRAY_DIMENSIONS": ["x"]},
        "hs/.zarray": _zarray([nt, nx], [nt, nx], "<f4", ["time", "x"]),
        "hs/.zattrs": {"_ARRAY_DIMENSIONS": ["time", "x"]},
    }
    store = {
        ".zmetadata": json.dumps(
            {"zarr_consolidated_format": 1, "metadata": meta}
        ).encode(),
        "time/0": time.tobytes(),
        "x/0": x.tobytes(),
        "hs/0.0": np.zeros((nt, nx), dtype="<f4").tobytes(),
    }
    return store


# -- integrity -------------------------------------------------------------
def test_valid_store_passes():
    check_store_consistency(make_store([0, 1, 2]))


def test_bad_chunk_byte_size():
    store = make_store([0, 1, 2])
    store["hs/0.0"] = store["hs/0.0"][:-4]  # one float short
    with pytest.raises(ConsistencyError, match="bytes"):
        check_store_consistency(store)


def test_chunk_out_of_grid():
    store = make_store([0, 1, 2])
    store["hs/1.0"] = store["hs/0.0"]  # grid is 1x1, index 1 is out of range
    with pytest.raises(ConsistencyError, match="out of range"):
        check_store_consistency(store)


def test_orphan_object():
    store = make_store([0, 1, 2])
    store["ghost/0"] = b"\x00" * 8
    with pytest.raises(ConsistencyError, match="orphan"):
        check_store_consistency(store)


def test_missing_zmetadata():
    store = make_store([0, 1, 2])
    del store[".zmetadata"]
    with pytest.raises(ConsistencyError, match="zmetadata"):
        check_store_consistency(store)


# -- replace (PUT) ---------------------------------------------------------
def _compare(existing, new, **kw):
    compare_stores(
        load_consolidated_metadata(existing.get),
        load_consolidated_metadata(new.get),
        existing.get,
        new.get,
        **kw,
    )


def test_replace_matching_coords_ok():
    _compare(make_store([0, 1, 2]), make_store([0, 1, 2]), mode="replace")


def test_replace_changed_coord_fails():
    with pytest.raises(ConsistencyError, match="coordinate 'time'"):
        _compare(make_store([0, 1, 2]), make_store([0, 1, 9]), mode="replace")


def test_replace_changed_x_coord_fails():
    with pytest.raises(ConsistencyError, match="coordinate 'x'"):
        _compare(
            make_store([0, 1, 2], x_vals=(10, 20)),
            make_store([0, 1, 2], x_vals=(10, 99)),
            mode="replace",
        )


# -- append (PATCH) --------------------------------------------------------
def test_append_non_overlapping_ok():
    _compare(
        make_store([0, 1, 2]), make_store([3, 4, 5]), mode="append", append_dim="time"
    )


def test_append_overlapping_fails():
    with pytest.raises(ConsistencyError, match="overlap"):
        _compare(
            make_store([0, 1, 2]),
            make_store([2, 3, 4]),
            mode="append",
            append_dim="time",
        )


def test_append_wrong_direction_fails():
    with pytest.raises(ConsistencyError, match="direction"):
        _compare(
            make_store([0, 1, 2]),
            make_store([5, 4, 3]),
            mode="append",
            append_dim="time",
        )


def test_append_non_append_coord_must_match():
    with pytest.raises(ConsistencyError, match="coordinate 'x'"):
        _compare(
            make_store([0, 1, 2], x_vals=(10, 20)),
            make_store([3, 4, 5], x_vals=(10, 99)),
            mode="append",
            append_dim="time",
        )


def test_append_dtype_mismatch_fails():
    existing = make_store([0, 1, 2])
    new = make_store([3, 4, 5])
    meta = json.loads(new[".zmetadata"])
    meta["metadata"]["hs/.zarray"]["dtype"] = "<f8"  # was <f4
    new[".zmetadata"] = json.dumps(meta).encode()
    with pytest.raises(ConsistencyError, match="dtype differs"):
        _compare(existing, new, mode="append", append_dim="time")
