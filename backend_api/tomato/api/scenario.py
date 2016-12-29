# by Chang Rui

from orchestration.topology_export_import import topology_export, topology_import
from ..lib.service import get_backend_core_proxy
from ..lib import anyjson as json

def scenario_save(topo_id, data=None):
    if not data:
        data = {}
    topo_full_info = topology_export(topo_id)
    topo_full_json = json.orig.dumps(topo_full_info, indent=2)
    data["topology_info_json"] = topo_full_json
    response = get_backend_core_proxy().scenario_create(data)
    return response

def scenario_create(data=None):
    if not data:
        data = {}
    response = get_backend_core_proxy().scenario_create(data)
    return response


def scenario_deploy(id_):
    topology_info_json = get_backend_core_proxy().scenario_topology_info_json(id_)
    topology_structure = json.loads(topology_info_json)
    print "get topology_structure, type is %s" % type(topology_structure)
    topo_id, _, _, errors = topology_import(topology_structure) # topo_id, elements, connections, errors
    return {'topo_id': topo_id, 'errors': errors}


def scenario_list(user, show):
    response = get_backend_core_proxy().scenario_list(user, show)
    return response


def scenario_modify(id_, data=None):
    response = get_backend_core_proxy().scenario_modify(id_, data)
    return response


def scenario_remove(id_):
    response = get_backend_core_proxy().scenario_remove(id_)
    return response


def scenario_info(id_):
    response = get_backend_core_proxy().scenario_info(id_)
    return response
