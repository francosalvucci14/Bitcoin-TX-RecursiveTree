from io import BytesIO
from Utils import helpers

class Script:
    def __init__(self, cmds):
        self.cmds = cmds

    def __str__(self):
        return " ".join([str(x) for x in self.cmds])

    @classmethod
    def parse(cls, bs):
        r = BytesIO(bs)
        script_len = len(bs)
        count = 0
        cmds = []
        while count < script_len:
            first = int.from_bytes(r.read(1), "little")
            count += 1
            if 1 <= first <= 75:
                data = r.read(first)
                cmds.append(data.hex())
                count += first
            elif first == 76:
                data_len = int.from_bytes(r.read(1), "little")
                cmds.append(r.read(data_len).hex())
                count += data_len + 1
            elif first == 77:
                data_len = int.from_bytes(r.read(2), "little")
                cmds.append(r.read(data_len).hex())
                count += data_len + 2
            elif first == 78:
                data_len = int.from_bytes(r.read(4), "little")
                cmds.append(r.read(data_len).hex())
                count += data_len + 4
            else:
                cmds.append(helpers.OPCODES.get(first, f'op_{first}'))
        return cls(cmds)

    @classmethod
    def from_witness(cls, witness_stack):
        return cls([w.hex() for w in witness_stack])

    def get_type(self):
        if len(self.cmds) == 0:
            return "No Script"
        if self.cmds[0] == "op_dup" and self.cmds[1] == "op_hash160" and \
           self.cmds[-2] == "op_equalverify" and self.cmds[-1] == "op_checksig":
            return "P2PKH"
        elif self.cmds[0] == "op_hash160" and self.cmds[-1] == "op_equal":
            return "P2SH"
        elif self.cmds[0] == "op_return":
            return "OP_RETURN"
        elif self.cmds[1:] and self.cmds[-1] == "op_checksig":
            return "P2PK"
        elif self.cmds[0] == "op_0" and len(self.cmds) == 2 and len(bytes.fromhex(self.cmds[1])) == 20:
            return "P2WPKH"
        elif self.cmds[0] == "op_0" and len(self.cmds) == 2 and len(bytes.fromhex(self.cmds[1])) == 32:
            return "P2WSH"
        return "Unknown Script"

if __name__ == "__main__":
    # hexscript proviene da tx1, output 2
    hexscript = "410411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3ac"
    bs = bytes.fromhex(hexscript)
    script = Script.parse(bs)
    print(script)
    print("Type of script:", script.get_type())
