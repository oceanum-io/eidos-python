# import altair with an abbreviated alias
import pytest
import altair as alt
import pandas as pd

from eidos import Eidos, Node, PlotView


@pytest.fixture
def data():
    return pd.read_json("https://vega.github.io/vega-datasets/data/cars.json")


@pytest.fixture
def basic_spec():
    cars = pd.read_json("https://vega.github.io/vega-datasets/data/cars.json")
    chart = (
        alt.Chart(cars)
        .mark_point()
        .encode(
            x="Horsepower",
            y="Miles_per_Gallon",
            color="Origin",
        )
    )
    plot = PlotView(plotSpec=chart)
    node = Node(
        id="test",
        nodeType="plot",
        nodeSpec=plot,
    )
    eidos = Eidos(
        id="test", name="test", description="I am an EIDOS spec", data=[], rootNode=node
    )
    return eidos


def test_basic_init(basic_spec):
    eidos = basic_spec
    assert eidos is not None
    print("Initialized")


def test_basic_change(basic_spec):
    eidos = basic_spec
    eidos.rootNode.nodeSpec.width = 800
    eidos.rootNode.id = "new_name"
    del eidos.description
    assert not hasattr(eidos, "description")
    assert eidos.dict()["rootNode"]["id"] == "new_name"


def test_html(basic_spec):
    eidos = basic_spec
    html = eidos.html()
    assert html is not None
    print(html)


def test_show(basic_spec):
    eidos = basic_spec
    assert eidos.show()
