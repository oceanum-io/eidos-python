"""Tests for the EIDOS platform API client (mocked HTTP via ``responses``)."""

import pytest
import responses

from eidosxr import (
    Dataset,
    Document,
    Eidos,
    EidosConnection,
    EidosError,
    NotFound,
    PatchConflict,
    PatchResult,
    PreconditionFailed,
    Specification,
    Template,
)

SERVICE = "https://api.eidosxr.com"
INGEST = "https://ingest.example"


@pytest.fixture
def conn():
    return EidosConnection(token="ek_test", service=SERVICE, ingestion_service=INGEST)


@pytest.fixture
def spec_body():
    return {
        "id": "s1",
        "name": "demo",
        "description": None,
        "account_id": None,
        "is_public": False,
        "spec": {
            "id": "s1",
            "name": "demo",
            "data": [],
            "root": {"id": "root", "content": "hello"},
        },
        "created_at": "2026-07-04T00:00:00Z",
        "updated_at": "2026-07-04T00:00:00Z",
        "version": 3,
    }


# --- auth -----------------------------------------------------------------
def test_token_required(monkeypatch):
    monkeypatch.delenv("EIDOS_TOKEN", raising=False)
    with pytest.raises(ValueError):
        EidosConnection()


@responses.activate
def test_bearer_header_sent(conn):
    responses.get(
        f"{SERVICE}/specifications",
        json={"specifications": [], "total": 0, "limit": 50, "offset": 0},
    )
    conn.list_specifications()
    assert responses.calls[0].request.headers["Authorization"] == "Bearer ek_test"


# --- specifications -------------------------------------------------------
@responses.activate
def test_list_specifications(conn):
    responses.get(
        f"{SERVICE}/specifications",
        json={
            "specifications": [
                {
                    "id": "s1",
                    "name": "demo",
                    "description": None,
                    "account_id": None,
                    "is_public": True,
                    "template": False,
                    "created_by_user_id": "u1",
                    "created_at": "2026-07-04T00:00:00Z",
                    "updated_at": "2026-07-04T00:00:00Z",
                }
            ],
            "total": 1,
            "limit": 50,
            "offset": 0,
        },
    )
    result = conn.list_specifications(limit=10, offset=0)
    assert result.total == 1
    assert result.specifications[0].id == "s1"
    assert responses.calls[0].request.params["limit"] == "10"


@responses.activate
def test_get_specification(conn, spec_body):
    responses.get(f"{SERVICE}/specifications/s1", json=spec_body)
    spec = conn.get_specification("s1")
    assert isinstance(spec, Specification)
    assert spec.version == 3
    eidos = spec.to_eidos()
    assert isinstance(eidos, Eidos)
    assert eidos.root.id == "root"


@responses.activate
def test_create_specification_from_eidos(conn, spec_body):
    responses.post(f"{SERVICE}/specifications", json=spec_body, status=201)
    eidos = Eidos(
        id="s1",
        name="demo",
        description="d",
        data=[],
        root=Document(id="root", content="hello"),
    )
    conn.create_specification(eidos)
    sent = responses.calls[0].request.body
    import json as _json

    payload = _json.loads(sent)
    assert payload["name"] == "demo"
    assert payload["spec"]["root"]["id"] == "root"


@responses.activate
def test_update_specification_sends_diff_and_if_match(conn):
    """update() must POST exactly the model's .patch() with an If-Match header."""
    responses.patch(
        f"{SERVICE}/specifications/s1",
        json={
            "id": "s1",
            "spec": {},
            "version": 4,
            "updated_at": "2026-07-04T01:00:00Z",
        },
    )
    eidos = Eidos(
        id="s1",
        name="demo",
        description="d",
        data=[],
        root=Document(id="root", content="hello"),
    )
    eidos.root.content = "changed"  # a single edit since checkpoint
    result = conn.update_specification("s1", eidos, if_match=3)
    assert isinstance(result, PatchResult)
    assert result.version == 4

    import json as _json

    ops = _json.loads(responses.calls[0].request.body)
    assert ops == [{"op": "replace", "path": "/root/content", "value": "changed"}]
    assert responses.calls[0].request.headers["If-Match"] == '"3"'


@responses.activate
def test_update_specification_noop_when_unchanged(conn):
    eidos = Eidos(
        id="s1",
        name="demo",
        data=[],
        root=Document(id="root", content="hello"),
    )
    # no edits -> no patch -> no request
    assert conn.update_specification("s1", eidos) is None
    assert len(responses.calls) == 0


@responses.activate
def test_delete_specification(conn):
    responses.delete(f"{SERVICE}/specifications/s1", status=204)
    assert conn.delete_specification("s1") is None


# --- error mapping --------------------------------------------------------
@responses.activate
def test_precondition_failed_carries_current_version(conn):
    responses.patch(
        f"{SERVICE}/specifications/s1",
        json={"error": "precondition_failed", "current_version": 7},
        status=412,
    )
    with pytest.raises(PreconditionFailed) as exc:
        conn.patch_specification(
            "s1", [{"op": "replace", "path": "/name", "value": "x"}], if_match=3
        )
    assert exc.value.current_version == 7
    assert exc.value.status == 412


@responses.activate
def test_patch_conflict(conn):
    responses.patch(
        f"{SERVICE}/specifications/s1",
        json={"error": "patch_conflict", "message": "path not found"},
        status=409,
    )
    with pytest.raises(PatchConflict):
        conn.patch_specification("s1", [{"op": "remove", "path": "/nope"}])


@responses.activate
def test_not_found(conn):
    responses.get(
        f"{SERVICE}/specifications/missing",
        json={"error": "not_found"},
        status=404,
    )
    with pytest.raises(NotFound):
        conn.get_specification("missing")


# --- templates ------------------------------------------------------------
@responses.activate
def test_list_templates_bare_array(conn):
    responses.get(
        f"{SERVICE}/templates",
        json=[
            {
                "id": "t1",
                "name": "tmpl",
                "description": "",
                "category": "custom",
                "node_type": "world",
                "icon": None,
                "scope": "user",
                "account_id": None,
                "created_by_user_id": "u1",
                "spec_json": {"nodeType": "world"},
                "created_at": "2026-07-04T00:00:00Z",
                "updated_at": "2026-07-04T00:00:00Z",
            }
        ],
    )
    templates = conn.list_templates(node_type="world")
    assert len(templates) == 1
    assert isinstance(templates[0], Template)
    assert templates[0].node_type == "world"


@responses.activate
def test_archive_template(conn):
    responses.post(f"{SERVICE}/templates/t1/archive", status=204)
    assert conn.archive_template("t1") is None


# --- datasets / ingestion -------------------------------------------------
@responses.activate
def test_list_datasets(conn):
    responses.get(
        f"{INGEST}/api/datasets",
        json=[
            {
                "id": "d1",
                "original_filename": "a.nc",
                "name": "A",
                "description": None,
                "coordkeys": None,
                "r2_zarr_uri": None,
                "size_bytes": None,
                "status": "completed",
                "error_message": None,
                "created_at": "2026-07-04T00:00:00Z",
            }
        ],
    )
    datasets = conn.list_datasets(status="completed")
    assert isinstance(datasets[0], Dataset)
    assert datasets[0].status == "completed"


@responses.activate
def test_put_zarr_object_sets_content_length(conn):
    responses.put(f"{INGEST}/api/datasets/d1/zarr/.zmetadata", status=204)
    conn.put_zarr_object("d1", ".zmetadata", b"{}")
    req = responses.calls[0].request
    assert req.headers["Content-Length"] == "2"


def test_put_zarr_object_too_large(conn):
    with pytest.raises(ValueError):
        conn.put_zarr_object("d1", "x", b"0" * (64 * 1024 * 1024 + 1))


def test_ingestion_not_configured():
    c = EidosConnection(token="ek_test")  # no ingestion_service
    with pytest.raises(EidosError):
        c.list_datasets()
