import json
import socket

class QMP():
    
    def __init__(self, path):
        """
        Init QMP connection to

        :param path: The QEMU unix socket path
        """
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(path)
    
        hello_msg = self.receive_qmp_message()

        self.send_qmp_message({
                "execute": "qmp_capabilities"
            }) 
       
        capabilities = self.receive_qmp_message()
        if(capabilities['return'] != { }):
            self.destroy()
            return

    def receive_qmp_message(self):
        """
        Get a QMP message from QEMU
        
        Returns a json object (resp) or None
        """
        buffer = b""

        while True:
            data = self.sock.recv(4096)
            
            # Socket closed
            if not data:
                break

            buffer += data
            try:
                return json.loads(buffer.decode("utf-8"))

            # Not a full json object yet
            except json.JSONDecodeError:
                pass
       
        return None

    def send_qmp_message(self, qmp_msg):
        """
        Send a QMP message to the socket
        """
        msg = json.dumps(qmp_msg)
        self.sock.send(msg.encode("utf-8"))
    
    def execute_qmp_command(self, qmp_msg):
        """
        Send QMP message and await a response
        """
        self.send_qmp_message(qmp_msg)
        return self.receive_qmp_message()

    def destroy(self):
        self.sock.close()
        
