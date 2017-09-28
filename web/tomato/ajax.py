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

from lib import wrap_json

@wrap_json
def topology_info(api, request, id): #@ReservedAssignment
	info = api.topology_info(id, True)
	return info

@wrap_json
def topology_modify(api, request, id, **attrs): #@ReservedAssignment
	info = api.topology_modify(id, attrs)
	return info

@wrap_json
def topology_action(api, request, id, action, params={}): #@ReservedAssignment
	res = api.topology_action(id, action, params)
	info = api.topology_info(id)
	return (res, info)

@wrap_json
def topology_remove(api, request, id): #@ReservedAssignment
	return api.topology_remove(id)

@wrap_json
def topology_set_permission(api, request, id, user, permission): #@ReservedAssignment
	return api.topology_set_permission(id, user, permission)

@wrap_json
def element_create(api, request, topid, type, parent=None, **attrs): #@ReservedAssignment
	info = api.element_create(topid, type, parent, attrs)
	return info

@wrap_json
def element_info(api, request, id, fetch=False): #@ReservedAssignment
	info = api.element_info(id, fetch)
	return info

@wrap_json
def element_modify(api, request, id, **attrs): #@ReservedAssignment
	info = api.element_modify(id, attrs)
	return info

@wrap_json
def element_action(api, request, id, action, params={}): #@ReservedAssignment
	res = api.element_action(id, action, params)
	info = api.element_info(id)
	return (res, info)

@wrap_json
def element_remove(api, request, id): #@ReservedAssignment
	res = api.element_remove(id)
	return res

@wrap_json
def element_execute_command(api, request, id, **data):
    # /ajax/element/<id>/exec
	# data: { path: <str>, args: <list> }
	# res: { return_code: <number>, output: <str>}
	path, args = data['path'], data['args']
	res = api.element_execute_command(id, path, args)
	return res

@wrap_json
def connection_create(api, request, elements, **attrs):
	info = api.connection_create(elements[0], elements[1], attrs)
	return info

@wrap_json
def connection_info(api, request, id, fetch=False): #@ReservedAssignment
	info = api.connection_info(id, fetch)
	return info

@wrap_json
def connection_modify(api, request, id, **attrs): #@ReservedAssignment
	info = api.connection_modify(id, attrs)
	return info

@wrap_json
def connection_action(api, request, id, action, params={}): #@ReservedAssignment
	res = api.connection_action(id, action, params)
	info = api.connection_info(id)
	return (res, info)

@wrap_json
def connection_remove(api, request, id): #@ReservedAssignment
	res = api.connection_remove(id)
	return res

@wrap_json
def account_info(api, request, name):
	res = api.account_info(name)
	return res

@wrap_json
def account_modify(api, request, name, **attrs): #@ReservedAssignment
	info = api.account_modify(name, attrs)
	request.session["user"].updateData(api, data=info)
	return info

# by Chang Rui
@wrap_json
def save_as_scenario(api, request, id_, **data):
	# return "Save As Scenario from web. id=%s, data=%s" % (id, data)
	info = api.scenario_save(id_, data)
	return info

@wrap_json
def scenario_remove(api, request, id_, **data):
	response = api.scenario_remove(id_)
	return response

@wrap_json
def scenario_deploy(api, request, id_, **data):
	response = api.scenario_deploy(id_)
	return response

@wrap_json
def scenario_modify(api, request, id_, **data):
	response = api.scenario_modify(id_, data)
	return response

#add by Nong Caihua at 2016.12.29
@wrap_json
def traffic_info(api, request, id):
	info = api.traffic_info(id)
	return info

@wrap_json
def traffic_create(api, request, element_id,**attrs):
	res = api.traffic_create(element_id, attrs)
	return res

@wrap_json
def traffic_list(api, request, element_id=None):
	res = api.traffic_list(element_id)
	return res

@wrap_json
def traffic_remove(api, request, traffic_id):
	res = api.traffic_remove(traffic_id)
	return res

@wrap_json
def traffic_modify(api, request,element_id, **attrs):
	res = api.traffic_modigy(element_id, attrs)
	return res

@wrap_json
def traffic_start(api, request,element_id,selected):
	#selected:The Array of traffics' id which are selected to start
	print element_id
	print selected
	if not selected:
		return 	None
	res = api.traffic_start(element_id, selected)
	return res

@wrap_json
def group_info(api, request, group):
	return api.group_info(group)

@wrap_json
def topology_add_group(api, request, topl_id, group):
	return api.topology_add_group(topl_id, group)

@wrap_json
def topology_remove_group(api, request, topl_id, group):
	return api.topology_remove_group(topl_id, group)



@wrap_json
def topology_get_sub_topologies(api, request, topo_id):
	"""
	/ajax/topology/<topo_id>/subtopology
	"""
	return api.topology_get_sub_topologies(topo_id)

@wrap_json
def topology_add_sub_topology(api, request, topo_id, **data):
	"""
	/ajax/topology/<topo_id>/subtopology/add
	data: {name: <sub_topo_name>}
	"""
	name = data.get('name')
	return api.topology_add_sub_topology(topo_id, name)

@wrap_json
def topology_sub_topology_info(api, request, topo_id, sub_topo_id):
	"""
	/ajax/topology/<topo_id>/subtopology/<subtopo_id>
	"""
	return api.topology_sub_topology_info(topo_id, sub_topo_id)

@wrap_json
def topology_remove_sub_topology(api, request, topo_id, sub_topo_id):
	"""
	/ajax/topology/<topo_id>/subtopology/<sub_topo_id>/remove
	"""
	return api.topology_remove_sub_topology(topo_id, sub_topo_id)

@wrap_json
def sub_topology_add_group(api, request, topo_id, sub_topo, **data):
	"""
	/ajax/topology/<topo_id>/subtopology/<sub_topo_id>/add_group
	data: {name: <group_name>}
	"""
	group = data.get('group')
	return api.sub_topology_add_group(topo_id, sub_topo_id, group)

@wrap_json
def sub_topology_remove_group(api, request, topo_id, sub_topo, **data):
	"""
	/ajax/topology/<topo_id>/subtopology/<sub_topo_id>/remove_group
	data: {name: <group_name>}
	"""
	group = data.get('group')
	return api.sub_topology_remove_group(topo_id, sub_topo, group)
