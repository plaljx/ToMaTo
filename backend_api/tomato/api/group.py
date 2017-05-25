from ..lib.error import InternalError, UserError
from ..lib.service import get_backend_users_proxy, get_backend_core_proxy, get_backend_accounting_proxy
from api_helpers import getCurrentUserInfo
from ..lib.remote_info import get_user_info, get_user_list_by_group

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

def account_list_by_group(group=None, role=None):
	if group is None and role is None:
		getCurrentUserInfo().check_may_list_all_users()
	else:
		# TODO: may need permission to check group users
		pass
	return get_user_list_by_group(group=group, role=role)

def account_set_group_role(user, group, role=None):
	"""
	Direct set a group role of a user.
	Only global admin should use this
	"""
	getCurrentUserInfo().check_may_set_group_role(user, group, role)
	target_account = get_user_info(user)
	UserError.check(target_account.exists(),
	                code=UserError.ENTITY_DOES_NOT_EXIST, message="Account with that name does not exist")
	UserError.check(get_backend_users_proxy().group_exists(group),
	                code=UserError.ENTITY_DOES_NOT_EXIST, message="Group with that name does not exist")
	if role == "owner":
		UserError.check(not (get_backend_users_proxy().group_has_owner(group)),
		                code=UserError.INVALID_CONFIGURATION, message="The group already has a owner")
	return target_account.set_group_role(group, role)

def group_invite(user, group):
	"""
	Invite a user to group
	If success, the target user will have a 'invited' role on target group
	"""
	getCurrentUserInfo().check_may_invite_users(group)
	target_account = get_user_info(user)
	UserError.check(target_account.exists(),
	                code=UserError.ENTITY_DOES_NOT_EXIST, message="Account with that name does not exist")
	UserError.check(get_backend_users_proxy().group_exists(group),
	                code=UserError.ENTITY_DOES_NOT_EXIST, message="Group with that name does not exist")
	return target_account.set_group_role(group, 'invited')

def account_handle_invite(group, operation):
	"""
	Handle the group inviting
	if accept, set the role to 'user'
	if decline, remove the group role info
	"""
	user = getCurrentUserInfo()
	user.check_may_handle_invite(group)
	if operation is True or operation == 'accept':
		user.set_group_role(group, 'user')
	elif operation is False or operation == 'decline':
		user.set_group_role(group, None)
	else:
		raise Exception("Invalid parameter")
