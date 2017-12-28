import os
import requests
import yaml

default_setting = yaml.load("""
modul: [MGEN]
attributes: [source_port, dest_ip, dest_port, start_time, off_time, protocol, pattern, packet_size, packet_rate, tos, ttl]
MGEN:
  name: MGEN
  source_port: [True, False]
  dest_ip: [True, True]
  dest_port: [True, True]
  start_time: [True, False]
  off_time: [True, True]
  protocol: [True, True, TCP, UDP]
  pattern: [True, True, PERIODIC, POISSON, BRUST, JITTER]
  packet_size: [True, True]
  packet_rate: [True, True]
  tos: [True, False]
  priority: 10
  command:
    source: MGEN EVENT "+start_time+ ON 1 -source_port- DST +protocol+ +destination_ip+/+destination_port+ -pattern-" EVENT "+off_time+ OFF 1"
    pattern:
      PERIODIC: PERIODIC [+packet_rate+, +packet_size+]
      POISSON: POISSON [+packet_rate%, %packet_size+]
      BRUST: BRUST [RANDOM +packet_rate+ PERIODIC [+packet_rate+  +packet_size+] EXP 5.0]
      JITTER: JITTER [+packet_rate+, +packet_size+ .5]
    source_port: SRC +source_port+
""")

def get_traffic_modul():
	return default_setting

def make_command_file(traffic_info, tool, source_command):
	return None

def make_mgen_pack(traffic_info):
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

def make_ditg_pack(event ,element_id ,  **attrs):
	if not os.path.exists("/ditg"):
		os.mkdir("/ditg")
	if os.path.exists("/ditg/%s/" % element_id):
		os.system("rm /ditg/%s/*" % element_id)
	else:
		os.mkdir("/ditg/%s" % element_id)
	cmd = ""
	if event == "receive":
		cmd = "/usr/share/D-ITG-2.8.1-r1023/bin/ITGRecv"
	if event == "send":
		cmd = "/usr/share/D-ITG-2.8.1-r1023/bin/ITGSend -T %s -a 10.0.0.3 -c 512 -C 100 -t %s -l sender.log -x receiver.log " \
			  %(attrs["protocol"] ,  attrs["duration"])
		print cmd
	f = open("/ditg/%s/auto_exec.sh" % element_id, "w")
	f.write('#!/bin/bash' + '\n' + '%s' % cmd)
	f.close()
	os.chdir("/ditg/%s/" % element_id)
	os.system("tar czvf %s.tar.gz auto_exec.sh" % element_id)
	# return "/work/%s.tar.gz" % name
	return "/ditg/%s/%s.tar.gz" % (element_id, element_id)


