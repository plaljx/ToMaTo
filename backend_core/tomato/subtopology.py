from db import *
from .topology import Topology

class Subtopology(BaseDocument):
	topology = ReferenceField('Topology', db_field = 'topology')
	topologyId = ReferenceFieldId(topology)
	subtopologyList = ListField(required = True)
	# subtopologyNum = IntFiled(required = True)

	@classmethod
	def create(cls , top_id = None, **data):
		subtopology = cls()
		subtopology.topology = Topology.objects.get(id = top_id)
		subtopology.subtopologyList = []
		subtopology.subtopologyList.append('main')
		# subtopology.subtopologyNum = 1
		subtopology.save()
		return subtopology.subtopologyList

	def add(self, **data):
		self.subtopologyList.append(data['name'])
		self.save()
		# subtopology.subtopologyNum = subtopologyNum + 1
		return self.subtopologyList
	
	def get_list(self, top_id = None, **data):
		return self.subtopologyList

	def remove(self, top_id = None, **data):
		# topology = Topology.objects.get(id = top_id)
		subtopology = Subtopology.objects.get(topologyId = top_id)
		subtopology.subtopologyList.remove(data['name'])
		subtopology.save()
		return 'remove success'

	@classmethod
	def check(cls, top_id = None, **data):
		topology = Topology.objects.get(id = top_id)
		subtopology = Subtopology.objects.get(topology = topology)
		return True if len(subtopology.subtopologyList) else False

	@classmethod
	def get(cls, top_id = None, **data):
		topology = Topology.objects.get(id = top_id)
		subtopology = Subtopology.objects.get(topology = topology)
		return subtopology