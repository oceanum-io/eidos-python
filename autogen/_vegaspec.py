import altair
from pydantic import RootModel, model_validator
from .exceptions import EidosSpecError


# This top level model for the vega spec is used in the PlotView model
# The spec is validated by Altair


class TopLevelSpec(RootModel[dict]):
    """
    Top-level specification of PlotView plotSpec.
    This model can be initialized as a valid vega-lite dictionary, JSON string or an Altair Chart.
    To use an Altair Chart with one of the defined EIDOS datasources, use an altair.NamedData object with the id of the dataspec Datasource.
    """

    root: dict

    @model_validator(mode="before")
    @classmethod
    def validate(cls, spec: dict | str | altair.Chart):
        if isinstance(spec, dict):
            try:
                spec = altair.Chart.from_dict(spec)
            except Exception as e:
                raise EidosSpecError(e)
        elif isinstance(spec, str):
            try:
                spec = altair.Chart.from_json(spec)
            except Exception as e:
                raise EidosSpecError(e)
        return spec.to_dict()
