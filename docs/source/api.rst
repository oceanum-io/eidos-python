=================
API documentation
=================
Version |version|

Convenience classes
-------------------
.. autoclass:: eidos.EidosDatasource
        :members:
        :exclude-members: BaseModel, ConfigDict, RootModel, Field, constr, model_computed_fields, EidosError, model_post_init, model_config, model_fields

.. autoclass:: eidos.EidosChart
        :members:
        :exclude-members: BaseModel, ConfigDict, RootModel, Field, constr, model_computed_fields, EidosError, model_post_init, model_config, model_fields


Specification components
-----------------------
.. automodule:: eidos
    :members:
    :imported-members:
    :exclude-members: BaseModel, ConfigDict, RootModel, Field, constr, model_computed_fields, EidosError, model_post_init, Eidos

    .. autopydantic_model:: Eidos
        :members:
        :inherited-members:
        :exclude-members: BaseModel, ConfigDict, RootModel, Field, constr, model_computed_fields, EidosError, model_post_init

    


