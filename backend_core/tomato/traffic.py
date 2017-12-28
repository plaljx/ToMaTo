from .db import *
from .lib import traffic
from .elements import Element


class Traffic(BaseDocument):

	topology_id = StringField(required=True)
	source_element = StringField()
	dest_element = StringField()
	traffic_name = StringField(required=True)
	start_time = StringField()#@unresolved
	off_time = StringField()
	source_ip = StringField()
	source_port = StringField()
	dest_ip = StringField()
	dest_port = StringField()
	protocol = StringField()
	pattern = StringField()
	packet_rate = FloatField()
	packet_size = FloatField()
	tos = StringField() #@unresolved
	ttl = IntField()
	file = StringField()

	def init(self,topology_id, **attrs):
		self.topology_id = topology_id
		self.modify(**attrs)
		self.save()

	def modify(self, **attrs):
		for key in attrs:
			if hasattr(self, "modify_%s" % key):
				getattr(self, "modify_%s" % key)(attrs[key])
			else:
				print "Wrong attribute %s" % key
		self.save()
		return self.info()

	def info(self):
		return {
			"id":self.id.__str__(),
			"source_element":self.source_element,
			"dest_element":self.dest_element,
			"traffic_name": self.traffic_name,
			"source_ip":self.source_ip,
			"source_port":self.source_port,
			"dest_ip": self.dest_ip,
			"dest_port": self.dest_port,
			"start_time":self.start_time,
			"off_time":self.off_time,
			"protocol":self.protocol,
			"pattern":self.pattern,
			"tos": self.tos,
			"ttl": self.ttl,
			"file": self.file
		}

	def remove(self):
		self.delete()

	def modify_source_element(self, val):
		self.source_element = val

	def modify_dest_element(self, val):
		self.dest_element = val

	def modify_traffic_name(self, val):
		self.traffic_name = val

	def modify_source_ip(self, val):
		self.source_ip = val

	def modify_source_port(self, val):
		self.source_port = val

	def modify_start_time(self, val):
		self.start_time = val

	def modify_off_time(self, val):
		self.off_time = val

	def modify_dest_ip(self, val):
		self.dest_ip = val

	def modify_dest_port(self, val):
		self.dest_port = val

	def modify_protocol(self, val):
		self.protocol = val

	def modify_pattern(self, val):
		self.pattern = val

	def modify_tos(self, val):
		self.tos = val

	def modify_ttl(self, val):
		self.ttl = val

	def modify_file(self, val):
		self.file = val

def get(id_, **kwargs):
	try:
		res = Traffic.objects.get(id = id_, **kwargs)
		return res
	except Exception, e:
		raise e

def getAll(**kwargs):
	return list(Traffic.objects.filter(**kwargs))

def create(topology_id, **attrs):
	res = Traffic()
	print attrs
	try:
		res.init(topology_id, **attrs)
	except Exception, e:
		if res.id.__str__():
			try:
				res.remove()
			except:
				pass
		raise e
	return res

def ditg_start(element_id , **attrs):
	print attrs
	if attrs["dns_enable"] == True and attrs["telnet_enable"] == True:
		return None
	kind = ""
	if attrs["dns_enable"] == True:
		kind = "dns"
	elif attrs["telnet_enable"] == True:
		kind = "telnet"
	else:
		kind = ""

	action = "rextfv_upload_grant"
	action_use = "rextfv_upload_use"
	#launch ditg receiver
	receiver_element = Element.get(attrs["target_id"]).info()
	receiver_key = Element.get(attrs["target_id"]).action(action)
	receiver_dir = traffic.make_ditg_pack("receive",attrs["target_id"],kind,**attrs)
	upload = traffic.send_pack(receiver_element, receiver_dir, receiver_key)
	res = Element.get(attrs["target_id"]).action(action_use)

	#launch ditg sender
	sender_element = Element.get(element_id)
	sender_key = sender_element.action(action)
	print sender_key
	sender_dir = traffic.make_ditg_pack("send", element_id , kind,**attrs)
	print sender_dir
	upload = traffic.send_pack(sender_element.info(), sender_dir, sender_key)
	res = sender_element.action(action_use)
	return res

def get_usages(element_ids):
	usages = {}
	useage_ratio = {}
	for id in element_ids:
		temp = Element.getUsage(id)
		usages[id] = temp
		cpu = 100 * float(temp["cpu"])
		memory = (100 * float(temp["memory"])) /(1024*1024*float(temp["ram"]))
		traffic = (100 * float(temp["traffic"])) / (60 * 10000 )
		useage_ratio[id] = {"cpu": cpu, "memory": memory,"traffic": traffic}
	print usages
	print useage_ratio
	return useage_ratio

def calculate_load(usages, a=0.4, b=0.3, c=0.3):
	load = {}
	for  key in usages:
		load[key] = usages[key]["cpu"] * 0.4 + usages[key]["memory"] * 0.3 + usages[key]["traffic"]
	return load

def choose_vms(elemet_ids, number):
	usages = get_usages(elemet_ids)
	load = calculate_load(usages)
	#sort
	load = sorted(load.iteritems(), key=lambda d: d[1], reverse=False)
	print "load:"
	print load
	i = 0
	result  = []
	while i < number and i < len(load):
		result.append(load[i][0])
		i = i + 1
	print "result:"
	print result
	return result

def test_usages():
	elementids = ["5a436a89a67da503ac2df973", "5a436a90a67da503ac2df977","5a436a8ca67da503ac2df975", "5a436a8ba67da503ac2df974", "5a436a8ea67da503ac2df976"]
	result = choose_vms(elementids, 4)
	return result

def traffic_start(traffic_id):
	action = "rextfv_upload_grant"
	action_use = "rextfv_upload_use"
	traffic_info = get(traffic_id).info()

	tool = choose_tool(traffic_info)
	source_command = get_source_command(tool, traffic_info)
	dest_command = get_dest_command(tool, traffic_info)

	source_dir = traffic.make_command_file(traffic_info, tool, source_command)
	dest_dir = traffic.make_command_file(traffic_info, tool, dest_command)

	#upload  dest
	if dest_dir is not None:
		dest_element = Element.get(traffic_info["dest_element"])
		key = dest_element.action(action)
		traffic.send_pack(dest_element.info() ,dest_dir, key)
		dest_element.action(action_use)

	#upload source
	if source_dir is not None:
		source_element = Element.get(traffic_info["source_element"])
		key = source_element.action(action)
		traffic.send_pack(source_element.info() ,dest_dir, key)
		source_element.action(action_use)
	return None

def choose_tool(traffic_info):
	#todo匹配选择流量生成工具
	return None

def get_source_command(tool, traffic_info):
	#todo创建源主机控制命令
	return None

def get_dest_command(tool, traffic_info):
	#todo创建目标主机控制命令
	return None





