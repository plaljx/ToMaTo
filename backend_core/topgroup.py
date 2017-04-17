from db import *
import time


class Topgroup(BaseDocument):
	tops = ListField()
	create_time = DateField()
	name = StringField(unique = True)


	@classmethod
	def create(cls ,name):
		group = Topgroup()
		group.name = name
		group.create_time = time.time()
		group.save()

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
		'create_time':self.create_time
		}
