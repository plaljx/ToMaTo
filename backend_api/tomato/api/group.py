from ..lib.error import InternalError, UserError
from ..lib.service import get_backend_users_proxy, get_backend_core_proxy, get_backend_accounting_proxy


def group_list():
	"""
	Return a list of groups
	:return: list of group info
	"""
	return get_backend_users_proxy().group_list()


def group_create(attrs=None):
	"""
	Create a group with provided info (name, label, description)
	:return: Info of the group
	"""
	return get_backend_users_proxy().group_create(attrs)

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
	return get_backend_users_proxy().group_modify(name, attrs)


def group_remove(name):
	"""
	Removes the group with provided name
	All the users will also lost their role on this group.
	:param name: Name of the group
	:return: True if remove successful
	"""
	return get_backend_users_proxy().group_remove(name)

