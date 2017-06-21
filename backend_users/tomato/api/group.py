from ..group import Group
from ..user import User
from _shared import _getGroup, _getUser
from ..lib.error import UserError
from ..lib.group_role import GroupRole

def group_exists(name):
	if Group.get(name):
		return True
	return False


def group_list(user=None, role=None):
	"""
	Get group list. If user is None, the role will be omitted
	"""
	if user is None:
		return [g.info() for g in Group.objects.all()]
	else:
		user = _getUser(user)
		return [g.info() for g in user.get_account_group(role)]


def group_create(**attrs):
	UserError.check(not group_exists(attrs['name']),
	                code=UserError.ALREADY_EXISTS,
	                message="Group with that name already exists",
	                data={"name": attrs['name']})
	group = Group.create(**attrs)
	return group.info()


def group_info(name):
	group = _getGroup(name)
	return group.info()


def group_modify(name, **attrs):
	group = _getGroup(name)
	group.modify(**attrs)
	return group.info()


def group_remove(name):
	group = _getGroup(name)
	group.remove()
	return True

def group_has_owner(name):
	if len(User.list_by_group(name, GroupRole.owner)) != 0:
		return True
	else:
		return False

