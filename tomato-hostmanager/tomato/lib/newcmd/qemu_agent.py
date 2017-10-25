from . import Error, SUPPORT_CHECK_PERIOD
from .util.cmd import run
import os, socket, contextlib, json, subprocess, os, base64, uuid


SOCK_BUF_LEN = 65536
SOCK_TIMEOUT = 3  # seconds


class QemuAgentError(Error):
    CODE_UNKNOWN = "qemu_agent.unknown"
    CODE_UNSUPPORTED = "qemu_agent.unsupported"     # qga functions not supported, usually because qga not working properly on guest
    CODE_FAILED_TO_SET = "qemu_agent.failed_to_set" # failed change qemu settings on host machine
    CODE_SYNC_FAILED = "qemu_agent.sync_failed"     # can not get synchronized
    CODE_EXECUTE_ERROR = "qemu_agent.execute_error" # get error message from qga resnponse


def random_64bit_int():
    """generate a random 64-bit long integer"""
    return uuid.uuid1().int >> 64

def qga_path(vmid):
    """path of qga socket"""
    return "/var/run/qemu-server/%d.qga" % self.vmid

def qga_exists(vmid):
    """check if qga socket exists"""
    return os.path.exists(qga_path(vmid))

def qga_check(vmid):
    """raise error if qga socket does not exist"""
    path = qga_path(vmid)
    QemuAgentError.check(os.path.exists(path), QemuAgentError.CODE_UNSUPPORTED,
        "QGA socket not found, ensure that agent setting is enabled")
    QemuAgentError.check(stat.S_ISSOCK(os.stat(path).st_mode), QemuAgentError.CODE_UNSUPPORTED,
        "QGA file is not a socket file, weird")
    return True

def qga_enable(vmid):
    """enable Qemu Guest Agent for a VM"""
    command = ["qm", "set", str(vmid), "-agent", "1"]
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = proc.communicate()
    return_code = proc.returncode
    if return_code != 0
        raise QemuAgentError(
            code=QemuAgentError.CODE_FAILED_TO_SET,
            message="qm failed enable agent",
            data={"return_code": return_code,"output": output, "err": err}
        )
    return True


@contextlib.contextmanager
def _get_connected_socket(vmid):
    """
    return socket object connected to qga, with context manager
    Usage:
        with _get_connected_socket() as s:
            # do something with s
    """
    qga_check(vmid)
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(SOCK_TIMEOUT)
    try:
        s.connect(qga_path(vmid))
        yield s
    except socket.timeout as e:
        raise e
    finally:
        s.close()

def _qga_send(vmid, data_obj):
    """
    Open a socket and send command data

    Args:
        vmid (int): vmid
        data_obj (dict): a dict represents json data
    
    Return:
        the total length of sent data

    Raises:
        socket.timeout
    """
    qga_check(vmid)
    with _get_connected_socket(vmid) as s:
        sent_length = s.sendall(json.dumps(data_obj))
        return sent_length

def _qga_recv(vmid):
    """
    Open the qga socket and recv data

    Args:
        vmid (int): vmid

    Return:
        a dict contains json data from qga socket

    Raises:
        socket.timeout: if receiving timeout
        TypeError: if JSON stringify or parse failed
    """
    with _get_connected_socket(vmid) as s:
        buf, data = '', None
        while True:
            data = s.recv(SOCK_BUF_LEN)
            if not data:
                break
            buf += data
        if not buf:
            return None
        return json.loads(buf)

def _qga_recv_delimited(vmid):
    """
    Open the qga socket and recv data
    only data after `0xff` will be returned, for `guest_sync_delimited`

    Args:
        vmid (int): vmid

    Return:
        a dict contains json data from qga socket

    Raise:
        socket.timeout: if receiving timeout
        TypeError: if JSON stringify or parse failed
    """
    with _get_connected_socket(vmid) as s:
        buf, data = '', None
        while True:
            data = s.recv(SOCK_BUF_LEN)
            if not data:
                break
            buf += data
        if not buf:
            return None
        buf = buf.split('\xff')[-1]
        return json.loads(buf)


# def guest_sync_delimited(vmid, _id=None):
#     """
#     Send a `guest_sync_delimited` command to qga socket

#     > Echo back a unique integer value, and prepend to response a leading sentinel byte (0xFF) the client can check scan for.
#     > After this '\xff{"return": <id>}' should be recved from qga socket

#     Args:
#         vmid (int): vmid
#         _id (int): randomly generated 64-bit integer
#     """
#     if not _id:
#         _id = random_64bit_int()
#     data = {"execute": "guest-sync-delimited", "arguments": {"id": _id}}
#     return _qga_send(vmid, data)

# def guest_sync(vmid, _id):
#     """
#     Send a `guest_sync` command to qga socket

#     > Echo back a unique integer value
#     > After this '{"return": <id>}' should be recved from qga socket

#     Args:
#         vmid (int): vmid
#         _id (int): randomly generated 64-bit integer
#     """
#     if not _id:
#         _id = random_64bit_int()
#     data = {"execute": "guest-sync", "arguments": {"id": _id}}
#     return _qga_send(vmid, data)

# def sync(vmid):
#     """
#     sync with guest, use guest_sync_delimited
#     return True if synchronized successfully
#     """
#     random_id = random_64bit_int()
#     guest_sync_delimited(vmid, random_id) # send guest_sync_demilited command
#     recved = _qga_recv_delimited(vmid)
#     if recved["return"] != random_id:
#         raise QemuAgentError(code=QemuAgentError.CODE_SYNC_FAILED, message="qga sync failed", data={"send_id": random_id, "recv_id": recved["return"]})
#     return True

def sync(vmid):
    """
    Get sync with guest
    """
    _id = random_64bit_int()
    guest_sync_delimited = {
        "execute": "guest-sync-delimited"
        "arguments": {"id": _id}
    }
    try:
        _qga_send(vmid, json.dumps(guest_sync_delimited))
        res = _qga_recv_delimited(vmid)
        if res["return"] != _id:
            raise QemuAgentError(
                code=QemuAgentError.CODE_SYNC_FAILED,
                data={"sent_id": _id, "received_id": res["return"], "received": res}
            )
    except Error as e:
        raise QemuAgentError(
            code=QemuAgentError.CODE_SYNC_FAILED,
            message="failed get sync with guest",
            data={"error": e}
        )
    return True


def guest_info(vmid):
    """
    Execute the `guest-info` command through Qemu Guest Agent.
    Returned object contains guest agent info
    Require guest machine running Qemu Guest Agent 0.15.0 or higher.

    Args:
        vmid (int): vmid
    
    Returns:
        Dict contains guest agent info
        - version (str): Guest agent version
        - supported_commands (list of obj): Information about guest agent commands
            - name (str): name of the command
            - enabled (bool): whether command is currently enabled by guest admin
            - success-response (bool): whether command returns a response on success (since 1.7)
    """
    data = { "command": "guest-info" }
    _qga_send(vmid, data)
    rtn = _qga_recv(vmid)
    return rtn["return"]

# TODO
def guest_ping(vmid):
    """
    Execute the `guest-info` command through Qemu Guest Agent.
    Ping the guest agent, a non-error return implies success.
    Will get non-error response: `{"return": {}}\n`
    Require guest machine running Qemu Guest Agent 0.15.0 or higher.

    Args:
        vmid (int): vmid
    """
    data = { "command": "guest-ping" }
    _qga_send(vmid, data)
    rtn = _qga_recv(vmid)
    return rtn

def guest_exec(vmid, path, arg=None, env=None, input_data=None, capture_output=True):
    """
    Execute the `guest-exec` command through Qemu Guest Agent, which will execute a command in the guest.
    Require guest machine running Qemu Guest Agent 2.5 or higher.
    Will return JSON like `{"return": {"pid": 1234567}}`
    Should check QGA is working properly before execute

    Args:
        vmid (int): vmid
        path (str): path or executable name to execute.
        arg (list of str): (optional) argument list to pass to executable.
        env (list of str): (optinoal) environment variables to pass to executable.
        input_data (str): (optional) data to be passed to process stdin (base64 encoded).
        capture-output (boolean): (optional) bool flag to enable capture of stdout/stderr of running process. defaults to false.
    
    Returns:
        pid (int): process id

    Raises:
        TODO
    """
    data = { "execute": "guest-exec", "arguments": { "path": path, "capture-output": capture_output } }
    if arg:
        data["argument"]["arg"] = arg  # if arg is None, or arg is []
    if env:
        data["argument"]["env"] = env
    if input_data:
        data["argument"]["input-data"] = base64.b64encode(input_data)
    _qga_send(vmid, data)
    received = _qga_recv(vmid)
    pid = received["return"]["pid"]
    return pid

# TODO
def guest_exec_status(vmid, pid):
    """
    Execute the `guest-exec-status` command through Qemu Guest Agent.
    Check status of process associated with PID retrieved via guest-exec. Reap the process and associated metadata if it has exited.
    Require guest machine running Qemu Guest Agent 2.5 or higher.

    Args:
        vmid (int): vmid
        pid (int): pid of child process in guest OS
    
    Returns:
        Dict contains process status info. Note: out-data and err-data are present only if `capture-output` was specified for `guest-exec`.
        - exited (bool): true if process has already terminated.
        - exitcode (int): (optional) process exit code if it was normally terminated.
        - signal (int): (optional) signal number (linux) or unhandled exception code (windows) if the process was abnormally terminated.
        - out-data (str): (optional) base64-encoded stdout of the process.
        - err-data (str): (optional) base64-encoded stderr of the process.
        - out-truncated (bool): (optional) true if stdout was not fully captured due to size limitation.
        - err-truncated (bool): (optional) true if stderr was not fully captured due to size limitation.
    
    Raises:
        TODO
    """
    data = { "execute": "guest-exec-status", "arguments": { "pid": pid } }
    _qga_send(vmid, data)
    rtn = _qga_recv(vmid)
    return rtn["return"]

# TODO
def execute_and_get_output(vmid, path, arg=None, env=None, input_data=None, capture_output=True):
    """
    run command on guest and get the output, use `guest_exec` and `guest_exec_status`
    sync with func `sync` first

    Return (return_code, output)
    """
    # check qga enabled
    qga_check(vmid)
    # sync, with timeout setting
    sync(vmid)
    # send execute and receive pid
    pid = guest_exec(vmid, path, arg=arg, env=env, input_data=input_data, capture_output=capture_output=True)
    
    # continue sending guest_exec_status, and trying to get execute result
    while True:
        status = guest_exec_status(vmid, pid)
        if status["exited"]:
            break
    return (status["exitcode"], status["out-data"], status["err-data"])
