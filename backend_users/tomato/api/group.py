from ..group import Group
from ..user import User
from _shared import _getGroup
from ..lib.error import UserError


def group_exists(name):
	if Group.get(name):
		return True
	return False


def group_list():
	return [g.info() for g in Group.objects.all()]

def group_create(**args):
	UserError.check(not group_exists(args['name']),
	                code=UserError.ALREADY_EXISTS,
	                message="Group with that name already exists",
	                data={"name": args['name']})
	group = Group.create(**args)
	return group.info()


def group_info(name):
	group = _getGroup(name)
	return group.info()


def group_modify(name, **args):
	group = _getGroup(name)
	group.modify(**args)
	return group.info()


def group_remove(name):
	group = _getGroup(name)
	group.remove()
	return True

def group_has_owner(name):
	if len(User.list_by_group(name, "owner")) != 0:
		return True
