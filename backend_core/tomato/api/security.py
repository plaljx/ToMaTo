from ..resources.security import Security
from ..lib.error import UserError
from ..lib.exceptionhandling import wrap_errors

@wrap_errors(errorcls_func=lambda e: UserError, errorcode=UserError.ENTITY_DOES_NOT_EXIST)
def _getSecurity(id_):
	res = Security.objects.get(id=id_)
	UserError.check(res, code=UserError.ENTITY_DOES_NOT_EXIST, message="Security does not exist", data={"id": id_})
	return res



def security_list(tech=None):
	"""
	Retrieves information about all resources.

	Parameter *tech*:
	  If *tech* is set, only resources with a matching tech will be returned.

	Return value:
	  A list with information entries of all matching security. Each list
	  entry contains exactly the same information as returned by
	  :py:func:`security_info`. If no resource matches, the list is empty.
	"""
	res = Security.objects(tech=tech) if tech else Security.objects()
	return [r.info() for r in res]


def security_create(tech, name, attrs=None):
	"""
	Creates a security of given tech and name, configuring it with the given attributes.

	Parameter *tech*:
	  The parameter *tech* must be a string identifying one of the supported
	  security techs.

	Parameter *name*:
	  The parameter *name* must be a string giving a name for the security.

	Parameter *attrs*:
	  The attributes of the security can be given as the parameter *attrs*.
	  This parameter must be a dict of attributes if given. Attributes can
	  later be changed using :py:func:`template_modify`.

	Return value:
	  The return value of this method is the info dict of the new security as
	  returned by :py:func:`resource_info`.
	"""
	if not attrs: attrs = {}
	attrs = dict(attrs)
	attrs.update(name=name, tech=tech)
	res = Security.create(**attrs)
	return res.info()


def security_modify(id, attrs):
	"""
	Modifies a security, configuring it with the given attributes.

	Parameter *id*:
	  The parameter *id* must be a string identifying one of the existing
	  security.

	Parameter *attrs*:
	  The attributes of the security can be given as the parameter *attrs*.
	  This parameter must be a dict of attributes.

	Return value:
	  The return value of this method is the info dict of the resource as
	  returned by :py:func:`security_info`. This info dict will reflect all
	  attribute changes.

	Exceptions:
	  If the given security does not exist an exception *security does not
	  exist* is raised.
	"""
	res = _getSecurity(id)
	res.modify(**attrs)
	return res.info()


def security_remove(id):
	"""
	Removes a security.

	Parameter *id*:
	  The parameter *id* must be a string identifying one of the existing
	  security.

	Return value:
	  The return value of this method is ``None``.

	Exceptions:
	  If the given security does not exist an exception *security does not
	  exist* is raised.
	"""
	res = _getSecurity(id)
	res.remove()
	return {}

@wrap_errors(errorcls_func=lambda e: UserError, errorcode=UserError.ENTITY_DOES_NOT_EXIST)
def security_id(tech, name):
	"""
	translate tech and name to a security id
	"""
	return str(Security.objects.get(tech=tech, name=name).id)

@wrap_errors(errorcls_func=lambda e: UserError, errorcode=UserError.ENTITY_DOES_NOT_EXIST)
def security_info(id): #@ReservedAssignment
	"""
	Retrieves information about a security.

	Parameter *id*:
	  The parameter *id* must be a string identifying one of the existing
	  security.

	Return value:
	  The return value of this method is a dict containing information
	  about this security.

	Exceptions:
	  If the given security does not exist an exception *security does not
	  exist* is raised.
	"""
	res = _getSecurity(id)
	return res.info()
