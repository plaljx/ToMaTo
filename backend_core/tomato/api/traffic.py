#author Nong Caihua 2016.12.29

from ..import traffic
from .. import topology
import time


def _getTraffic(id_):
	res = traffic.get(id_)
	return res

def traffic_list(topology_fileter=None):
	res = traffic.getAll(topology_id=topology_fileter) if topology_fileter else traffic.getAll()
	return [r.info() for r in res]

def traffic_create(topology_id, attrs=None):
	res = traffic.create(topology_id,**attrs)
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

def traffic_start(traffic_ids):
	print "start time"
	print time.time()
	for traffic_id in traffic_ids:
		res = traffic.traffic_start(traffic_id)
	return res

def mutil_traffic_start(elements, attrs=None):
	if not attrs:
		return None
	print elements
	res = traffic.mutil_traffic_start(elements, attrs)
	print time.time()
	return None
