from ...lib.service import get_backend_users_proxy, get_backend_core_proxy, get_backend_accounting_proxy


def malicious_code_list():
    return get_backend_core_proxy().malicious_code_list()


def malicious_code_create(attrs):
    return get_backend_core_proxy().malicious_code_create(attrs)


def malicious_code_modify(id_, attrs):
    return get_backend_core_proxy().malicious_code_modify(id_, attrs)


def malicious_code_remove(id_):
    return get_backend_core_proxy().malicious_code_remove(id_)


def malicious_code_info(id_):
    return get_backend_core_proxy().malicious_code_info()

