from ..lib.service import get_backend_core_proxy

def traffic_create(element_id, attrs=None):
	if not attrs:
		attrs = {}
	res = get_backend_core_proxy().traffic_create(element_id, attrs)
	return res

def traffic_list(element_fileter=None):
	print element_fileter
	res = get_backend_core_proxy().traffic_list(element_fileter = element_fileter)
	return res

def traffic_info(id):
	res = get_backend_core_proxy().traffic_info(id)
	return res

def traffic_remove(id):
	res = get_backend_core_proxy().traffic_remove(id)
	return res

def traffic_modify(id, attrs=None):
	if not attrs:
		attrs = {}
	res = get_backend_core_proxy().traffic_modify(id, attrs)
	return res