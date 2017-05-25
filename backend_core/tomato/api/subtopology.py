from ..subtopology import Subtopology

def subtopology_add(top_id, **data):
 	# if Subtopology.check(top_id):
 	# 	subtopology = Subtopology.get(top_id, **data)
 	# 	subtopology.add(**data)
 	# else:
 	# 	Subtopology.create(top_id, **data)
 	subtopology = Subtopology.get(top_id, **data)
 	res = subtopology.add(**data)
 	return res
 	# return 


# def subtopology_getList(top_id, **data):
# 	if 

def subtopology_get(top_id, **data):
	subtopology = Subtopology.get(top_id, **data)
	res = subtopology.get_list(**data)
	return res


def subtopology_init(top_id, **data):
	res = Subtopology.create(top_id)
	return res


