from ...lib.service import get_backend_users_proxy, get_backend_core_proxy, get_backend_accounting_proxy


def security_software_list():
    return get_backend_core_proxy().security_software_list()


def security_software_create(attrs):
    return get_backend_core_proxy().security_software_create(attrs)


def security_software_modify(id_, attrs):
    return get_backend_core_proxy().security_software_modify(id_, attrs)


def security_software_remove(id_):
    return get_backend_core_proxy().security_software_remove(id_)


def security_software_info(id_):
    return get_backend_core_proxy().security_software_info(id_)

