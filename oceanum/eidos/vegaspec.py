import altair
from pydantic import RootModel, model_validator


# This top level model for the vega spec is used in the PlotView model
# Validation is not needed here as the spec is already validated by Altair
class TopLevelSpec(RootModel[dict]):
    """
    Top-level specification of a Vega or Vega-Lite visualization.
    You can instantiate this class with a valid vega-lite dictionary or with an Altair Chart
    """

    root: dict

    @model_validator(mode="before")
    @classmethod
    def validate(cls, spec: dict | str | altair.Chart):
        if isinstance(spec, dict):
            spec = altair.Chart.from_dict(spec)
        elif isinstance(spec, str):
            spec = altair.Chart.from_json(spec)
        return spec.to_dict()
