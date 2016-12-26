from ...security_resources.malicious_code import MaliciousCode
from ...lib.error import UserError
from ...lib.exceptionhandling import wrap_errors


@wrap_errors(errorcls_func=lambda e: UserError, errorcode=UserError.ENTITY_DOES_NOT_EXIST)
def _get_malicious_code(id_):
    res = MaliciousCode.objects.get(id=id_)
    UserError.check(res, code=UserError.ENTITY_DOES_NOT_EXIST, message="MaliciousCode does not exist", data={"id": id_})
    return res


def malicious_code_list():
    res_list = MaliciousCode.objects()
    return [res.info() for res in res_list]


def malicious_code_create(attrs=None):
    if not attrs:
        attrs = {}
    attrs = dict(attrs)
    res = MaliciousCode.create(**attrs)
    return res.info()


def malicious_code_modify(id_, attrs=None):
    res = _get_malicious_code(id_)
    res.modify(**attrs)
    return res.info()


def malicious_code_remove(id_):
    res = _get_malicious_code(id_)
    res.remove()
    return {}


def malicious_code_info(id_):
    res = _get_malicious_code(id_)
    return res.info()

