from .db import *
from .lib import logging
from .lib.error import UserError
from .generic import *
from .lib.service import get_backend_core_proxy


class Group(Entity, BaseDocument):
	"""
	The group is a smaller management unit, compare to organization.
	An organization can have multiple groups.
	The group will provides filter for topology list, so that a topology could be only visible for the specified group.
	"""

	from .organization import Organization

	name = StringField(unique=True, required=True)
	description = StringField()
	organization = ReferenceField(Organization, reverse_delete_rule=DENY)

	meta = {
		'ordering': 'name',
		'indexes': ['name']
	}

	@classmethod
	def get(cls, name, **kwargs):
		try:
			return cls.objects.get(name=name, **kwargs)
		except cls.DoesNotExist:
			return None

	@property
	def users(self):
		from .user import User
		return User.objects(group=self)

	def _checkRemove(self):
		if self.id:
			UserError.check(not self.users, code=UserError.NOT_EMPTY, message="Group still has users")

	def _remove(self):
		logging.logMessage("remove", category="group", name=self.name)
		if self.id:
			self.delete()

	def modify_organization(self, orga_name):
		from .organization import Organization
		orga = Organization.get(orga_name)
		UserError.check(orga,
						code=UserError.ENTITY_DOES_NOT_EXIST,
						message="Organization with that name does not exist",
						data={"name": orga_name})
		self.organization = orga

	def __str__(self):
		return self.name

	def __repr__(self):
		return "Group(%s)" % self.name

	ACTIONS = {
		Entity.REMOVE_ACTION: Action(fn=_remove, check=_checkRemove)
	}

	ATTRIBUTES = {
		"name": Attribute(field=name, schema=schema.Identifier(minLength=3)),
		"description": Attribute(field=description, schema=schema.String(null=True)),
		"organization": Attribute(get=lambda self: self.organization.name, set=modify_organization)
	}
