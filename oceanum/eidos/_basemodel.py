import copy
from pydantic import BaseModel, ConfigDict, ValidationError
from typing import TYPE_CHECKING

from .exceptions import EidosSpecError


class ListProxy(list):
    _parent = None

    def _set_as_parent(self, value):
        if value is None:
            return
        elif hasattr(value, "_parent"):
            value._parent = self

    def __init__(self, *args):
        super().__init__(*args)

    def append(self, value):
        self._set_as_parent(value)
        super().append(value)
        self._parent._change()

    def insert(self, index, value):
        self._set_as_parent(value)
        super().insert(index, value)
        self._parent._change()

    def pop(self, index):
        value = super().pop(index)
        self._parent._change()
        return value

    def remove(self, value):
        super().remove(value)
        self._parent._change()

    def __setitem__(self, index, value):
        self._set_as_parent(value)
        super().__setitem__(index, value)
        self._parent._change()

    def __delitem__(self, index):
        super().__delitem__(index)
        self._parent._change()


class EidosModel(BaseModel):
    model_config: ConfigDict = ConfigDict(
        use_enum_values=True, validate_assignment=True
    )
    _parent = None

    def __init__(self, **data):
        self.__pydantic_validator__.validate_python(data, self_instance=self)
        for name, _ in data.items():
            if not name.startswith("_") and name in self.model_fields:
                value = self.__dict__[name]
                if isinstance(value, list):
                    value = ListProxy(value)
                self._set_as_parent(value)
                self.__dict__[name] = value
        self._change()

    def _set_as_parent(self, value):
        if value is None:
            return
        elif hasattr(value, "_parent"):
            value._parent = self

    def __setattr__(self, name, value):
        if isinstance(value, list):
            value = ListProxy(value)
        if not name.startswith("_"):
            self._set_as_parent(value)
        try:
            super().__setattr__(name, value)
        except ValidationError as e:
            raise EidosSpecError(e)
        if name[0] != "_":
            self._change()

    def __delattr__(self, name):
        self._change()
        super().__delattr__(name)

    def _change(self):
        if self._parent:
            self._parent._change()
