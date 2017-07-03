from db import *
import datetime
from .host import Host


class Topgroup(BaseDocument):
	# main_top = StringField() remove main_top
	tops = ListField()
	create_time = DateTimeField()
	name = StringField(unique = True)


	@property
	def topology(self):
		return topology.Topology.objects(topgroup = self)

	@property
	def groupconnection(self):
		return groupconnection.Groupconnetion.object(topgroup = self)

	@classmethod
	def create(cls , top_id = None, **data):
		group = Topgroup()
		group.name = data['name']
		group.create_time = datetime.datetime.now()
		group.save()
		return group

	def add(self, top_id, name):
		self.tops.append(top_id)
		top = topology.Topology.objects.get(id = top_id)
		top.topgroup = self
		top.save()
		self.save()

	@classmethod
	def get(cls, name):
		topgroup = cls.objects.get(name = name)
		return topgroup

	@classmethod
	def get_bytop(cls, top_id = None, **data):
		topgroup = topology.Topology.objects.get(id = top_id).topgroup
		# topgroup = cls.objects.get(name = topgroup_name)
		return topgroup

	# todo change logic
	def remove_top(self, id):
		self.tops.remove(id)
		self.save()

	@classmethod
	def remove(cls, name):
		topgroup = cls.get(name)
		topgroup.delete()

	def info(self):
		tops = self.topology
		tops_info = [top.info() for top in tops]
		
		# tops_info = {top.name:{el.name: el.info() for el in top.elements}for top in tops}
		# # tops_info[top.name]['id'] = 
		# for top in tops:
		# 	tops_info[top.name]['id'] = top.idStr
		return {
		'tops': self.tops,
		'name': self.name,
		'info': tops_info,
		}
	
	@classmethod
	def count(cls, name):
		topgroup = cls.objects.get(name = name)
		return len(topgroup.tops)

	@classmethod
	def list(cls,top_id = None,  **data):
		return [topgroup.name for topgroup in list(cls.objects.all())]


import topology
import groupconnection