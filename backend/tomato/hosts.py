# -*- coding: utf-8 -*-
# ToMaTo (Topology management software) 
# Copyright (C) 2010 Dennis Schwerdel, University of Kaiserslautern
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from django.db import models

import config, fault, util, sys, atexit
from django.db.models import Q, Sum

class ClusterState:
	MASTER = "M"
	NODE = "N"
	NONE = "-"

class Host(models.Model):
	SSH_COMMAND = ["ssh", "-q", "-oConnectTimeout=30", "-oStrictHostKeyChecking=no", "-oUserKnownHostsFile=/dev/null", "-oPasswordAuthentication=false", "-i%s" % config.remote_ssh_key]
	RSYNC_COMMAND = ["rsync", "-a", "-e", " ".join(SSH_COMMAND)]
	
	group = models.CharField(max_length=10, blank=True)
	name = models.CharField(max_length=50, unique=True)
	enabled = models.BooleanField(default=True)
	port_range_start = models.PositiveSmallIntegerField(default=7000)
	port_range_count = models.PositiveSmallIntegerField(default=1000)
	vmid_range_start = models.PositiveSmallIntegerField(default=1000)
	vmid_range_count = models.PositiveSmallIntegerField(default=200)
	bridge_range_start = models.PositiveSmallIntegerField(default=1000)
	bridge_range_count = models.PositiveSmallIntegerField(default=1000)
	hostserver_port = models.PositiveSmallIntegerField(null=True)
	hostserver_basedir = models.CharField(max_length=100, null=True)
	hostserver_secret_key = models.CharField(max_length=100, null=True)

	def __unicode__(self):
		return self.name

	def fetch_all_templates(self, task):
		for tpl in Template.objects.all(): # pylint: disable-msg=E1101
			tpl.upload_to_host(self, task)

	def check_save(self, task):
		task.subtasks_total = 9
		self.check(task)
		self.save()
		task.done()

	def check(self, task):
		"""
		Checks if the host is reachable, login works and the needed software is installed
		
		@param task: the task object to use
		@type task: tasks.TaskStatus
		@raise AssertionError: is something looks wrong
		@rtype: None   
		"""
		if config.remote_dry_run:
			return True
		task.output.write("checking login...\n")
		res = self.get_result("true; echo $?")
		task.output.write(res)
		assert res.split("\n")[-2] == "0", "Login error"
		task.subtasks_done = task.subtasks_done + 1
		
		task.output.write("checking for openvz...\n")
		res = self.get_result("vzctl --version; echo $?")
		task.output.write(res)
		assert res.split("\n")[-2] == "0", "OpenVZ error"
		task.subtasks_done = task.subtasks_done + 1
		
		task.output.write("checking for kvm...\n")
		res = self.get_result("qm list; echo $?")
		task.output.write(res)
		assert res.split("\n")[-2] == "0", "OpenVZ error"
		task.subtasks_done = task.subtasks_done + 1
		
		task.output.write("checking for bridge utils...\n")
		res = self.get_result("brctl --version; echo $?")
		task.output.write(res)
		assert res.split("\n")[-2] == "0", "brctl error"
		task.subtasks_done = task.subtasks_done + 1
		
		task.output.write("checking for dummynet...\n")
		res = self.get_result("modprobe ipfw_mod && ipfw list; echo $?")
		task.output.write(res)
		assert res.split("\n")[-2] == "0", "dumynet error"
		task.subtasks_done = task.subtasks_done + 1
		
		task.output.write("checking for tinc...\n")
		res = self.get_result("tincd --version; echo $?")
		task.output.write(res)
		assert res.split("\n")[-2] == "0", "tinc error"
		task.subtasks_done = task.subtasks_done + 1
		
		task.output.write("checking for timeout...\n")
		res = self.get_result("timeout 1 true; echo $?")
		task.output.write(res)
		assert res.split("\n")[-2] == "0", "timeout error"
		task.subtasks_done = task.subtasks_done + 1
		
		task.output.write("checking for hostserver...\n")
		res = self.get_result("/etc/init.d/tomato-hostserver status; echo $?")
		task.output.write(res)
		assert res.split("\n")[-2] == "0", "hostserver error"
		task.subtasks_done = task.subtasks_done + 1
		
		task.output.write("checking cluster membership...\n")
		cluster_state = self.cluster_state()
		if cluster_state == ClusterState.MASTER:
			task.output.write("node is cluster master\n\n")
		elif cluster_state == ClusterState.NODE:
			task.output.write("node is cluster member\n\n")
		elif cluster_state == ClusterState.NONE:
			task.output.write("node is not part of a cluster\n\n")
		
		self.fetch_hostserver_config()
		self.hostserver_cleanup(task)
		self.fetch_all_templates(task)
				
	def fetch_hostserver_config(self):
		res = self.get_result(". /etc/tomato-hostserver.conf; echo $port; echo $basedir; echo $secret_key").splitlines()
		self.hostserver_port = int(res[0])
		self.hostserver_basedir = res[1]
		self.hostserver_secret_key = res[2]
		self.save();
				
	def hostserver_cleanup(self, task):
		if self.hostserver_basedir:
			self.execute("find %s -type f -mtime +0 -delete" % self.hostserver_basedir, task)
			
	def cluster_state(self):
		res = self.get_result("pveca -i 2>/dev/null | tail -n 1")
		return res.split("\n")[-2].split(" ")[-1]
				
	def next_free_vm_id (self):
		ids = range(self.vmid_range_start,self.vmid_range_start+self.vmid_range_count)
		import openvz
		for dev in openvz.OpenVZDevice.objects.filter(host=self, openvz_id__isnull=False): # pylint: disable-msg=E1101
			ids.remove(dev.openvz_id)
		import kvm
		for dev in kvm.KVMDevice.objects.filter(host=self, kvm_id__isnull=False): # pylint: disable-msg=E1101
			ids.remove(dev.kvm_id)
		try:
			return ids[0]
		except:
			raise fault.new(fault.NO_RESOURCES, "No more free VM ids on %s" + self)

	def next_free_port(self):
		ids = range(self.port_range_start,self.port_range_start+self.port_range_count)
		import openvz
		for dev in openvz.OpenVZDevice.objects.filter(host=self, vnc_port__isnull=False): # pylint: disable-msg=E1101
			ids.remove(dev.vnc_port)
		import kvm
		for dev in kvm.KVMDevice.objects.filter(host=self, vnc_port__isnull=False): # pylint: disable-msg=E1101
			ids.remove(dev.vnc_port)
		import tinc
		for con in tinc.TincConnection.objects.filter(interface__device__host=self, tinc_port__isnull=False): # pylint: disable-msg=E1101
			ids.remove(con.tinc_port)
		try:
			return ids[0]
		except:
			raise fault.new(fault.NO_RESOURCES, "No more free ports on %s" + self)

	def next_free_bridge(self):
		ids = range(self.bridge_range_start,self.bridge_range_start+self.bridge_range_count)
		import generic
		for con in generic.Connection.objects.filter(interface__device__host=self, bridge_id__isnull=False): # pylint: disable-msg=E1101
			ids.remove(con.bridge_id)
		try:
			return ids[0]
		except:
			raise fault.new(fault.NO_RESOURCES, "No more free bridge ids on %s" + self)
	
	def _exec(self, cmd):
		res = util.run_shell(cmd, config.remote_dry_run)
		#if res[0] == 255:
		#	raise fault.Fault(fault.UNKNOWN, "Failed to execute command %s on host %s: %s" % (cmd, self.name, res) )
		return res[1]
	
	def execute(self, command, task=None):
		cmd = Host.SSH_COMMAND + ["root@%s" % self.name, command]
		log_str = self.name + ": " + command + "\n"
		if task:
			fd = task.output
		else:
			fd = sys.stdout
		fd.write(log_str)
		res = self._exec(cmd)
		fd.write(res)
		return res
	
	def _calc_grant(self, params):
		list = [k+"="+v for k, v in params.iteritems() if not k == "grant"]
		list.sort()
		import hashlib
		return hashlib.sha1("&".join(list)+"|"+self.hostserver_secret_key).hexdigest()
	
	def upload_grant(self, filename, redirect):
		import urllib, base64, time
		params={"file": filename, "redirect": base64.b64encode(redirect), "valid_until": str(time.time()+3600)}
		params.update(grant=self._calc_grant(params))
		qstr = urllib.urlencode(params)
		return "http://%s:%s/upload?%s" % (self.name, self.hostserver_port, qstr)
	
	def download_grant(self, file, name):
		import time
		params={"file": file, "valid_until": str(time.time()+3600), "name": name}
		params.update(grant=self._calc_grant(params))
		import urllib
		qstr = urllib.urlencode(params)
		return "http://%s:%s/download?%s" % (self.name, self.hostserver_port, qstr)

	def upload(self, local_file, remote_file, task=None):
		cmd = Host.RSYNC_COMMAND + [local_file, "root@%s:%s" % (self.name, remote_file)]
		log_str = self.name + ": " + local_file + " -> " + remote_file  + "\n"
		self.execute("mkdir -p $(dirname %s)" % remote_file, task)
		if task:
			fd = task.output
		else:
			fd = sys.stdout
		fd.write(log_str)
		res = self._exec(cmd)
		fd.write(res)
		return res
	
	def download(self, remote_file, local_file, task=None):
		cmd = Host.RSYNC_COMMAND + ["root@%s:%s" % (self.name, remote_file), local_file]
		log_str = self.name + ": " + local_file + " <- " + remote_file  + "\n"
		if task:
			fd = task.output
		else:
			fd = sys.stdout
		fd.write(log_str)
		res = self._exec(cmd)
		fd.write(res)
		return res
	
	def get_result(self, command):
		return self._exec(Host.SSH_COMMAND+["root@%s" % self.name, command])

	def _first_line(self, line):
		if not line:
			return line
		line = line.splitlines()
		if len(line) == 0:
			return ""
		else:
			return line[0]

	def free_port(self, port, task):
		self.execute("for i in $(lsof -i:%s -t); do cat /proc/$i/status | fgrep PPid | cut -f2; done | xargs -r kill" % port, task)
		self.execute("lsof -i:%s -t | xargs -r kill" % port, task)

	def bridge_exists(self, bridge):
		if config.remote_dry_run:
			return
		return self._first_line(self.get_result("[ -d /sys/class/net/%s/brif ]; echo $?" % bridge)) == "0"

	def bridge_create(self, bridge):
		if config.remote_dry_run:
			return
		self.get_result("brctl addbr %s" % bridge)
		assert self.bridge_exists(bridge), "Bridge cannot be created: %s" % bridge
		
	def bridge_remove(self, bridge):
		if config.remote_dry_run:
			return
		self.get_result("brctl delbr %s" % bridge)
		assert not self.bridge_exists(bridge), "Bridge cannot be removed: %s" % bridge
		
	def bridge_interfaces(self, bridge):
		if config.remote_dry_run:
			return
		assert self.bridge_exists(bridge), "Bridge does not exist: %s" % bridge 
		return self.get_result("ls /sys/class/net/%s/brif" % bridge).split()
		
	def bridge_disconnect(self, bridge, iface):
		if config.remote_dry_run:
			return
		assert self.bridge_exists(bridge), "Bridge does not exist: %s" % bridge
		if not iface in self.bridge_interfaces(bridge):
			return
		self.get_result("brctl delif %s %s" % (bridge, iface))
		assert not iface in self.bridge_interfaces(bridge), "Interface %s could not be removed from bridge %s" % (iface, bridge)
		
	def bridge_connect(self, bridge, iface):
		if config.remote_dry_run:
			return
		if iface in self.bridge_interfaces(bridge):
			return
		assert self.interface_exists(iface), "Interface does not exist: %s" % iface
		if not self.bridge_exists(bridge):
			self.bridge_create(bridge)
		oldbridge = self.interface_bridge(iface)
		if oldbridge:
			self.bridge_disconnect(oldbridge, iface)
		self.get_result("brctl addif %s %s" % (bridge, iface))
		assert iface in self.bridge_interfaces(bridge), "Interface %s could not be connected to bridge %s" % (iface, bridge)
		
	def interface_bridge(self, iface):
		if config.remote_dry_run:
			return
		return self._first_line(self.get_result("[ -d /sys/class/net/%s/brport/bridge ] && basename $(readlink /sys/class/net/%s/brport/bridge)" % (iface, iface)))
			
	def interface_exists(self, iface):
		if config.remote_dry_run:
			return
		return self._first_line(self.get_result("[ -d /sys/class/net/%s ]; echo $?" % iface)) == "0"

	def debug_info(self):		
		result={}
		result["top"] = self.get_result("top -b -n 1")
		result["OpenVZ"] = self.get_result("vzlist -a")
		result["KVM"] = self.get_result("qm list")
		result["Bridges"] = self.get_result("brctl show")
		result["iptables router"] = self.get_result("iptables -t mangle -v -L PREROUTING")		
		result["ipfw rules"] = self.get_result("ipfw show")
		result["ipfw pipes"] = self.get_result("ipfw pipe show")
		result["ifconfig"] = self.get_result("ifconfig -a")
		result["netstat"] = self.get_result("netstat -tulpen")		
		result["df"] = self.get_result("df -h")		
		result["templates"] = self.get_result("ls -lh /var/lib/vz/template/*")		
		result["hostserver"] = self.get_result("/etc/init.d/tomato-hostserver status")		
		result["hostserver-files"] = self.get_result("ls -l /var/lib/vz/hostserver")		
		return result
	
	def special_features(self):
		return self.specialfeature_set.all() # pylint: disable-msg=E1101
	
	def special_features_add(self, feature_type, group_name, bridge):
		sfg = SpecialFeatureGroup.objects.get(feature_type=feature_type, group_name=group_name)
		sf = SpecialFeature(host=self, feature_group=sfg, bridge=bridge)
		sf.save()
		self.specialfeature_set.add(sf) # pylint: disable-msg=E1101
		
	def special_features_remove(self, feature_type, group_name):
		sfg = SpecialFeatureGroup.objects.get(feature_type=feature_type, group_name=group_name)
		for sf in self.special_features():
			if sf.feature_group == sfg:
				sf.delete()
	
	def to_dict(self):
		"""
		Prepares a host for serialization.
		
		@return: a dict containing information about the host
		@rtype: dict
		"""
		return {"name": self.name, "group": self.group, "enabled": self.enabled, 
			"device_count": self.device_set.count(), # pylint: disable-msg=E1101
			"vmid_start": self.vmid_range_start, "vmid_count": self.vmid_range_count,
			"port_start": self.port_range_start, "port_count": self.port_range_count,
			"bridge_start": self.bridge_range_start, "bridge_count": self.bridge_range_count,
			"special_features": [sf.to_dict() for sf in self.special_features()]}

	
class Template(models.Model):
	name = models.CharField(max_length=100)
	type = models.CharField(max_length=12)
	default = models.BooleanField(default=False)
	download_url = models.CharField(max_length=255, default="")
		
	def init(self, name, ttype, download_url):
		self.name = name
		self.type = ttype
		self.download_url = download_url
		self.save()

	def set_default(self):
		Template.objects.filter(type=self.type).update(default=False) # pylint: disable-msg=E1101
		self.default=True
		self.save()
		
	def get_filename(self):
		if self.type == "kvm":
			return "/var/lib/vz/template/qemu/%s" % self.name
		if self.type == "openvz":
			return "/var/lib/vz/template/cache/%s.tar.gz" % self.name
	
	def upload_to_all(self, task):
		for host in Host.objects.all(): # pylint: disable-msg=E1101
			self.upload_to_host(host, task)
		
	def upload_to_host(self, host, task):
		if host.cluster_state() == ClusterState.NODE:
			return
		dst = self.get_filename()
		if self.download_url:
			host.execute("wget -nv %s -O %s" % (self.download_url, dst), task)

	def __unicode__(self):
		return "Template(type=%s,name=%s,default=%s)" %(self.type, self.name, self.default)
			
	def to_dict(self):
		"""
		Prepares a template for serialization.
			
		@return: a dict containing information about the template
		@rtype: dict
		"""
		return {"name": self.name, "type": self.type, "default": self.default, "url": self.download_url}

			
class PhysicalLink(models.Model):
	src_group = models.CharField(max_length=10)
	dst_group = models.CharField(max_length=10)
	loss = models.FloatField()
	delay_avg = models.FloatField()
	delay_stddev = models.FloatField()
			
	sliding_factor = 0.25
			
	def adapt(self, loss, delay_avg, delay_stddev):
		self.loss = ( 1.0 - self.sliding_factor ) * self.loss + self.sliding_factor * loss
		self.delay_avg = ( 1.0 - self.sliding_factor ) * self.delay_avg + self.sliding_factor * delay_avg
		self.delay_stddev = ( 1.0 - self.sliding_factor ) * self.delay_stddev + self.sliding_factor * delay_stddev
		self.save()
	
	def to_dict(self):
		"""
		Prepares a physical link object for serialization.
		
		@return: a dict containing information about the physical link
		@rtype: dict
		"""
		return {"src": self.src_group, "dst": self.dst_group, "loss": self.loss,
			"delay_avg": self.delay_avg, "delay_stddev": self.delay_stddev}
	

class SpecialFeatureGroup(models.Model):
	feature_type = models.CharField(max_length=50)
	group_name = models.CharField(max_length=50)
	max_devices = models.IntegerField(null=True)
	avoid_duplicates = models.BooleanField(default=False)

	def has_free_slots(self):
		return not (self.max_devices and self.usage_count() >= self.max_devices) 

	def usage_count(self):
		import special
		connectors = special.SpecialFeatureConnector.objects.filter(used_feature_group=self)
		num = connectors.annotate(num_connections=models.Count('connection')).aggregate(Sum('num_connections'))["num_connections__sum"]
		return num if num else 0
		
	def to_dict(self, instances=False):
		"""
		Prepares a special feature group for serialization.
		
		@return: a dict containing information about the special feature group
		@rtype: dict
		"""
		data = {"type": self.feature_type, "name": self.group_name, "max_devices": (self.max_devices if self.max_devices else False), "avoid_duplicates": self.avoid_duplicates}
		if instances:
			data["instances"] = [sf.to_dict() for sf in self.specialfeature_set.all()]
		return data

	
class SpecialFeature(models.Model):
	host = models.ForeignKey(Host)
	feature_group = models.ForeignKey(SpecialFeatureGroup)
	bridge = models.CharField(max_length=10)

	def to_dict(self):
		"""
		Prepares a special feature for serialization.
		
		@return: a dict containing information about the special feature
		@rtype: dict
		"""
		return {"host": self.host.name, "type": self.feature_group.feature_type, "group": self.feature_group.group_name, "bridge": self.bridge}

	
def get_host_groups():
	groups = []
	for h in Host.objects.all(): # pylint: disable-msg=E1101
		if not h.group in groups:
			groups.append(h.group)
	return groups
	
def get_host(name):
	return Host.objects.get(name=name) # pylint: disable-msg=E1101

def get_hosts(group=None):
	hosts = Host.objects.all()
	if group:
		hosts = hosts.filter(group=group)
	return hosts

def get_best_host(group):
	all_hosts = Host.objects.filter(enabled=True) # pylint: disable-msg=E1101
	if group:
		all_hosts = all_hosts.filter(group=group)
	hosts = all_hosts.annotate(num_devices=models.Count('device')).order_by('num_devices', '?')
	if len(hosts) > 0:
		return hosts[0]
	else:
		raise fault.new(fault.NO_HOSTS_AVAILABLE, "No hosts available")

def get_templates(ttype=None):
	tpls = Template.objects.all() # pylint: disable-msg=E1101
	if ttype:
		tpls = tpls.filter(type=ttype)
	return tpls

def get_template_name(ttype, name):
	try:
		return Template.objects.get(type=ttype, name=name).name # pylint: disable-msg=E1101
	except: #pylint: disable-msg=W0702
		return get_default_template(ttype)

def get_template(ttype, name):
	return Template.objects.get(type=ttype, name=name) # pylint: disable-msg=E1101

def add_template(name, template_type, url):
	tpl = Template.objects.create(name=name, type=template_type, download_url=url) # pylint: disable-msg=E1101
	import tasks
	t = tasks.TaskStatus(tpl.upload_to_all)
	t.subtasks_total = 1
	t.start()
	return t.id
	
def remove_template(name):
	Template.objects.filter(name=name).delete() # pylint: disable-msg=E1101
	
def get_default_template(ttype):
	tpls = Template.objects.filter(type=ttype, default=True) # pylint: disable-msg=E1101
	if tpls.count() >= 1:
		return tpls[0].name
	else:
		return None
	
def create(host_name, group_name, enabled, vmid_start, vmid_count, port_start, port_count, bridge_start, bridge_count):
	host = Host(name=host_name, enabled=enabled, group=group_name,
			vmid_range_start=vmid_start, vmid_range_count=vmid_count,
			port_range_start=port_start, port_range_count=port_count,
			bridge_range_start=bridge_start, bridge_range_count=bridge_count)
	import tasks
	t = tasks.TaskStatus(host.check_save)
	t.subtasks_total = 1
	t.start()
	return t.id

def change(host_name, group_name, enabled, vmid_start, vmid_count, port_start, port_count, bridge_start, bridge_count):
	host = get_host(host_name)
	host.enabled=enabled
	host.group=group_name
	host.vmid_range_start=vmid_start
	host.vmid_range_count=vmid_count
	host.port_range_start=port_start
	host.port_range_count=port_count
	host.bridge_range_start=bridge_start
	host.bridge_range_count=bridge_count
	host.save()
	
def remove(host_name):
	host = get_host(host_name)
	assert len(host.device_set.all()) == 0, "Cannot remove hosts that are used"
	host.delete()
		
def get_physical_link(srcg_name, dstg_name):
	return PhysicalLink.objects.get(src_group = srcg_name, dst_group = dstg_name) # pylint: disable-msg=E1101		
		
def get_all_physical_links():
	return PhysicalLink.objects.all() # pylint: disable-msg=E1101		
		
def measure_link_properties(src, dst):
	res = src.get_result("ping -A -c 500 -n -q -w 300 %s" % dst.name)
	if not res:
		return
	lines = res.splitlines()
	loss = float(lines[3].split()[5][:-1])/100.0
	import math
	loss = 1.0 - math.sqrt(1.0 - loss)
	times = lines[4].split()[3].split("/")
	unit = lines[4].split()[4][:-1]
	avg = float(times[1]) / 2.0
	stddev = float(times[3]) / 2.0
	if unit == "s":
		avg = avg * 1000.0
		stddev = stddev * 1000.0
	return (loss, avg, stddev)
				
def measure_physical_links():
	if config.remote_dry_run:
		return
	for srcg in get_host_groups():
		for dstg in get_host_groups():
			if not srcg == dstg:
				try:
					src = get_best_host(srcg)
					dst = get_best_host(dstg)
					(loss, delay_avg, delay_stddev) = measure_link_properties(src, dst)
					link = get_physical_link(srcg, dstg)
					link.adapt(loss, delay_avg, delay_stddev) 
				except PhysicalLink.DoesNotExist: # pylint: disable-msg=E1101
					PhysicalLink.objects.create(src_group=srcg, dst_group=dstg, loss=loss, delay_avg=delay_avg, delay_stddev=delay_stddev) # pylint: disable-msg=E1101
				except fault.Fault:
					pass

def check_all_hosts():
	if config.remote_dry_run:
		return
	import tasks
	task = tasks.TaskStatus(None)
	for host in get_hosts():
		try:
			if host.enabled:
				host.check(task)
		except:
			host.enabled = False
			host.save()
	task.done()

if not config.TESTING:				
	measurement_task = util.RepeatedTimer(3600, measure_physical_links)
	measurement_task.start()
	host_check_task = util.RepeatedTimer(3600*6, check_all_hosts)
	host_check_task.start()
	atexit.register(measurement_task.stop)
	atexit.register(host_check_task.stop)

def host_check(host):
	import tasks
	t = tasks.TaskStatus(host.check)
	t.subtasks_total = 7
	t.start()
	return t.id

def special_features():
	return [sfg.to_dict(True) for sfg in SpecialFeatureGroup.objects.all()]