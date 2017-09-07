# from ..topgroup import Topgroup
#
# def topgroup_create(top_id = None, **data):
# 	topgroup = Topgroup.create(top_id, **data)
# 	return topgroup.info()
#
# def topgroup_addtop(top_id, **data):
# 	topgroup = Topgroup.get(data['name'])
# 	topgroup.add(top_id, data['name'])
# 	return topgroup.info()
#
# def topgroup_remove(name):
# 	Topgroup.remove(name)
#
# def topgroup_deletetop(name, id):
# 	topgroup = Topgroup.get(name)
# 	topgroup.remove_top(id)
# 	return topgroup.info()
#
# def topgroup_list(top_id = None, **data):
# 	return Topgroup.list(top_id, **data)
#
# def topgroup_info(top_id = None, **data):
# 	topgroup = Topgroup.get_bytop(top_id, **data)
# 	return topgroup.info()
#
# def topgroup_topology(name):
# 	topgroup = Topgroup.get(name)
# 	return topgroup.topology
