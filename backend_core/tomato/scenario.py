import datetime

from .db import *
# from generic import *


# By Chang Rui
class Scenario(BaseDocument):

    name = StringField(required=True, unique=True)
    description = StringField()
    accessibility = StringField()   # 'private' or 'public', in lower case.
    author = StringField()
    create_time = DateTimeField()
    topology_info_json = StringField()

    @classmethod
    def create(cls, **attrs):
        scenario = Scenario()
        scenario.create_time = datetime.datetime.now()
        scenario.mod(**attrs)
        scenario.save()
        return scenario.info

    def mod(self, **attrs):
        for key in attrs:
            if key in ['name', 'description', 'accessibility', 'author', 'topology_info_json']:
                setattr(self, key, attrs[key])
            else:
                print '[Scenario Modify] Unknown attribute "%s", ignore this attribute.' % key
        self.save()
        return self.info()

    @classmethod
    def modify_by_id(cls, id_, **attrs):
        scenario = Scenario.get(id_)
        return scenario.mod(**attrs)

    def remove(self):
        self.delete()

    @classmethod
    def remove_by_id(cls, id_):
        scenario = cls.get(id_)
        scenario.remove()

    def info(self):
        sc_info = {
            'id': self.id.__str__(),
            'name': self.name,
            'description': self.description,
            'accessibility': self.accessibility,
            'author': self.author,
            'create_time': self.create_time.__str__(),
            'topology_info_json': self.topology_info_json,
        }
        return sc_info

    @classmethod
    def info_by_id(cls, id_):
        scenario = cls.get(id_)
        return scenario.info()

    @classmethod
    def get_count(cls):
        return len(cls.objects.filter())

    @classmethod
    def get_all(cls, **kwargs):
        return list(Scenario.objects.filter(**kwargs))

    @classmethod
    def get_list(cls, user, show):
        if show == 'all':
            print "Show all."
            return list(cls.objects.filter(Q(accessibility='public') | Q(author=user)))
        elif show == 'my':
            print "Show mine."
            return list(cls.objects.filter(author=user))
        elif show == 'public':
            print "Show public."
            return list(cls.objects.filter(accessibility='public'))
        else:
            print "Invalid Parameter."
            print "user: %s, show: %s" % (user, show)
            return []

    @classmethod
    def get(cls, id_, **kwargs):
        return Scenario.objects.get(id=id_, **kwargs)

    @classmethod
    def get_topology_info_json(cls, id_):
        scenario = cls.get(id_)
        return scenario.topology_info_json
