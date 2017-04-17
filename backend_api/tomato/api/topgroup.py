from ..lib.service import get_backend_core_proxy

def topgroup_create(top_id = None, **data):
	info = get_backend_core_proxy().topgroup_create(top_id, **data)
	return info


def topgroup_addtop(top_id, **data):
	info = get_backend_core_proxy().topgroup_addtop(top_id, **data)
	return info

def topgroup_remove(name):
	info = get_backend_core_proxy().topgroup_remove(name)
	return info

def topgroup_deletetop(name, id):
	info = get_backend_core_proxy().topgroup_deletetop(name, id)
	return info

def topgroup_list():
	return get_backend_core_proxy().topgroup_list()

def topgroup_info(name):
	return get_backend_core_proxy().topgroup_list(name)