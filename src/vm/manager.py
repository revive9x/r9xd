import subprocess
import os
import time
import json

from qmp.qmp import QMP
from log import log

class VMManager():
    
    def __init__(self, qemu_bin: str, qmp_socket_path: str):
        """
        Initialize VMManager class
        """
        self.qemu_bin = qemu_bin
        self.qmp_socket_path = qmp_socket_path
        self.qemu_process = None
        self.qmp = None
        self.cdrom_mode = "SCSI" # default

        if(os.path.exists("vm.json")):
            self.setup_mode = False

            with open("vm.json", "r+") as f:
                self.conf = json.loads(f.read())

        else:
            self.setup_mode = True
    
    def setup(self, disk_size_mb, memory_size_mb):
        """
        Initial setup for running a VM
        """
        
        if(not os.path.exists("iso")):
            os.mkdir("iso")
        
        if(not os.path.exists("floppy")):
            os.mkdir("floppy")
        
        # fetch this:
        # https://github.com/JHRobotics/patcher9x/releases/download/v0.8.50/patcher9x-0.8.50-boot.ima

        os.system(f"qemu-img create -f qcow2 win98.qcow2 {disk_size_mb}M")
        
        # Write VM Config
        self.conf = {
                "disk_size": disk_size_mb,
                "ram_size": memory_size_mb,
                "display": "1920x1080",
                "iso": None,
                "floppy": None,
            }

        with open("vm.json", "w+") as f:
            f.write(json.dumps(self.conf))

        self.setup_mode = False

    def get_vmconf(self):
        return {
                "running": self.is_running(),
                "conf": self.conf
            }

    def is_running(self) -> bool:
        """
        Check if VM is running.
        """
        if(self.qemu_process is None):
            return False

        if(not self.qemu_process.poll() is None):
            return False

        return True

    def start(self):
        """
        Start the VirtualMachine, establish QMP connection
        """
        if(self.is_running()):
            return False

        log.info(f"Launching QEMU ({self.qemu_bin})..")
        
        # SCSI CD mode
        if(self.cdrom_mode == "SCSI"):
            log.info("Starting in SCSI CDRom mode.")
            self.qemu_process = subprocess.Popen(
                    [self.qemu_bin,
                        "-nodefaults", "-rtc", "base=localtime", "-display", "sdl",
                        "-boot", "menu=on",
                        "-M", "pc,accel=kvm,hpet=off,usb=off", "-cpu", "host",
                        "-qmp", f"unix:{self.qmp_socket_path},server,nowait", # QMP Unix socket
                        "-full-screen",
                        "-device", "VGA", "-device", "lsi", "-device", "ac97",
                        "-netdev", "user,id=net0", "-device", "pcnet,rombar=0,netdev=net0",
                        "-drive", "id=win98,if=none,file=win98.qcow2", "-device", "scsi-hd,drive=win98",
                        "-drive", "id=iso,if=none,media=cdrom", "-device", "scsi-cd,drive=iso",
                     ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # IDE CD mode
        else:
            log.info("Starting in IDE CDRom mode.")
            self.qemu_process = subprocess.Popen(
                    [self.qemu_bin,
                        "-nodefaults", "-rtc", "base=localtime", "-display", "sdl",
                        "-boot", "menu=on",
                        "-M", "pc,accel=kvm,hpet=off,usb=off", "-cpu", "host",
                        "-qmp", f"unix:{self.qmp_socket_path},server,nowait", # QMP Unix socket
                        "-full-screen",
                        "-device", "VGA", "-device", "lsi", "-device", "ac97",
                        "-netdev", "user,id=net0", "-device", "pcnet,rombar=0,netdev=net0",
                        "-drive", "id=win98,if=none,file=win98.qcow2", "-device", "scsi-hd,drive=win98",
                        "-drive", "id=iso,if=none,media=cdrom", "-device", "ide-cd,drive=iso",
                     ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        not_ready = True
        while not_ready:
            if(os.path.exists(self.qmp_socket_path)):
                not_ready = False
                continue

            time.sleep(0.1)
        
        log.info(f"QMP connection established to '{self.qmp_socket_path}', PID: {self.qemu_process.pid}")
        self.qmp = QMP(self.qmp_socket_path)
        return True
    
    def kill(self):
        """
        Kill virtualmachine
        """
        if(not self.is_running()):
            return
        
        self.qmp.destroy()
        self.qemu_process.terminate()
        log.info("Virtualmachine terminated.")
    
    def reset(self) -> bool:
        """
        Send a Reset request to QEMU
        """
        q = self.get_qmp()
        if(q is None):
            return False

        q.execute_qmp_command({
            "execute": "system_reset"
        })
        return True
    
    
    def setiso(self, filename) -> bool:
        """
        Set ISO image
        """
        q = self.get_qmp()
        if(q is None):
            return False

        if(not filename in os.listdir("iso/")):
            return False
        
        q.send_qmp_message({
            "execute": "blockdev-change-medium",
            "arguments": {
                    "device": "iso",
                    "filename": f"iso/{filename}"
                }
        })
        return True

    def ejectiso(self) -> bool:
        """
        Eject ISO image from CD drive
        """
        q = self.get_qmp()
        if(q is None):
            return False

        q.send_qmp_message({
                "execute": "eject",
                "device": "cdrom",
                "force": "true"
            })
        return True

    def setfloppy(self, filename) -> bool:
        """
        Set ISO image
        """
        q = self.get_qmp()
        if(q is None):
            return False

        if(not filename in os.listdir("floppy/")):
            return False

        q.send_qmp_message({
            "execute": "blockdev-change-medium",
            "arguments": {
                    "device": "floppy0",
                    "filename": f"floppy/{filename}"
                }
        })
        return True

    def ejectfloppy(self) -> bool:
        """
        Eject floppy image from floppy drive
        """
        q = self.get_qmp()
        if(q is None):
            return False

        q.send_qmp_message({
                "execute": "eject",
                "device": "floppy0",
                "force": "true"
            })
        return True
    
    def queryblock(self):
        """
        Query block devices
        """
        q = self.get_qmp()
        if(q is None):
            return False

        return q.execute_qmp_command({
            "execute": "query-block"
        })


    def get_qmp(self) -> QMP:
        """
        Get QMP socket object if it exists or None
        """
        if(not self.is_running()):
            return None

        return self.qmp
