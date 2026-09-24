# Minimal stand-in for odoo/fields.py: only the lines odoo_trace.py cites.


class Field:
    def _get_attrs(self, model_class, name):
        attrs = {}
        for field in self._args__.get('_base_fields', ()):
            if not isinstance(self, type(field)):
                attrs.clear()
                continue
            attrs.update(field._args__)
        return attrs
