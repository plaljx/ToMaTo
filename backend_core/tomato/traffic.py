from .db import *


class Traffic(BaseDocument):

	element_id = StringField(required=True)
	traffic_name = StringField(required=True,unique=True)
	flow_number = IntField(default=1)#@unresolved
	start_time = StringField(default='0')#@unresolved
	off_time = StringField()
	dest_ip = StringField()
	dest_port = StringField()
	protocol = StringField()
	pattern = StringField()
	tos = StringField(default='0') #@unresolved

	def init(self,element_id, **attrs):
		self.element_id = element_id
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
			"traffic_name":self.traffic_name,
			"off_time":self.off_time,
			"dest_ip":self.dest_ip,
			"dest_port":self.dest_port,
			"protocol":self.protocol,
			"pattern":self.pattern,
		}

	def remove(self):
		self.delete()

	def modify_element_id(self, val):
		self.element_id = val

	def modify_traffic_name(self, val):
		self.traffic_name = val

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

def get(id_, **kwargs):
	try:
		res = Traffic.objects.get(id = id_, **kwargs)
		return res
	except Exception, e:
		raise e

def getAll(**kwargs):
	return list(Traffic.objects.filter(**kwargs))

def create(element_id, **attrs):
	res = Traffic()
	print attrs
	try:
		res.init(element_id, **attrs)
	except Exception, e:
		if res.id.__str__():
			try:
				res.remove()
			except:
				pass
		raise e
	return res