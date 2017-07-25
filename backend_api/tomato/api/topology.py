# -*- coding: utf-8 -*-
# ToMaTo (Topology management software) 
# Copyright (C) 2010 Dennis Schwerdel, University of Kaiserslautern
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from api_helpers import getCurrentUserInfo, getCurrentUserName
from ..lib.topology_role import Role
from ..lib.remote_info import get_topology_info, get_topology_list, TopologyInfo,get_organization_info
from ..lib.service import get_backend_core_proxy,get_backend_users_proxy
from ..lib.error import UserError
from ..lib.group_role import GroupRole

def topology_create():
	"""
	Creates an empty topology.
	
	Return value:
	  The return value of this method is the info dict of the new topology as
	  returned by :py:func:`topology_info`. This info dict also contains the
	  topology id that is needed for further manipulation of that object.
	"""
	getCurrentUserInfo().check_may_create_topologies()
	return TopologyInfo.create(getCurrentUserName())

def topology_remove(id): #@ReservedAssignment
	"""
	Removes and empty topology.
	
	Return value:
	  The return value of this method is ``None``.
	  
	Exceptions:
	  The topology must not contain elements or connections, otherwise the call
	  will fail.
	"""
	topl = get_topology_info(id)
	UserError.check(topl.exists(), code=UserError.ENTITY_DOES_NOT_EXIST, message="Topology with that name does not exist")
	getCurrentUserInfo().check_may_remove_topology(topl)
	topl.remove()

def topology_modify(id, attrs): #@ReservedAssignment
	"""
	Modifies a topology, configuring it with the given attributes.
   
	Currently the only supported attribute for topologies is ``name``.
   
	Additional to the attributes that are supported by the topology,
	all attributes beginning with an underscore (``_``) will be accepted.
	This can be used to store addition information needed by a frontend.
	
	Parameter *id*:
	  The parameter *id* identifies the topology by giving its unique id.
	 
	Parameter *attrs*:
	  The attributes of the topology can be given as the parameter *attrs*. 
	  This parameter must be a dict of attributes.
	
	Return value:
	  The return value of this method is the info dict of the topology as 
	  returned by :py:func:`topology_info`. This info dict will reflect all
	  attribute changes.	
	"""
	topl = get_topology_info(id)
	UserError.check(topl.exists(), code=UserError.ENTITY_DOES_NOT_EXIST, message="Topology with that name does not exist")
	getCurrentUserInfo().check_may_modify_topology(topl, attrs)
	return topl.modify(attrs)

def topology_action(id, action, params=None): #@ReservedAssignment
	"""
	Performs an action on the whole topology (i.e. on all elements) in a smart
	way.
	
	The following actions are currently supported by topologies:
	
	  ``prepare``
		This action will execute the action ``prepare`` on all elements in the 
		state ``created``.
	  
	  ``destroy``
		This action will first execute the action ``stop`` on all elements in 
		the state ``started`` and then the action ``destroy`` on all elements 
		in the state ``prepared``.
		Note that the states of the elements will be re-evaluated after the 
		first round of actions.

	  ``start``
		This action will first execute the action ``prepare`` on all elements
		in the state ``created`` and then the action ``start`` on all elements
		in the state ``prepared``.
		Note that the states of the elements will be re-evaluated after the 
		first round of actions.
	  
	  ``stop``
		This action will execute the action ``stop`` on all elements in the 
		state ``started``.
		
	Parameter *id*:
	  The parameter *id* identifies the topology by giving its unique id.

	Parameter *action*:
	  The parameter *action* is the action to execute on the topology.
	 
	Parameter *params*:
	  The parameters for the action (if needed) can be given as the parameter
	  *params*. This parameter must be a dict if given.
	
	Return value:
	  The return value of this method is  **not the info dict of the 
	  topology**. Instead this method returns the result of the action. Changes
	  of the action to the topology can be checked using 
	  :py:func:`~topology_info`.	
	"""
	if not params: params = {}
	topl = get_topology_info(id)
	UserError.check(topl.exists(), code=UserError.ENTITY_DOES_NOT_EXIST, message="Topology with that name does not exist")
	getCurrentUserInfo().check_may_run_topology_action(topl, action, params)
	return topl.action(action, params)

def topology_info(id, full=False): #@ReservedAssignment
	"""
	Retrieves information about a topology.
	
	Parameter *id*:
	  The parameter *id* identifies the topology by giving its unique id.

	Parameter *full*:
	  If this parameter is ``True``, the fields ``elements`` and 
	  ``connections`` will be a list holding all information of 
	  :py:func:`~backend.tomato.api.elements.element_info`
	  and :py:func:`~backend.tomato.api.connections.connection_info`
	  for each component.
	  Otherwise these fields will be lists holding only the ids of the
	  respective objects.

	Return value:
	  The return value of this method is a dict containing information
	  about this topology:

	``id``
	  The unique id of the topology.
	  
	``elements``
	  A list with all elements. Depending on the parameter *full* this list
	  includes the full information of the elements as given by 
	  :py:func:`~backend.tomato.api.element.element_info` or only the id of the
	  element.

	``connections``
	  A list with all connections. Depending on the parameter *full* this list
	  includes the full information of the connections as given by 
	  :py:func:`~backend.tomato.api.connection.connection_info` or only the id
	  of the connection.
	  
	``attrs``
	  A dict of attributes of this topology. If this topology does not have
	  attributes, this field is ``{}``.	

	``usage``
	  The latest usage record of the type ``5minutes``. See 
	  :doc:`/docs/accountingdata` for the contents of the field.

	``permissions``
	  A dict with usernames as the keys and permission levels as values.
	"""


	topl = get_topology_info(id)
	UserError.check(topl.exists(), code=UserError.ENTITY_DOES_NOT_EXIST, message="Topology with that name does not exist")
	getCurrentUserInfo().check_may_view_topology(topl)
	if full:
		return get_backend_core_proxy().topology_info(id, full)
	else:
		return topl.info(update=True)

def topology_list(full=False, showAll=False, organization=None): #@ReservedAssignment
	"""
	Retrieves information about all topologies the user can access.

	Parameter *full*:
	  See :py:func:`~topology_info` for this parameter.
	 
	Return value:
	  A list with information entries of all topologies. Each list entry
	  contains exactly the same information as returned by 
	  :py:func:`topology_info`. If no topologies exist, the list is empty. 
	"""

	if organization:
		UserError.check(get_organization_info(organization).exists(),
						code=UserError.ENTITY_DOES_NOT_EXIST, message="Organization with that name does not exist")

		getCurrentUserInfo().check_may_list_organization_topologies(organization)
	if showAll:
		getCurrentUserInfo().check_may_list_all_topologies()
	return get_topology_list(full, organization_filter=organization, username_filter=(None if showAll else getCurrentUserName()))

def topology_set_permission(id, user, role): #@ReservedAssignment
	"""
	Grants/changes permissions for a user on a topology. See :doc:`permissions`
	for further information about available roles and their meanings.

	You may not change your own role.
	
	Parameter *id*:
	  The parameter *id* identifies the topology by giving its unique id.

	Parameter *user*:
	  The name of the user.

	Parameter *role*:
	  The name of the role for this user. If the user already has a role,
	  if will be changed.
	"""
	if role is None:
		role = Role.null

	topl = get_topology_info(id)
	UserError.check(topl.exists(), code=UserError.ENTITY_DOES_NOT_EXIST, message="Topology with that name does not exist")
	UserError.check(get_backend_users_proxy().user_exists(user), code=UserError.ENTITY_DOES_NOT_EXIST, message="User with that name does not exist")
	UserError.check(topl.existsRole(role), code=UserError.INVALID_VALUE, message="Role with that name does not exist")

	getCurrentUserInfo().check_may_grant_permission_for_topologies(topl, role, user)
	return topl.set_permission(user, role)
	
def topology_usage(id): #@ReservedAssignment
	"""
	Retrieves aggregated usage statistics for a topology.
	
	Parameter *id*:
	  The parameter *id* identifies the topology by giving its unique id.

	Return value:
	  Usage statistics for the given topology according to 
	  :doc:`/docs/accountingdata`.
	"""
	target_topology = get_topology_info(id)
	UserError.check(target_topology.exists(), code=UserError.ENTITY_DOES_NOT_EXIST, message="Topology with that name does not exist")
	getCurrentUserInfo().check_may_view_topology_usage(target_topology)
	return target_topology.get_usage(hide_no_such_record_error=True)

def topology_get_sub_topologies(topo_id):
	"""
	Return list of sub-topology info.
	This will add `allowed` value, so that front end could know which sub-topology is able to shown.
	"""
	# TODO: Permission Checking
	user = getCurrentUserInfo()
	topl = get_topology_info(topo_id)
	sub_topologies = get_backend_core_proxy().topology_get_sub_topologies(topo_id)
	if user.may_view_all_sub_topologies(topl):
		for sub_topology in sub_topologies:
			sub_topology["permitted"] = True
	else:
		groups_set = set(user.get_groups(GroupRole.user))
		for sub_topology in sub_topologies:
			if groups_set.isdisjoint(sub_topology["groups"]):
				sub_topology["permitted"] = False
			else:
				sub_topology["permitted"] = True
	return sub_topologies

def topology_add_sub_topology(topo_id, name):
	# TODO: Permission Checking
	return get_backend_core_proxy().topology_add_sub_topology(topo_id, name)

def topology_remove_sub_topology(topo_id, name):
	# TODO: Permission Checking
	return get_backend_core_proxy().topology_remove_sub_topology(topo_id, name)

def sub_topology_get_groups(topo_id, sub_topo):
	# TODO: Permission Checking
	return get_backend_core_proxy().sub_topology_get_groups(topo_id, sub_topo)

def sub_topology_add_group(topo_id, sub_topo, group):
	# TODO: Permission Checking
	UserError.check(
		get_backend_users_proxy().group_exists(group),
		code=UserError.ENTITY_DOES_NOT_EXIST,
		message="User with that name does not exist")
	return get_backend_core_proxy().sub_topology_add_group(topo_id, sub_topo, group)

def sub_topology_remove_group(topo_id, sub_topo, group):
	# TODO: Permission Checking
	return get_backend_core_proxy().sub_topology_remove_group(topo_id, sub_topo, group)
