import main
import os

from branchweb import webserver
from branchweb.usermanager import usermanager
from branchweb.usermanager import USER_FILE
from log import log
import traceback

class r9x_web_providers():
    usermgr: usermanager = None

    @staticmethod
    def setup_usermgr(file: str = USER_FILE):
        r9x_web_providers.usermgr = usermanager(file)
    
    @staticmethod
    def get_post_providers():
        return {
            "auth": r9x_web_providers.auth_endpoint,
            "setupstatus": r9x_web_providers.setupstatus_endpoint,
            "setup": r9x_web_providers.setup_endpoint,
            "vminfo": r9x_web_providers.vminfo_endpoint,
            "start": r9x_web_providers.start_endpoint,
            "reset": r9x_web_providers.reset_endpoint,
            "setiso": r9x_web_providers.setiso_endpoint,
            "setfloppy": r9x_web_providers.setfloppy_endpoint,
            "files": r9x_web_providers.file_endpoint
        }

    @staticmethod
    def get_get_providers():
        return { }


    # ENDPOINT /auth (POST)
    @staticmethod
    def auth_endpoint(httphandler, form_data, post_data):
        # invalid request
        if("user" not in post_data or "pass" not in post_data):
            log.debug("Missing request data for authentication")
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data for authentication")
            return

        p_user = post_data["user"]
        p_pass = post_data["pass"]

        user = r9x_web_providers.usermgr.get_user(p_user)

        if (user is None):
            log.debug("Failed to authenticate user '{}': Not registered".format(p_user))
            httphandler.send_web_response(webserver.webstatus.AUTH_FAILURE, "Authentication failed: user {} is not registered.".format(p_user))
            return

        authkey = user.authenticate(p_pass)

        if (authkey is None):
            log.debug("Authentication failure")
            httphandler.send_web_response(webserver.webstatus.AUTH_FAILURE, "Authentication failed.")
        else:
            log.debug("Authentication succeeded for user {} with new autkey {}".format(user.name, authkey.key_id))
            httphandler.send_web_response(webserver.webstatus.SUCCESS, "{}".format(authkey.key_id))



    # ENDPOINT /status (POST)
    @staticmethod
    def setupstatus_endpoint(httphandler, form_data, post_data):
        if("authkey" not in post_data):
            log.debug("Missing request data for authentication: authkey")
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data for authentication: Authentication key (authkey)")
            return

        authkey = post_data["authkey"]

        user = r9x_web_providers.usermgr.get_key_owner(authkey)
        if (user is None):
            httphandler.send_web_response(webserver.webstatus.AUTH_FAILURE, "Invalid authentication key.")
            return

        user.authkeys[authkey].refresh()

        httphandler.send_web_response(webserver.webstatus.SUCCESS, {
                "setup": main.VMM.setup_mode
            })
   

    # ENDPOINT /setup (POST)
    @staticmethod
    def setup_endpoint(httphandler, form_data, post_data):
        if("authkey" not in post_data):
            log.debug("Missing request data for authentication: authkey")
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data for authentication: Authentication key (authkey)")
            return

        authkey = post_data["authkey"]

        user = r9x_web_providers.usermgr.get_key_owner(authkey)
        if (user is None):
            httphandler.send_web_response(webserver.webstatus.AUTH_FAILURE, "Invalid authentication key.")
            return
    
        user.authkeys[authkey].refresh()
        
        if(not main.VMM.setup_mode):
            httphandler.send_web_response(webserver.webstatus.SERV_FAILURE, "VirtualMachine is already configured!")
            return
        
        try:
            disk_size_mb = int(post_data["disk_size_mb"])
            ram_size_mb = int(post_data["ram_size_mb"])
        except Exception:
            httphandler.send_web_response(webserver.webstatus.SERV_FAILURE, "Could not parse ram_size or disk_size to int")
            return
    
        main.VMM.setup(disk_size_mb, ram_size_mb)

        httphandler.send_web_response(webserver.webstatus.SUCCESS, {
                "setup": main.VMM.setup_mode
            })


    # endpoint /vminfo (post)
    @staticmethod
    def vminfo_endpoint(httphandler, form_data, post_data):
        if("authkey" not in post_data):
            log.debug("Missing request data for authentication: authkey")
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data for authentication: Authentication key (authkey)")
            return

        authkey = post_data["authkey"]

        user = r9x_web_providers.usermgr.get_key_owner(authkey)
        if (user is None):
            httphandler.send_web_response(webserver.webstatus.AUTH_FAILURE, "Invalid authentication key.")
            return
    
        user.authkeys[authkey].refresh()
        
        if(main.VMM.setup_mode):
            httphandler.send_web_response(webserver.webstatus.SUCCESS, "VirtualMachine is not configured yet.")
        else:
            httphandler.send_web_response(webserver.webstatus.SUCCESS, main.VMM.get_vmconf())


    # endpoint /start (post)
    @staticmethod
    def start_endpoint(httphandler, form_data, post_data):
        if("authkey" not in post_data):
            log.debug("Missing request data for authentication: authkey")
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data for authentication: Authentication key (authkey)")
            return

        authkey = post_data["authkey"]

        user = r9x_web_providers.usermgr.get_key_owner(authkey)
        if (user is None):
            httphandler.send_web_response(webserver.webstatus.AUTH_FAILURE, "Invalid authentication key.")
            return
    
        user.authkeys[authkey].refresh()
        if(main.VMM.start()):
            httphandler.send_web_response(webserver.webstatus.SUCCESS, "VirtualMachine started.")
        else:
            httphandler.send_web_response(webserver.webstatus.SUCCESS, "VM is already running.")


    # endpoint /reset (post)
    @staticmethod
    def reset_endpoint(httphandler, form_data, post_data):
        if("authkey" not in post_data):
            log.debug("Missing request data for authentication: authkey")
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data for authentication: Authentication key (authkey)")
            return

        authkey = post_data["authkey"]

        user = r9x_web_providers.usermgr.get_key_owner(authkey)
        if (user is None):
            httphandler.send_web_response(webserver.webstatus.AUTH_FAILURE, "Invalid authentication key.")
            return
    
        user.authkeys[authkey].refresh()
        if(main.VMM.reset()):
            httphandler.send_web_response(webserver.webstatus.SUCCESS, "Resetting VirtualMachine.")
        else:
            httphandler.send_web_response(webserver.webstatus.SUCCESS, "QMP connection is not ready!")


    # endpoint /setiso (post)
    @staticmethod
    def setiso_endpoint(httphandler, form_data, post_data):
        if("iso" not in post_data):
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data: iso")
            return

        if("authkey" not in post_data):
            log.debug("Missing request data for authentication: authkey")
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data for authentication: Authentication key (authkey)")
            return

        authkey = post_data["authkey"]

        user = r9x_web_providers.usermgr.get_key_owner(authkey)
        if (user is None):
            httphandler.send_web_response(webserver.webstatus.AUTH_FAILURE, "Invalid authentication key.")
            return
    
        user.authkeys[authkey].refresh()

        if(main.VMM.setiso(post_data["iso"])):
            httphandler.send_web_response(webserver.webstatus.SUCCESS, "ISO set.")
        else:
            httphandler.send_web_response(webserver.webstatus.SUCCESS, "Could not set ISO")



    # endpoint /setfloppy (post)
    @staticmethod
    def setfloppy_endpoint(httphandler, form_data, post_data):
        if("floppy" not in post_data):
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data: floppy")
            return

        if("authkey" not in post_data):
            log.debug("Missing request data for authentication: authkey")
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data for authentication: Authentication key (authkey)")
            return

        authkey = post_data["authkey"]

        user = r9x_web_providers.usermgr.get_key_owner(authkey)
        if (user is None):
            httphandler.send_web_response(webserver.webstatus.AUTH_FAILURE, "Invalid authentication key.")
            return
    
        user.authkeys[authkey].refresh()

        if(main.VMM.setfloppy(post_data["floppy"])):
            httphandler.send_web_response(webserver.webstatus.SUCCESS, "Floppy set.")
        else:
            httphandler.send_web_response(webserver.webstatus.SUCCESS, "Could not set floppy.")



    # endpoint /files (post)
    @staticmethod
    def file_endpoint(httphandler, form_data, post_data):
        if("authkey" not in post_data):
            log.debug("Missing request data for authentication: authkey")
            httphandler.send_web_response(webserver.webstatus.MISSING_DATA, "Missing request data for authentication: Authentication key (authkey)")
            return

        authkey = post_data["authkey"]

        user = r9x_web_providers.usermgr.get_key_owner(authkey)
        if (user is None):
            httphandler.send_web_response(webserver.webstatus.AUTH_FAILURE, "Invalid authentication key.")
            return
    
        user.authkeys[authkey].refresh()
        
        httphandler.send_web_response(webserver.webstatus.SUCCESS, {
                "isos": os.listdir("iso/"),
                "floppy": os.listdir("floppy/")
            })
