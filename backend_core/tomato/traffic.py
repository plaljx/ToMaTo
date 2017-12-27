from .db import *
from .lib import traffic
from .elements import Element


class Traffic(BaseDocument):

	topology_id = StringField(required=True)
	element_id =  StringField(required=True)
	traffic_name = StringField(required=True)
	flow_number = IntField(default=1)#@unresolved
	start_time = StringField(default='0')#@unresolved
	off_time = StringField()
	source_ip = StringField()
	src_port = StringField()
	dest_ip = StringField()
	dest_port = StringField()
	protocol = StringField()
	pattern = StringField()
	tos = StringField(default='0') #@unresolved
	extra_param = StringField()

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
			"element_id":self.element_id,
			"topology_id":self.topology_id,
			"source_ip":self.source_ip,
			"src_port":self.src_port,
			"tos":self.tos,
			"start_time":self.start_time,
			"traffic_name":self.traffic_name,
			"off_time":self.off_time,
			"dest_ip":self.dest_ip,
			"dest_port":self.dest_port,
			"protocol":self.protocol,
			"pattern":self.pattern,
			"extra_param":self.extra_param,
		}

	def remove(self):
		self.delete()

	def modify_extra_param(self, val):
		self.extra_param = val

	def modify_element_id(self, val):
		self.element_id = val

	def modify_traffic_name(self, val):
		self.traffic_name = val

	def modify_src_port(self, val):
		self.src_port = val

	def modify_flow_number(self, val):
		self.flow_number = val

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

	def modify_element_id(self, val):
		self.element_id = val

	def modify_source_ip(self, val):
		self.source_ip = val

	@classmethod
	def traffic_start(cls, traffic_id):
		action = "rextfv_upload_grant"
		action_use = "rextfv_upload_use"
		traffic_info = get(traffic_id).info()

		element_id = traffic_info["element_id"]
		pack_dir = traffic.make_mgen_pack(traffic_info)
		element_info = Element.get(element_id).info()
		key = Element.get(element_id).action(action)
		upload = traffic.send_pack(element_info ,pack_dir, key)
		action = Element.get(element_id).action(action_use)
		return action


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
	usages = dict()
	useage_ratio = dict()
	for id in element_ids:
		temp = Element.getUsage(id)
		usages[id] = temp
		useage_ratio[id] = {
			"cpu" :100 * float(temp["cpu"]),
			"memory" : 100 * float(temp["memory"]) /(1024*1024*temp("ram")),
			"traffic" : 100 * float(temp["traffic"]) / (60 * 10000 )
		}
	print usages
	print useage_ratio
	return useage_ratio

def calculate_load(usages, a=0.4, b=0.3, c=0.3):
	load = dict()
	for  key in usages:
		load[key] = usages[key]["cpu"] * 0.4 + usages[key]["memory"] * 0.3 + usages[key]["traffic"]
	return load

def choose_vms(elemet_ids, number):
	usages = get_usages(elemet_ids)
	load = calculate_load(usages)
	#sort
	load = sorted(load.iteritems(), key=lambda d: d[1], reverse=False)
	print "load:"+load
	i = 0
	result  = list()
	while i < number and i < len(load):
		result.append(load[i][0])
	print "result:"+result
	return result

def test_usages():
	elementids = ["5a436a89a67da503ac2df973", "5a436a90a67da503ac2df977","5a436a8ca67da503ac2df975", "5a436a8ba67da503ac2df974", "5a436a8ea67da503ac2df976"]
	choose_vms(elementids, 4)
	return None



