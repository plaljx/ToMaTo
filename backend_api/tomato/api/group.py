from ..lib.error import InternalError, UserError
from ..lib.service import get_backend_users_proxy, get_backend_core_proxy, get_backend_accounting_proxy


def group_list():
	return get_backend_users_proxy().group_list()


def group_create(attrs=None):
	return get_backend_users_proxy().group_create(attrs)


def group_info(name):
	return get_backend_users_proxy().group_info(name)


def group_modify(name, attrs):
	return get_backend_users_proxy().group_modify(name, attrs)


def group_remove(name):
	return get_backend_users_proxy().group_remove(name)

