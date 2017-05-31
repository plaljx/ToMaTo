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

def traffic_start(element_id, traffic_ids):
    for traffic_id in traffic_ids:
        res = traffic.Traffic.traffic_start(element_id, traffic_id)
    return res

'''

import os
import requests
from .elements import element_action, element_info
action = "rextfv_upload_grant"
action_use = "rextfv_upload_use"


def traffic_start(element_id, trafficIds):
	for trafficId in trafficIds:
		pack_dir = make_pack(trafficId)
		send_result=send_pack(element_id, pack_dir)
		action_result = element_action(element_id,action_use)
	return action_result

def get_element(id):
	info = element_info(id)
	return info

def get_send_key(id, action, params={}):
	res = element_action(id, action, params)
	return res

def make_pack(traffic_id):
	traffic_info = _getTraffic(traffic_id)
	if os.path.exists("/work/%s/" % traffic_id):
		os.system("rm  /work/%s/*" % traffic_id)
	else:
		os.mkdir("/work/%s" % traffic_id)
	on_event = "0.0 ON 1 UDP DST %s/%s %s" % (traffic_info.dest_ip , traffic_info.dest_port , traffic_info.pattern)
	print "pattern" + on_event + "\n"
	off_event  = "20.0 OFF 1"
	f = open("/work/%s/auto_exec.sh" % traffic_id, "w")
	f.write('#!/bin/bash' + '\n' + 'mgen event \"%s\" event \"%s\"' % (on_event , off_event))
	f.close()
	os.chdir("/work/%s/" % traffic_id)
	os.system("tar czvf %s.tar.gz auto_exec.sh" % traffic_id)
	#return "/work/%s.tar.gz" % name
	return "/work/%s/%s.tar.gz" % (traffic_id , traffic_id)

def send_pack(element_id , pack_dir):
	info = get_element(element_id)
	key = get_send_key(element_id, action)
	url = "http://" + str(info["host_info"]["address"]) + ":" + str(info["host_info"]["fileserver_port"]) + "/" + key + "/upload"

	if os.path.exists(pack_dir):
		print pack_dir + "exist"
	upload = {"file":open(pack_dir, "rb")}
	r = requests.post(url, files=upload)
	print r.text
    return r.text
'''