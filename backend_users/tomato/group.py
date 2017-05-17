from .db import *
from .lib import logging
from .lib.error import UserError
from .generic import *
from .lib.service import get_backend_core_proxy


class Group(Entity, BaseDocument):

	name = StringField(unique=True, required=True)
	label = StringField(required=True)
	description = StringField()

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
		return User.objects(groups__group__exact=self.name)

	@property
	def owner(self):
		from.user import User
		owner = User.objects.get(Q(groups__group__exact=self.name) & Q(groups__role__exact='owner'))
		return owner.name

	@owner.setter
	def owner(self, new=None):
		from .user import User
		old = self.owner
		if new == old:
			return
		if new is None:
			_old = User.objects.get(name=old) if old is not None else None
			if _old:
				_old.quit_group(self.name)
		else:
			_new = User.objects.get(name=new)
			UserError.check(_new, code=UserError.ENTITY_DOES_NOT_EXIST,
			                message="User with that name does not exist", data={"name": new})
			_old = User.objects.get(name=old) if old is not None else None
			if _old:
				_old.quit_group(self.name)
			_new.set_group_role(self.name, 'owner')

	def _remove(self):
		# logging.logMessage("remove", category="group", name=self.name)
		group_users = self.users
		for user in group_users:
			user.quit_group(self)
		if self.id:
			self.delete()

	def __str__(self):
		return self.name

	def __repr__(self):
		return "Group(%s)" % self.name

	ACTIONS = {
		# Entity.REMOVE_ACTION: Action(fn=_remove, check=_checkRemove)
	}

	ATTRIBUTES = {
		"name": Attribute(field=name, schema=schema.Identifier(minLength=3)),
		"label": Attribute(field=label, schema=schema.String(minLength=3)),
		"description": Attribute(field=description, schema=schema.String(null=True)),
		"owner": Attribute(field=owner, schema=schema.String())
	}
