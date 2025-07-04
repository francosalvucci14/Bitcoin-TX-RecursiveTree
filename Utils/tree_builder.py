from transaction_total import SegWitTx, TX
from Utils.helpers import get_tx_tot, color_print


class TreeBuilder:

    @classmethod
    def buildTree(cls,root_tx,height,ssh=False,testnet=False,client=None,log_func=None,gui=False):
        root = Node(root_tx)
        if root_tx.isCoinbase():
            return root
        if height > 0:
            for txh_in in root_tx.getInputs():
                hex_tx = (txh_in.prevtx).hex()
                try:
                    _tx_in = get_tx_tot(
                        hex_tx, ssh, client, testnet, log_func=log_func, gui=gui
                    )
                except Exception as e:
                    color_print(
                        f"[ERROR] Error while retrieving transaction: {e}",
                        "red",
                    )
                    continue
                if SegWitTx.isSegWit(_tx_in):
                    tx = SegWitTx.parse(_tx_in, hex_tx)
                else:
                    tx = TX.parse(_tx_in, hex_tx)
                child = TreeBuilder.buildTree(
                    tx, height - 1, ssh, testnet, client, log_func=log_func, gui=gui
                )
                root.addChild(child)
        return root


class Node:

    def __init__(self, root):
        self.root = root
        self.children = []

    def addChild(self, node):
        self.children.append(node)


if __name__ == "__main__":
    tx_hex = get_tx_tot(
        "13e3167d46334600b59a5aa286dd02147ac33e64bfc2e188e1f0c0a442182584"
    )
    tx_in = TX.parse(
        tx_hex, "13e3167d46334600b59a5aa286dd02147ac33e64bfc2e188e1f0c0a442182584"
    )
    tree = TreeBuilder.buildTree(tx_in, 2)
