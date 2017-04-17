from ..topgroup import Topgroup

def topgroup_create(top_id = None, **data):
	topgroup = Topgroup.create(top_id, **data)
	return topgroup.info()

def topgroup_addtop(top_id, **data):
	topgroup = Topgroup.get(data['name'])
	topgroup.add(id)
	return topgroup.info()

def topgroup_remove(name):
	Topgroup.remove(name)

def topgroup_deletetop(name, id):
	topgroup = Topgroup.get(name)
	topgroup.remove_top(id)
	return topgroup.info()

def topgroup_list():
	return Topgroup.list()

def topgroup_info(name):
	topgroup = Topgroup.get(name)
	return topgroup.info()

def topgroup_topology(name):
	topgroup = Topgroup.get(name)
	return topgroup.topology
