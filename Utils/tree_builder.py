from transaction_total import SegWitTx, TX
from Utils.helpers import get_tx, color_print, get_tx_testnet, get_tx_ssh

class TreeBuilder:

    @classmethod
    def buildTree(cls, root_tx, height=float("inf")):
        root = Node(root_tx)
        if root_tx.isCoinbase():
            return root
        if height > 0:
            for txh_in in root_tx.getInputs():
                hex_tx = (txh_in.prevtx).hex()
                try:
                    _tx_in = get_tx(hex_tx)
                except Exception as e:
                    color_print(
                        f"[ERROR] Errore durante il recupero della transazione: {e}",
                        "red",
                    )
                    continue
                if SegWitTx.isSegWit(_tx_in):
                    tx = SegWitTx.parse(_tx_in, hex_tx)
                else:
                    tx = TX.parse(_tx_in, hex_tx)
                child = TreeBuilder.buildTree(tx, height - 1)
                root.addChild(child)
        return root

    @classmethod
    def buildTreeSSH(cls, root_tx, client, height=float("inf")):
        root = Node(root_tx)
        if root_tx.isCoinbase():
            return root
        if height > 0:
            for txh_in in root_tx.getInputs():
                hex_tx = (txh_in.prevtx).hex()
                try:
                    _tx_in = get_tx_ssh(hex_tx, client)
                except Exception as e:
                    color_print(
                        f"[ERROR] Errore durante il recupero della transazione: {e}",
                        "red",
                    )
                    continue
                if SegWitTx.isSegWit(_tx_in):
                    tx = SegWitTx.parse(_tx_in, hex_tx)
                else:
                    tx = TX.parse(_tx_in, hex_tx)
                child = TreeBuilder.buildTreeSSH(tx, client, height - 1)
                root.addChild(child)
        return root

    @classmethod
    def buildTreeTESTNET(cls, root_tx, height=float("inf")):
        root = Node(root_tx)
        if root_tx.isCoinbase():
            return root
        if height > 0:
            for txh_in in root_tx.getInputs():
                hex_tx = (txh_in.prevtx).hex()
                try:
                    _tx_in = get_tx_testnet(hex_tx)
                except Exception as e:
                    color_print(
                        f"[ERROR] Errore durante il recupero della transazione: {e}",
                        "red",
                    )
                    continue
                if SegWitTx.isSegWit(_tx_in):
                    tx = SegWitTx.parse(_tx_in, hex_tx)
                else:
                    tx = TX.parse(_tx_in, hex_tx)
                child = TreeBuilder.buildTreeTESTNET(tx, height - 1)
                root.addChild(child)
        return root



class Node:

    def __init__(self, root):
        self.root = root
        self.children = []

    def addChild(self, node):
        self.children.append(node)


if __name__ == "__main__":
    tx_hex = get_tx("13e3167d46334600b59a5aa286dd02147ac33e64bfc2e188e1f0c0a442182584")
    if TX.isSegWit(tx_hex):
        tx_in = TX.parse(
            tx_hex,
            "13e3167d46334600b59a5aa286dd02147ac33e64bfc2e188e1f0c0a442182584",
            True,
        )
    else:
        tx_in = TX.parse(
            tx_hex, "13e3167d46334600b59a5aa286dd02147ac33e64bfc2e188e1f0c0a442182584"
        )
    tree = TreeBuilder.buildTree(tx_in, 2)
    TreeBuilder.visualize(tree)
