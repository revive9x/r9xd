import os
import inspect

HEADER = '\033[95m'
NORMAL = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

#
# array of output provider functions
#
# Output provider function: test(module, level, logmessage)
#
OUTPUT_PROVIDERS = [ ]

#
# dict of log config options
#
CONFIG_OPTIONS = {
    # used to determine if logger is running inside docker
    "NO_TERM": True,

    # enable debug log
    "DEBUG_LOG": False
}

#
# checks the environment for TERM variable and
# disables color log if no TERm is available.
#
def initialize():
    if("TERM" in os.environ):
        CONFIG_OPTIONS["NO_TERM"] = False
    else:
        print("No terminal available. Disabling log color.")
initialize()

#
# Disable debug log messages
#
def disable_debug_level():
    CONFIG_OPTIONS["DEBUG_LOG"] = False

#
# enable debug log messages
#
def enable_debug_level():
    CONFIG_OPTIONS["DEBUG_LOG"] = True

#
# register Output provider function
#
def register_output_provider(callback):
    OUTPUT_PROVIDERS.append(callback)

#
# Unregister output provider function
#
def unregister_output_provider(callback):
    OUTPUT_PROVIDERS.remove(callback)

def warn(log):
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0]).__name__

    for output_prov in OUTPUT_PROVIDERS:
        output_prov(module, "WARN", log)

    if(CONFIG_OPTIONS["NO_TERM"]):
        print("[WARN] {}: {} ".format(module, log))
    else:
        print("{}{:<8}{}{}{:<24}{} {}".format(BOLD, "[WARN]", ENDC, WARNING, module, ENDC, log))

def error(log):
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0]).__name__

    for output_prov in OUTPUT_PROVIDERS:
        output_prov(module, "ERROR", log)

    if(CONFIG_OPTIONS["NO_TERM"]):
        print("[ERROR] {}: {} ".format(module, log))
    else:
        print("{}{:<8}{}{}{:<24}{} {}".format(BOLD, "[ERROR]", ENDC, FAIL, module, ENDC, log))

def info(log):
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0]).__name__

    for output_prov in OUTPUT_PROVIDERS:
        output_prov(module, "INFO", log)

    if(CONFIG_OPTIONS["NO_TERM"]):
        print("[INFO] {}: {} ".format(module, log))
    else:
        print("{}{:<8}{}{}{:<24}{} {}".format(BOLD, "[INFO]", ENDC, OKGREEN, module, ENDC, log))

def web_log(log):
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0]).__name__

    for output_prov in OUTPUT_PROVIDERS:
        output_prov(module, "WEB", log)   

    if(CONFIG_OPTIONS["NO_TERM"]):
        print("[WEB] {}: {} ".format(module, log))
    else:
        print("{}{:<8}{}{}{:<24}{} {}".format(BOLD, "[WEB]", ENDC, OKCYAN, module, ENDC, log))

def debug(log):
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0]).__name__

    for output_prov in OUTPUT_PROVIDERS:
        output_prov(module, "DEBUG", log)

    if(CONFIG_OPTIONS["DEBUG_LOG"]):
        if(CONFIG_OPTIONS["NO_TERM"]):
            print("[DEBUG] {}: {} ".format(module, log))
        else:
            print("{}{:<8}{}{}{:<24}{} {}".format(BOLD, "[DEBUG]", ENDC, OKCYAN, module, ENDC, log))

