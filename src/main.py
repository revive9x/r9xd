import socket
import json
import os

from web import endpoints
from branchweb import webserver
from qmp.qmp import QMP
from log import log
from vm.manager import VMManager

R9XD_CODENAME="Black Mesa Inbound"
R9XD_VERSION=0.1

CONF = {
    "host": "localhost",
    "port": 8080,
    "qemu-bin": "../../qemu-3dfx-fork/build/qemu-system-i386",
    "qmp-socket": "/tmp/qmpsock"
}
VMM = VMManager(CONF['qemu-bin'], CONF['qmp-socket'])

def mold():
    q = QMP("qemu-monitor-socket")
    
    print("reset request..")
    res = q.execute_qmp_command({
            "execute": "system_reset"
        })
    print(res)

    print("vm status..")
    res = q.execute_qmp_command({
            "execute": "query-status"
        })

    print(res)

    print("block query..")
    res = q.execute_qmp_command({
            "execute": "query-block"
        })
    print(res)

    print("set cdrom")
    q.send_qmp_message({
            "execute": "blockdev-change-medium",
            "arguments": {
                    "device": "ide1-cd0",
                    "filename": "/home/zimsneexh/dev/qemu-3dfx-fork/build/w98.iso"
                }
        })
    
    input()
    #print("send eject")
    #res = q.send_qmp_message({
    #        "execute": "eject",
    #        "device": "ide1-cd0",
    #        "force": "true"
    #    })

    q.destroy()


def main():
    #v = VMManager(CONF['qemu-bin'], CONF['qmp-socket'])
   # v.start()

  #  input()
   # v.kill()


    log.initialize()
    print(f"r9xd {R9XD_VERSION}, ({R9XD_CODENAME})")
    print("Copyright (c) zimsneexh (https://zsxh.eu)\n")

    #log.info(f"Checking for KVM acceleration..")
    #if(os.path.exists("/dev/kvm")):
    #    log.info("KVM acceleration is available.")

    #else:
    #    log.warn("KVM acceleration is not available.")

    log.info("Starting webserver..")
    log.info(f"Listening on 'http://{CONF['host']}:{CONF['port']}'")
    
    endpoints.r9x_web_providers.setup_usermgr("users.conf")
    webserver.WEB_CONFIG["logger_function_debug"] = log.debug
    webserver.WEB_CONFIG["logger_function_info"] = log.web_log

    webserver.web_server.register_get_endpoints(
        endpoints.r9x_web_providers.get_get_providers())
    webserver.web_server.register_post_endpoints(
        endpoints.r9x_web_providers.get_post_providers())
    
    webserver.start_web_server(CONF['host'], CONF['port'])

if(__name__ == "__main__"):
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting on KeyboardInterrupt")
