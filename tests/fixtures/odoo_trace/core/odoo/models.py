# Minimal stand-in for odoo/models.py: only the lines odoo_trace.py cites and parses.


class MetaModel(type):
    def __init__(self, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if not self._abstract and self._name not in self._inherit:
            add('id', fields.Id(automatic=True))
            add_default('display_name', fields.Char(string='Display Name', automatic=True))
            if attrs.get('_log_access', self._auto):
                add_default('create_uid', fields.Many2one('res.users', automatic=True))
                add_default('create_date', fields.Datetime(automatic=True))
                add_default('write_uid', fields.Many2one('res.users', automatic=True))
                add_default('write_date', fields.Datetime(automatic=True))


class BaseModel(metaclass=MetaModel):
    _auto = False
    _register = False
    _abstract = True

    def write(self, vals):
        self._validate_fields(vals)
        return True

    def _valid_field_parameter(self, field, name):
        return name == 'related_sudo'


AbstractModel = BaseModel


class Model(AbstractModel):
    _auto = True
    _register = False
    _abstract = False


class TransientModel(Model):
    _transient = True
