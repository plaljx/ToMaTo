from ..lib.service import get_backend_core_proxy
from api_helpers import checkauth, getCurrentUserInfo
from ..lib.remote_info import get_security_info, get_security_list, SecurityInfo

@checkauth
def security_list(tech=None):
	"""
	Retrieves information about all resources.

	Parameter *tech*:
	  If *tech* is set, only resources with a matching tech will be returned.

	Return value:
	  A list with information entries of all matching securitys. Each list
	  entry contains exactly the same information as returned by
	  :py:func:`security_info`. If no resource matches, the list is empty.
	"""
	#return get_security_list(tech)
	security_list = [{"name":360,"tech":"software","subtype":"windows"}]
	return security_list

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
	  later be changed using :py:func:`security_modify`.

	Return value:
	  The return value of this method is the info dict of the new security as
	  returned by :py:func:`resource_info`.
	"""
	getCurrentUserInfo().check_may_create_user_resources()
	return SecurityInfo.create(tech, name, attrs)

def security_modify(id, attrs):
	"""
	Modifies a security, configuring it with the given attributes.

	Parameter *id*:
	  The parameter *id* must be a string identifying one of the existing
	  securitys.

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
	getCurrentUserInfo().check_may_modify_user_resources()
	return get_security_info(id).modify(attrs)

def security_remove(id):
	"""
	Removes a security.

	Parameter *id*:
	  The parameter *id* must be a string identifying one of the existing
	  securitys.

	Return value:
	  The return value of this method is ``None``.

	Exceptions:
	  If the given security does not exist an exception *security does not
	  exist* is raised.
	"""
	getCurrentUserInfo().check_may_remove_user_resources()
	return get_security_info(id).remove()

@checkauth
def security_info(id): #@ReservedAssignment
	"""
	Retrieves information about a security.

	Parameter *id*:
	  The parameter *id* must be a string identifying one of the existing
	  securitys.

	Return value:
	  The return value of this method is a dict containing information
	  about this security.

	Exceptions:
	  If the given security does not exist an exception *security does not
	  exist* is raised.
	"""
	secur = get_security_info(id)
	return secur.info(update=True)
