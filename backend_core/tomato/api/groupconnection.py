from ..groupconnection import Groupconnection
from elements import _getElement

def groupconnection_create(el1, el2, data=None): #@ReservedAssignment
	if not data: data = {}
	el1 = _getElement(el1)
	el2 = _getElement(el2)
	con = Groupconnection.create(el1, el2)
	# return con.info()
	return 'assert'

