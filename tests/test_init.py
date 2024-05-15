import pytest
from eidoslib import Eidos, Node, DocumentView, Particles, StyleAccessorConstant


def test_basic_init():
    doc = DocumentView(content="test")
    node = Node(
        id="test",
        nodeType="document",
        nodeSpec=doc,
    )
    eidos = Eidos(id="test", name="test", data=[], rootNode=node)
    assert eidos is not None
    print("Initialized")


def test_basic_change():
    doc = DocumentView(content="test")
    node = Node(
        id="test",
        nodeType="document",
        nodeSpec=doc,
    )
    eidos = Eidos(
        id="test", name="test", description="I am an EIDOS spec", data=[], rootNode=node
    )
    doc.style = "test"
    eidos.rootNode.id = "new_name"
    del eidos.description
    assert not hasattr(eidos, "description")
    assert eidos.dict()["rootNode"]["id"] == "new_name"


def test_json():
    json = {
        "id": "test",
        "name": "test",
        "data": [],
        "rootNode": {
            "id": "test",
            "nodeType": "document",
            "nodeSpec": {"content": "test"},
        },
    }
    eidos = Eidos.from_dict(json)
    assert eidos.rootNode.id == "test"


def test_root_prop():
    test = StyleAccessorConstant("a")
    test2 = StyleAccessorConstant(root="b")
    assert test.dict() == "a"
    assert test2.dict() == "b"
