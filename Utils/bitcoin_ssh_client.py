# bitcoin_ssh_client.py
import paramiko

class BitcoinSSHClient:
    def __init__(self, host, user, key_filename=None):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            hostname=host,
            username=user,
            key_filename=key_filename  # puoi anche usare password= se necessario
        )

    def run(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if stderr.channel.recv_exit_status() != 0:
            raise RuntimeError(f"Errore SSH:\n{error}")
        return output

    def close(self):
        self.client.close()
