from ..lib.service import get_backend_core_proxy

def traffic_create(topology_id, attrs=None):
	if not attrs:
		attrs = {}
	res = get_backend_core_proxy().traffic_create(topology_id, attrs)
	return res

def traffic_list(topology_fileter=None):
	print topology_fileter
	res = get_backend_core_proxy().traffic_list(topology_fileter = topology_fileter)
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

def traffic_start(trafficIds):
	print trafficIds[0]
	res = get_backend_core_proxy().traffic_start(trafficIds)
	return res

def mutil_traffic_start(elements, attrs = None):
	if not attrs:
		return  None
	res = get_backend_core_proxy().mutil_traffic_start(elements,attrs);
	return res