from ...security_resources.security_software import SecuritySoftware
from ...lib.error import UserError
from ...lib.exceptionhandling import wrap_errors


@wrap_errors(errorcls_func=lambda e: UserError, errorcode=UserError.ENTITY_DOES_NOT_EXIST)
def _get_security_software(id_):
    res = SecuritySoftware.objects.get(id=id_)
    UserError.check(res, code=UserError.ENTITY_DOES_NOT_EXIST, message="SecuritySoftware does not exist", data={"id": id_})
    return res


def security_software_list():
    res_list = SecuritySoftware.objects()
    return [res.info() for res in res_list]


def security_software_create(attrs=None):
    if not attrs:
        attrs = {}
    attrs = dict(attrs)
    res = SecuritySoftware.create(**attrs)
    return res.info()


def security_software_modify(id_, attrs=None):
    res = _get_security_software(id_)
    res.modify(**attrs)
    return res.info()


def security_software_remove(id_):
    res = _get_security_software(id_)
    res.remove()
    return {}


def security_software_info(id_):
    res = _get_security_software(id_)
    return res.info()

