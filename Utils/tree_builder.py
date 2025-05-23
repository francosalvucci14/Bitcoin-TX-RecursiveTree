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

    def visualize(self, level=0):
        print(" " * level + "Transaction Tree:")

        # Visualizza l'albero in modo ricorsivo con rami tipo |_ per i livelli
        def _visualize(node, prefix="", is_last=True, ancestors=[], level=0):
            branch = ""
            if level == 0 and prefix == "":
                branch = "ROOT:"
            else:
                for i, ancestor_last in enumerate(ancestors[:-1]):
                    branch += "   " if ancestor_last else "|  "
                branch += "`-- " if is_last else "|-- "
            if node.root.isCoinbase():
                color_print(branch + "[COINBASE]" + str(node.root.id), "red")
            else:
                print(branch + str(node.root.id))
            child_count = len(node.children)
            for idx, child in enumerate(node.children):
                _visualize(
                    child,
                    prefix,
                    idx == child_count - 1,
                    ancestors + [is_last],
                    level + 1,
                )

        _visualize(self, "", True, [], level)

    def save_tree(self, filename):
        with open(filename, "w") as f:

            def _save(node, level=0):
                if level == 0:
                    f.write("ROOT:")
                else:
                    f.write("| " + "--" * level)
                if node.root.isCoinbase():
                    f.write(" " * level + "[COINBASE]" + str(node.root.id) + "\n")
                else:
                    f.write(" " * level + str(node.root.id) + "\n")
                for child in node.children:
                    _save(child, level + 1)

            _save(self)


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
