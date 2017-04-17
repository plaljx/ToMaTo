from db import *
import datetime


class Topgroup(BaseDocument):
	main_top = StringField()
	tops = ListField()
	create_time = DateTimeField()
	name = StringField(unique = True)


	@classmethod
	def create(cls , top_id = None, **data):
		group = Topgroup()
		group.name = data['name']
		group.create_time = datetime.datetime.now()
		group.main_top = top_id
		group.tops.append(top_id)
		group.save()
		return group

	def add(self, id):
		self.tops.append(id)
		self.save()

	@classmethod
	def get(cls, name):
		topgroup = cls.objects.get(name = name)
		return topgroup

	def remove_top(self, id):
		self.tops.remove(id)
		self.save()

	@classmethod
	def remove(cls, name):
		topgroup = cls.get(name)
		topgroup.delete()

	def info(self):
		return {
		'tops': self.tops,
		'name': self.name,
		# 'create_time':self.create_time
		}
	
	@classmethod
	def count(cls, name):
		topgroup = cls.objects.get(name = name)
		return len(topgroup.tops)

	@classmethod
	def list(cls):
		return list(cls.objects.all())

	@property
	def topology(self):
		# return a list made by topgroup's topology info
		topology_list = []
		for topology_id in self.tops:
			topology_list.append(Topology.objects.get(idStr = topology_id).info())
		return topology_list


from .topology import Topology