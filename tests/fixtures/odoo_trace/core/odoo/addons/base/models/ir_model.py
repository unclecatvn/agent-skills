from odoo import models


class Base(models.AbstractModel):
    _name = 'base'
    _description = 'Base'


def _reflect_models(model, module):
    if model._module == module:
        return 'model_xmlid'


def _reflect_fields(model, field, module):
    if module == model._original_module or module in field._modules:
        return 'field_xmlid'


def _reflect_selections(field, m):
    xml_id = selection_xmlid(m, field.model_name, field.name, 'value')
    return xml_id
