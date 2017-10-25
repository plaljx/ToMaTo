from . import Error, SUPPORT_CHECK_PERIOD
from .util.cmd import run
import os, socket, contextlib, json, subprocess, os


SOCK_BUF_LEN = 65536
SOCK_TIMEOUT = 3  # seconds


class QemuAgentError(Error):
    CODE_UNKNOWN = "qemu_agent.unknown"
    CODE_UNSUPPORTED = "qemu_agent.unsupported"
    CODE_FAILED_TO_SET = "qemu_agent.failed_to_set"


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
        raise QemuAgentError(code=QemuAgentError.CODE_FAILED_TO_SET, message="qm failed enable agent", data={err: err})
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
    pass


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
        socket.timeout
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
        socket.timeout
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


# TODO
def guest_sync_delimited(vmid, _id):
    """
    Echo back a unique integer value, and prepend to response a leading sentinel byte (0xFF) the client can check scan for.
    After this '\xff{"return": <id>}' should be recved from qga socket

    Args:
        vmid (int): vmid
        _id (int): randomly generated 64-bit integer
    """
    data = { "execute": "guest-sync-delimited", "arguments": { "id": _id } }
    # recv data starts with a '0xFF'
    pass

# TODO
def guest_sync(vmid, _id):
    """
    Echo back a unique integer value
    After this '{"return": <id>}' should be recved from qga socket

    Args:
        vmid (int): vmid
        _id (int): randomly generated 64-bit integer
    """
    data = { "execute": "guest-sync"}
    pass

# TODO
def guest_info(vmid):
    """
    Execute the `guest-info` command through Qemu Guest Agent.
    Get some information about the guest agent.
    Require guest machine running Qemu Guest Agent 0.15.0 or higher.

    Args:
        vmid (int): vmid
    
    Returns:
        Object contains guest agent info
        - return (obj)
            - version (str): Guest agent version
            - supported_commands (list of obj): Information about guest agent commands
                - name (str): name of the command
                - enabled (bool): whether command is currently enabled by guest admin
                - success-response (bool): whether command returns a response on success (since 1.7)
    """
    data = { "command": "guest-info" }
    pass

# TODO
def guest_ping(vmid):
    """
    Execute the `guest-info` command through Qemu Guest Agent.
    Ping the guest agent, a non-error return implies success.
    Require guest machine running Qemu Guest Agent 0.15.0 or higher.

    Args:
        vmid (int): vmid
    """
    data = { "command": "guest-ping" }
    pass

# TODO
def guest_exec(vmid, path, arg=None, env=None, input_data=None, capture_output=True):
    """
    Execute the `guest-exec` command through Qemu Guest Agent.
    Execute a command in the guest.
    Require guest machine running Qemu Guest Agent 2.5 or higher.

    Args:
        vmid (int): vmid
        path (str): path or executable name to execute.
        arg (list of str): (optional) argument list to pass to executable.
        env (list of str): (optinoal) environment variables to pass to executable.
        input_data (str): (optional) data to be passed to process stdin (base64 encoded).
        capture-output (boolean): (optional) bool flag to enable capture of stdout/stderr of running process. defaults to false.
    
    Returns:
        Object
        - return
            - pid (int) pid returned from guest-exec

    Raises:
        TODO
    """
    data = { "execute": "guest-exec", "arguments": { "path": path, "capture-output": capture_output } }
    if arg:
        data["argument"]["arg"] = arg
    if env:
        data["argument"]["env"] = env
    if input_data:
        data["argument"]["input-data"] = input_data
    # DO: Get PID and return
    pass

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
        Object. Note: out-data and err-data are present only if `capture-output` was specified for `guest-exec`.
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
    # DO: check until `exited` is True, and return the results

    # note: should do -- received_data = received_data["return"]
    pass


# TODO
def sync(vmid):
    """
    sync with guest, use guest_sync_delimited
    """
    pass


# TODO
def execute_and_get_output(vmid, path, arg=None, env=None, input_data=None, capture_output=True):
    """
    run command on guest and get the output, use `guest_exec` and `guest_exec_status`
    sync with func `sync` first

    Args:
        vmid (int): vmid
        cmd (list of str): list of path and 
    """
    pass
