import os
import requests
import yaml
import time

default_setting = yaml.load("""
tools: [MGEN, DITG]
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
    source: mgen event "+start_time+ ON 1 +protocol+ ?source_port? DST +dest_ip+/+dest_port+ ?pattern?" event "+off_time+ OFF 1"
    pattern:
      PERIODIC: PERIODIC [+packet_rate+ +packet_size+]
      POISSON: POISSON [+packet_rate+ +packet_size+]
      BRUST: BRUST [RANDOM +packet_rate+ PERIODIC [+packet_rate+  +packet_size+] EXP 5.0]
      JITTER: JITTER [+packet_rate+ +packet_size+ .5]
    source_port: SRC +source_port+
    
DITG:
  name: DITG
  source_port: [True, False]
  dest_ip: [True, False]
  dest_port: [True, False]
  start_time: [True, False]
  off_time: [True, False]
  protocol: [True, True, TCP, UDP, ICMP, Telnet, DNS, Quake3, VoIP]
  pattern: [PERIODIC, UNIFORM, Exponential, Normal, POISSON]
  packet_rate: [True, False]
  packet_size: [True, True]
  ttl: [True, False]
  priority: 9
  expressions: [[off_time, 3, 1000 , off_time]]
  command:
    source: '/usr/share/D-ITG-2.8.1-r1023/bin/ITGSend ?protocol? -a +dest_ip+ -rp +dest_port+ ?pattern? -l +off_time+'
    dest:  '/usr/share/D-ITG-2.8.1-r1023/bin/ITGRecv'
    protocol:
      TCP: -T TCP
      UDP: -T UDP
      ICMP: -T ICMP 5
      Telnet: Telnet
      DNS: DNS
      Quake3: Quake3
      VoIP: VoIP -x G.711.2 -h RTP -VAD
    pattern:
      PERIODIC: -C +packet_rate+ -c +packet_size+
      UNIFORM:  -U 800 1600 -c +packet_size+
      Exponential: -E 10 -c +packet_size+ 
      Normal: -N 0 1 +packet_size+
      POISSON: -O 100 +packet_size+
""")

def get_traffic_modul():
	return default_setting

def make_command_file(target, command):
	if command is None:
		return None
	if not os.path.exists("/work"):
		os.mkdir("/work")
	if os.path.exists("/work/%s" % target  ):
		os.system("rm  /work/%s/*" % target)
	else:
		os.mkdir("/work/%s" % target)
	f = open("/work/%s/auto_exec.sh" % target, "w")
	f.write('#!/bin/bash' + '\n' + '%s' % command)
	f.close()
	os.chdir("/work/%s" % target)
	os.system("tar czvf %s.tar.gz auto_exec.sh" % target)
	return  "/work/%s/%s.tar.gz" % (target, target)

def send_file(element_info, file_dir, key):
	url = "http://" + str(element_info["host_info"]["address"]) + ":" + str(element_info["host_info"]["fileserver_port"]) + "/" + key + "/upload"
	upload = {"file":open(file_dir, "rb")}
	r = requests.post(url, files=upload)
	print r.text
	return r.text

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


