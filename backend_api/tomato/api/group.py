from ..lib.error import InternalError, UserError
from ..lib.service import get_backend_users_proxy, get_backend_core_proxy, get_backend_accounting_proxy
from api_helpers import getCurrentUserInfo
from ..lib.remote_info import get_user_info, get_user_list_by_group, get_topology_info
from ..lib.group_role import GroupRole

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
	if role == GroupRole.owner:
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
	return target_account.set_group_role(group, GroupRole.invited)

def account_handle_invite(group, operation):
	"""
	Handle the group inviting
	if accept, set the role to 'user'
	if decline, remove the group role info
	"""
	# TODO: may add 'user' as parameter, since URL contains user's name
	user = getCurrentUserInfo()
	user.check_may_handle_invite(group)
	if operation is True or operation == GroupRole.accept:
		user.set_group_role(group, GroupRole.user)
	elif operation is False or operation == GroupRole.decline:
		user.set_group_role(group, None)
	else:
		raise Exception("Invalid parameter")

def group_apply(user, group):
	"""
	User apply to join a group
	If success, the target user will have a 'applying' role on target group
	"""
	current_user = getCurrentUserInfo()
	target_account = get_user_info(user)
	UserError.check(current_user.name == target_account.name,
	                code=UserError.DENIED, message="You are not user %s" % target_account.name)
	current_user.check_may_apply_for_group(group)
	return target_account.set_group_role(group, GroupRole.applying)

def handle_application(user, group, operation):
	"""
	Handle the group application from a user
	If accept, set the role to 'user'
	If decline, remove the group role info
	"""
	current_user = getCurrentUserInfo()
	target_account = get_user_info(user)
	current_user.check_may_handle_application(group)
	UserError.check(target_account.get_group_role(group) == GroupRole.applying,
	                code=UserError.DENIED, message="The user %s is not applying for the group" % target_account.name)
	if operation is True or operation == GroupRole.accept:
		target_account.set_group_role(group, GroupRole.user)
	elif operation is False or operation == GroupRole.decline:
		target_account.set_group_role(group, None)
	else:
		raise Exception("Invalid parameter")

def group_topology_list(group=None):
	"""
	Return the group topology list
	if group is None, this will return all group permitted topologies
	"""
	current_user = getCurrentUserInfo()
	if group is None:
		# TODO: Permission Checking
		groups = current_user.get_groups(min_role=GroupRole.user)
		return get_backend_core_proxy().topology_list_by_group(groups)
	else:
		current_user.check_may_list_group_topologies(group)
		return get_backend_core_proxy().topology_list_by_group(group)

def topology_add_group(topl_id, group):
	topl = get_topology_info(topl_id)
	UserError.check(topl.exists(), code=UserError.ENTITY_DOES_NOT_EXIST, message="Topology with that name does not exist")
	UserError.check(get_backend_users_proxy().group_exists(group), code=UserError.ENTITY_DOES_NOT_EXIST, message="Group with that name does not exist")
	# TODO
	# getCurrentUserInfo().check_may_modify_group_info_for_topologies(topl)
	return topl.add_group(group)

def topology_remove_group(topl_id, group):
	topl = get_topology_info(topl_id)
	UserError.check(topl.exists(), code=UserError.ENTITY_DOES_NOT_EXIST, message="Topology with that name does not exist")
	UserError.check(get_backend_users_proxy().group_exists(group), code=UserError.ENTITY_DOES_NOT_EXIST, message="Group with that name does not exist")
	# TODO
	# getCurrentUserInfo().check_may_modify_group_info_for_topologies(topl)
	return topl.remove_group(group)
