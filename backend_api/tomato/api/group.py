from ..lib.error import InternalError, UserError
from ..lib.service import get_backend_users_proxy, get_backend_core_proxy, get_backend_accounting_proxy
from api_helpers import getCurrentUserInfo

def group_list(user=None, role=None):
	"""
	Return a list of groups
	:param user: if not None, only groups that user has a role will be list.
	:param role: role filter. If user is not None, this will be omitted
	:return: list of group info
	"""
	if user is not None:
		getCurrentUserInfo().check_may_list_group(user=user, role=role)
	return get_backend_users_proxy().group_list(user=user, role=role)


def group_create(attrs=None):
	"""
	Create a group with provided info (name, label, description)
	:return: Info of the group
	"""
	getCurrentUserInfo().check_may_create_group()
	return get_backend_users_proxy().group_create(**attrs)

def group_info(name):
	"""
	Return the info of the group with the provided name
	:param name: Name of the group
	:return: Info of the group
	"""
	return get_backend_users_proxy().group_info(name)


def group_modify(name, attrs):
	"""
	Modify the attributes of an existing group
	:param name: Name of the group
	:param attrs: Info of the group
	:return: Info of the group
	"""
	getCurrentUserInfo().check_may_modify_group(name)
	return get_backend_users_proxy().group_modify(name, **attrs)


def group_remove(name):
	"""
	Removes the group with provided name
	All the users will also lost their role on this group.
	:param name: Name of the group
	:return: True if remove successful
	"""
	getCurrentUserInfo().check_may_remove_group(name)
	return get_backend_users_proxy().group_remove(name)

