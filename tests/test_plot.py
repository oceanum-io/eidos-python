# import altair with an abbreviated alias
import pytest
import altair as alt
import pandas as pd
import numpy as np

from eidos import (
    Eidos,
    Node,
    PlotView,
    TopLevelSpec,
    EidosSpecError,
    EidosChart,
    EidosDatasource,
)


@pytest.fixture
def data():
    time = pd.date_range("2021-01-01", periods=100)
    data = pd.DataFrame(
        {"time": time, "value1": np.random.randn(100), "value2": np.random.randn(100)}
    ).set_index("time")
    return EidosDatasource("data", data)


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
    plot = PlotView(plotSpec=EidosChart(chart))
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


def test_change_fail(basic_spec):
    eidos = basic_spec
    with pytest.raises(EidosSpecError):
        eidos.rootNode.nodeSpec.plotSpec = {"data": "not a valid vega spec"}


def test_named_data(basic_spec, data):
    basic_spec.data = [data]
    chart = (
        alt.Chart(alt.NamedData("data"))
        .mark_point()
        .encode(
            x=alt.X(field="time", type="temporal"),
            y=alt.Y(field="value1", type="quantitative"),
            color=alt.Color(field="value2", type="quantitative"),
        )
    )
    basic_spec.rootNode.nodeSpec.plotSpec = chart
    assert basic_spec.show()


def test_html(basic_spec):
    eidos = basic_spec
    html = eidos.html()
    assert html is not None
    print(html)


def test_show(basic_spec):
    eidos = basic_spec
    assert eidos.show()
