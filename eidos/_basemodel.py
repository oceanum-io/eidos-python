import copy
from pydantic import BaseModel, ConfigDict


class EidosModel(BaseModel):
    model_config: ConfigDict = ConfigDict(use_enum_values=True)
    _parent = None

    def __init__(self, **data):
        self.__pydantic_validator__.validate_python(data, self_instance=self)
        for name, value in data.items():
            if hasattr(value, "_parent"):
                value._parent = self
        self._change((self, data))

    def __setattr__(self, name, value):
        if name != "_parent" and hasattr(value, "_parent"):
            value._parent = self
        if name[0] != "_":
            self._change((self, {name: value}))
        super().__setattr__(name, value)

    def __delattr__(self, name):
        self._change((self, {name: None}))
        super().__delattr__(name)

    def _change(self, update):
        if self._parent:
            self._parent._change(update)
