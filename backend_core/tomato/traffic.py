import re
from .db import *
from .lib import traffic
from .elements import Element

action = "rextfv_upload_grant"
action_use = "rextfv_upload_use"

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
	packet_rate = StringField()
	packet_size = StringField()
	tos = StringField() #@unresolved
	ttl = StringField()
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
		result = {
			"id":self.id.__str__(),
			"source_element":self.source_element.__str__(),
			"dest_element":self.dest_element.__str__(),
			"traffic_name": self.traffic_name,
			"source_ip":self.source_ip,
			"source_port":self.source_port,
			"dest_ip": self.dest_ip,
			"dest_port": self.dest_port,
			"start_time":self.start_time,
			"off_time":self.off_time,
			"protocol":self.protocol,
			"pattern":self.pattern,
			"packet_size":self.packet_size,
			"packet_rate":self.packet_rate,
			"tos": self.tos,
			"ttl": self.ttl,
			"file": self.file
		}
		print result
		return result

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

	def modify_packet_size(self, val):
		self.packet_size = val

	def modify_packet_rate(self, val):
		self.packet_rate = val

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

'''
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
'''

def get_usages(element_ids):
	usages = {}
	useage_ratio = {}
	print_ratio = {}
	for id in element_ids:
		temp = Element.getUsage(id)
		usages[id] = temp
		cpu = 100 * float(temp["cpu"])
		memory = (100 * float(temp["memory"])) /(1024*1024*float(temp["ram"]))
		traffic = (100 * float(temp["traffic"])) / (60 * 10000 )
		#if one of the metrics >= 80 ,ignore it
		if cpu <= 80 and memory <= 80 and traffic <= 80:
			useage_ratio[id] = {"cpu": cpu, "memory": memory,"traffic": traffic}
		print_ratio[id] = {"cpu": cpu, "memory": memory,"traffic": traffic}
	print usages
	print useage_ratio
	print "虚拟机资源使用情况:"
	print "虚拟机编号\t\tCPU使用率(%)\t内存使用率(%)\t带宽使用率(%)"
	for key in print_ratio:
		print key,"\t\t",print_ratio[key][cpu],"\t",print_ratio[key][memory],"\t",print_ratio[key][traffic]
	for key in print_ratio:

	return useage_ratio

def calculate_load(usages, a=0.4, b=0.3, c=0.3):
	load = {}
	for  key in usages:
		load[key] = usages[key]["cpu"] * 0.4 + usages[key]["memory"] * 0.3 + usages[key]["traffic"]
	print "虚拟机负载计算"
	print "虚拟机编号\t\t虚拟机负载"
	for key in load:
		print key,"\t\t",load[key]
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
	print number, len(load)
	while i < number and i < len(load):
		result.append(load[i][0])
		i = i + 1
		print i
	print "result:"
	print result
	return result

def test_usages():
	elementids = ["5a436a89a67da503ac2df973", "5a436a90a67da503ac2df977","5a436a8ca67da503ac2df975", "5a436a8ba67da503ac2df974", "5a436a8ea67da503ac2df976"]
	result = choose_vms(elementids, 4)
	return result

def traffic_start(traffic_id):
	traffic_info = get(traffic_id).info()

	tool = choose_tool(traffic_info)
	source_command = get_source_command(tool, traffic_info)
	dest_command = get_dest_command(tool, traffic_info)

	source_dir = traffic.make_command_file(traffic_info["source_element"], source_command)
	dest_dir = traffic.make_command_file(traffic_info["dest_element"], dest_command)

	#send destination vm's command file
	if dest_dir is not None:
		dest_element = Element.get(traffic_info["dest_element"])
		key = dest_element.action(action)
		traffic.send_file(dest_element.info() ,dest_dir, key)
		dest_element.action(action_use)

	#send source vm's command file
	if source_dir is not None:
		source_element = Element.get(traffic_info["source_element"])
		key = source_element.action(action)
		traffic.send_file(source_element.info() ,source_dir, key)
		source_element.action(action_use)
	return None

def choose_tool(traffic_info):
	definition = traffic.get_traffic_modul()
	candidates = {}
	attributes = definition["attributes"]
	print attributes
	tools = definition['tools']
	#traverse all the tools
	for tool in tools:
		#travese all the attributes
		cap = definition[tool]
		print "cap:", cap
		result = True
		for attribute in attributes:
			if traffic_info.has_key(attribute):
				if traffic_info[attribute] != "" :
					if not cap.has_key(attribute):
						print "not have attribute:",attribute
						result = False
						break
					else:
						if len(cap[attribute]) >2:
							if traffic_info[attribute] not in cap[attribute]:
								print "not in attribute:", cap[attribute], attribute
								result = False
								break
				else:
					if cap.has_key(attribute):
						if cap[attribute][1] is True:
							print "is required", attribute
							result = False
							break
			else:
				if cap.has_key(attribute):
					if cap[attribute][1] is True:
						print "is required2:",attribute
						result = False
						break
		#if the tool satisfies all the conditions ,add it to candidates
		if result is True:
			candidates[tool] = definition[tool]["priority"]
	#select the tool by priority
	print "candidates:",candidates
	if candidates:
		print "candidates",candidates
		tool = ""
		temp = 0
		for key in candidates:
			if candidates[key] > temp:
				tool = key
				temp = candidates[key]
		print "final tool:",tool
		return tool
	else:
		return None

def get_source_command(tool, traffic_info):
	command = traffic.get_traffic_modul()[tool]["command"]
	print "source_command:",command
	if traffic.get_traffic_modul()[tool].has_key("expressions"):
		for ex in traffic.get_traffic_modul()[tool]["expressions"]:
			print ex
			if int(ex[1]) ==  3:
				temp = int(int(ex[2]) * float(traffic_info[ex[3]]))
				traffic_info[ex[0]] = str(temp)
	print "traffic_info:", traffic_info
	if command.has_key("source"):
		return make_command("source", command,traffic_info)
	else:
		return None

def get_dest_command(tool, traffic_info):
	command = traffic.get_traffic_modul()[tool]["command"]
	print "dest_command:",command
	if command.has_key("dest"):
		return make_command("dest", command,traffic_info)
	else:
		return None

def make_command(target, command, traffic_info):
	formula1 = re.compile('\?.*?\?')
	formula2 = re.compile('\+.*?\+')
	com = command[target]
	add = formula1.findall(com)
	print add
	command_process = {}
	i = 1
	command_process[i] = com
	while add:
		for value in add:
			attribute = value[1:len(value)-1]
			if command.has_key(attribute):
				replacestr = ""
				if not isinstance(command[attribute], basestring):
					print command[attribute]
					print traffic_info[attribute]
					replacestr = command[attribute][traffic_info[attribute]]
				else:
					replacestr = command[attribute]
				if traffic_info.has_key(attribute):
					print "replace:",type(value),value, type(replacestr),replacestr
					com = com.replace(value, replacestr)
				else:
					com = com.replace(value, "")
				print com
		print com
		command_process[i] = com
		i = i + 1
		add = formula1.findall(com)
	add2 = formula2.findall(com)
	for value in add2:
		attribute = value[1:len(value)-1]
		print attribute, traffic_info[attribute]
		com = com.replace(value, traffic_info[attribute])
	command_process[i] = com
	print "控制命令求解过程："
	for key in command_process:
		print "第",key,"步：",command_process[key]
	print "final_command:", com
	return com


def mutil_traffic_start(elements, attrs):
	print "elements:",elements
	print "attrs:",attrs
	number = int(attrs["number"])
	#remove the destination element
	elements.remove(attrs["dest_element"])
	vms = choose_vms(elements, number)
	print "choose vms:",vms
	tool = choose_tool(attrs)
	print "tool:",tool

	source_command = get_source_command(tool, attrs)
	dest_command = get_dest_command(tool, attrs)

	#start traffics
	for source in vms:
		source_dir = traffic.make_command_file(source, source_command)
		dest_dir = traffic.make_command_file(attrs["dest_element"], dest_command)

		# send destination vm's command file
		if dest_dir is not None:
			dest_element = Element.get(attrs["dest_element"])
			key = dest_element.action(action)
			traffic.send_file(dest_element.info(), dest_dir, key)
			dest_element.action(action_use)

		# send source vm's command file
		if source_dir is not None:
			source_element = Element.get(source)
			key = source_element.action(action)
			traffic.send_file(source_element.info(), source_dir, key)
			source_element.action(action_use)
	return None










