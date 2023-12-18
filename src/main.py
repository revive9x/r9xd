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
    "host": "0.0.0.0",
    "port": 8080,
    "qemu-bin": "../../qemu-3dfx-fork/build/qemu-system-i386",
    "qmp-socket": "/tmp/qmpsock"
}
VMM = VMManager(CONF['qemu-bin'], CONF['qmp-socket'])

def main():
    log.initialize()
    print(f"r9xd {R9XD_VERSION}, ({R9XD_CODENAME})")
    print("Copyright (c) zimsneexh (https://zsxh.eu)\n")

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
