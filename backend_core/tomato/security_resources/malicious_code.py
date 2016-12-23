# by Chang Rui

from ..db import *
from ..generic import *
from . import system_options
from ..lib.error import UserError, InternalError #@UnresolvedImport



class MaliciousCode(BaseDocument, Entity):

    name = StringField(required=True, unique=True)
    type = StringField(required=True)
    system = StringField(required=True)
    url = URLField(required=False)
    description = StringField(required=False, null=True)
    creation_date = FloatField(required=False)

    malicious_code_type_options = {
        "virus": "Virus",
        "trojan": "Trojan",
        "worm": "Worm",
    }

    REQUIRED_ATTRS = ("name", "type", "system")     # url?

    ATTRIBUTES = {
        'id': IdAttribute(),
        'name': Attribute(field=name, schema=schema.String()),
        'type': Attribute(field=type, schema=schema.String(options=malicious_code_type_options.keys())),
        'system': Attribute(field=system, schema=schema.String(options=system_options.keys())),
        'url': Attribute(field=url, schema=schema.URL(null=True)),
        'description': Attribute(field=description, schema=schema.String()),
        'creation_date': Attribute(field=creation_date, schema=schema.Number(null=True)),
    }

    @classmethod
    def create(cls, **attrs):
        existing_malicious_code = cls.objects.filter(name=attrs["name"], type=attrs["type"], system=attrs["system"])
        UserError.check(not existing_malicious_code,
                        code=UserError.ALREADY_EXISTS,
						message="There exists already a malicious code in same name, type and system.",
						data={"name": attrs["name"], "type": attrs["type"], "system": attrs["system"]})
        obj = cls()
        try:
            obj.init(**attrs)
            obj.save()
            return obj
        except:
            obj.remove()
            raise

    def init(self, **attrs):
        for attr in self.__class__.REQUIRED_ATTRS:
            UserError.check(attr in attrs,
                            code=UserError.INVALID_CONFIGURATION,
                            message="Lack of necessary attribute.",
                            data={"attribute": attr})
        Entity.init(self, **attrs)

    def info(self):
        info = Entity.info(self)
        return info

    def remove(self, **kwargs):
        self.delete()

