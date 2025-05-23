import hashlib
from configparser import ConfigParser
import os
import requests
from io import BytesIO
import subprocess  # for SSH version


def color_print(text: str, color: str, **kwargs):
    colors = {
        "red": "\033[91m",
        "green": "\033[32m",
        "lightgreen": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
    }
    end = kwargs.get("end", "\n")
    print(f"{colors[color]}{text}\033[0m", end=end)


def get_tx(tx_id):
    color_print("[MEMPOOL] Recupero la transazione con id: " + tx_id, "cyan")
    url = "https://mempool.space/api/tx/" + tx_id + "/hex"
    r = requests.get(url)
    
    if r.status_code != 200:
        color_print("[ERROR] Transazione non trovata", "red")
    
    return BytesIO(bytes.fromhex(r.text))


def get_tx_testnet(tx_id):
    color_print("[MEMPOOL-TESTNET] Recupero la transazione con id: " + tx_id, "cyan")
    url = "https://mempool.space/testnet/api/tx/" + tx_id + "/hex"
    r = requests.get(url)
    
    if r.status_code != 200:
        color_print("[ERROR] Transazione non trovata", "red")
    
    return BytesIO(bytes.fromhex(r.text))


def get_tx_ssh(tx_id, client,cmd):
    color_print("[SSH] Recupero la transazione con id: " + tx_id, "cyan")

    # Comando bitcoin-cli
    cmd = f"/home/bitcoin-user/bin/bitcoin-cli getrawtransaction {tx_id}"

    try:
        tx_json = client.run(cmd)
    except subprocess.CalledProcessError as e:
        color_print(f"[ERROR] Errore durante l'esecuzione del comando SSH: {e}", "red")
        raise

    
    return BytesIO(bytes.fromhex(tx_json))


def opcodes(fname):

    config = ConfigParser()
    config.read(fname)
    
    return {int(config["OPCODES"][x], 16): x for x in config["OPCODES"]}


OPCODES = opcodes("Utils/opcodes.cfg")


def hash256(msg):
    return hashlib.sha256(hashlib.sha256(msg).digest()).digest()


def varint2int(bs):
    first = int.from_bytes(bs.read(1), "little")
    if first < 0xFD:  # <256
        return first
    elif first == 0xFD:  # = 253
        return int.from_bytes(bs.read(2), "little")
    elif first == 0xFE:  # = 254
        return int.from_bytes(bs.read(4), "little")
    return int.from_bytes(
        bs.read(8), "little"
    )  # = 255, qua solo se non va in nessuno dei casi precedenti


# Esercizio 1
def int2varint(i):
    if i < 0xFD:  # <256
        return i.to_bytes(1, "little")
    elif i <= 0xFFFF:  # = 253
        return b"\xfd" + i.to_bytes(2, "little")
    elif i <= 0xFFFFFFFF:  # = 254
        return b"\xfe" + i.to_bytes(4, "little")
    return b"\xff" + i.to_bytes(
        8, "little"
    )  # = 255, qua solo se non va in nessuno dei casi precedenti


def satoshi_to_btc(satoshi):
    return satoshi / 100_000_000


if __name__ == "__main__":
    # print(os.path.isfile("opcodes.cfg"))  # Deve stampare True
    # print(opcodes("opcodes.cfg"))
    """helpers.py"""
