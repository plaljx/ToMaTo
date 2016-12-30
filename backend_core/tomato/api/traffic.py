#author Nong Caihua 2016.12.29

from ..import traffic


def _getTraffic(id_):
	res = traffic.get(id_)
	return res

def traffic_list(element_fileter=None):
	res = traffic.getAll(element_id=element_fileter) if element_fileter else traffic.getAll()
	return [r.info() for r in res]

def traffic_create(element_id, attrs=None):
	res = traffic.create(element_id,**attrs)
	return res.info()

def traffic_info(id):
	res = _getTraffic(id)
	return res.info()

def traffic_remove(id):
	traffic =_getTraffic(id)
	traffic.remove()

def traffic_modify(id, attrs=None):
	traffic = _getTraffic(id)
	res = traffic.modify(**attrs)
	return res

