import pytest
from eidoslib import Eidos, Node, DocumentView, Particles, StyleAccessorConstant


def test_basic_patch():
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
    patch = eidos.json_diff()
    assert patch is not None
