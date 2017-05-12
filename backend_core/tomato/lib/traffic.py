import os
import requests


def make_pack(traffic_info):
	if not os.path.exists("/work"):
		os.mkdir("/work")
	if os.path.exists("/work/%s/" % traffic_info["id"]):
		os.system("rm  /work/%s/*" % traffic_info["id"])
	else:
		os.mkdir("/work/%s" % traffic_info["id"])
	on_event = "0.0 ON 1 %s DST %s/%s %s" % (traffic_info["protocol"],traffic_info["dest_ip"] , traffic_info["dest_port"] , traffic_info["pattern"])
	print "pattern " + on_event + "\n"
	off_event  = "%s OFF 1" % (traffic_info["off_time"])
	f = open("/work/%s/auto_exec.sh" % traffic_info["id"], "w")
	f.write('#!/bin/bash' + '\n' + 'mgen event \"%s\" event \"%s\"' % (on_event , off_event))
	f.close()
	os.chdir("/work/%s/" % traffic_info["id"])
	os.system("tar czvf %s.tar.gz auto_exec.sh" % traffic_info["id"])
	#return "/work/%s.tar.gz" % name
	return "/work/%s/%s.tar.gz" % (traffic_info["id"] , traffic_info["id"])

def send_pack(element_info , pack_dir, key):
	url = "http://" + str(element_info["host_info"]["address"]) + ":" + str(element_info["host_info"]["fileserver_port"]) + "/" + key + "/upload"
	print url
	if os.path.exists(pack_dir):
		print pack_dir + " exist"
	upload = {"file":open(pack_dir, "rb")}
	r = requests.post(url, files=upload)
	print r.text
	return r.text