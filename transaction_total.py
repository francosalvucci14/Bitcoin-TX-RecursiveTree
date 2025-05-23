from io import BytesIO
import json
from Utils.helpers import varint2int, satoshi_to_btc

from Utils.script import Script


class TX:

    def __init__(self, id, version, inputs, outputs, locktime):
        self.id = id
        self.version = version
        self.inputs = inputs
        self.outputs = outputs
        self.locktime = locktime

    @classmethod
    def parse(cls, bs, id):
        version = int.from_bytes(bs.read(4), "little")
        ninput = varint2int(bs)
        inputs = [TXIn.parse(bs) for _ in range(ninput)]
        num_outputs = varint2int(bs)
        outputs = [TXOut.parse(bs) for _ in range(num_outputs)]
        locktime = int.from_bytes(bs.read(4), "little")
        return cls(id, version, inputs, outputs, locktime)

    def getInputs(self):
        return self.inputs

    def __str__(self):
        out = {
            "version": self.version,
            "inputs": [json.loads(str(txin)) for txin in self.inputs],
            "outputs": [json.loads(str(txout)) for txout in self.outputs],
            "locktime": self.locktime,
        }
        return json.dumps(out, indent=4)

    def isCoinbase(self):
        if (
            len(self.inputs) == 1
            and self.inputs[0].prevtx == bytes(32)
            and self.inputs[0].prevtxidx == 0xFFFFFFFF
        ):
            return True
        return False


class SegWitTx(TX):

    def __init__(
        self, id, version, marker, flag, inputs, outputs, locktime, witness=None
    ):
        super().__init__(id, version, inputs, outputs, locktime)
        self.marker = marker  # 1 byte
        self.flag = flag  # 1 byte
        self.witness = witness or []

    def __str__(self):
        out = {
            "version": self.version,
            "inputs": [json.loads(str(txin)) for txin in self.inputs],
            "outputs": [json.loads(str(txout)) for txout in self.outputs],
            "witness": (
                [
                    {
                        "elements": [w.hex() for w in wit],
                        "type": Script.from_witness(wit).get_type(),
                    }
                    for wit in self.witness
                ]
                if self.witness
                else []
            ),
            "locktime": self.locktime,
        }
        return json.dumps(out, indent=4)

    @classmethod
    def parse(cls, r, id):
        version = int.from_bytes(r.read(4), "little")
        marker = r.read(1)
        flag = r.read(1)
        numin = varint2int(r)
        inputs = [TXIn.parse(r) for _ in range(numin)]
        numout = varint2int(r)
        outputs = [TXOut.parse(r) for _ in range(numout)]
        witness = []
        for _ in range(numin):
            n_stack = varint2int(r)
            stack = [r.read(varint2int(r)) for _ in range(n_stack)]
            witness.append(stack)
        locktime = int.from_bytes(r.read(4), "little")

        return cls(id, version, marker, flag, inputs, outputs, locktime, witness)

    # in input ho uno stream di byte di una transazione
    @classmethod
    def isSegWit(cls, r):
        r.seek(4)
        marker = r.read(1)
        flag = r.read(1)
        r.seek(0)

        if marker == b"\x00" and flag == b"\x01":
            return True
        return False


class TXIn:

    def __init__(self, prevtx, prevtxidx, scriptsig, script, sequence):
        self.prevtx = prevtx
        self.prevtxidx = prevtxidx
        self.scriptsig = scriptsig
        self.script = script
        self.sequence = sequence

    def __str__(self):
        out = {
            "prevtx": self.prevtx.hex(),
            "prevtxidx": self.prevtxidx,
            "scriptsig": self.script.cmds,
            "type": self.script.get_type(),
            "sequence": self.sequence,
        }
        return json.dumps(out, indent=4)

    @classmethod
    def parse(cls, bs):
        prevtx = bs.read(32)[::-1]
        prevtxidx = int.from_bytes(bs.read(4), "little")
        scriptsig_len = varint2int(bs)
        scriptsig = bs.read(scriptsig_len)
        script = Script.parse(scriptsig)
        sequence = int.from_bytes(bs.read(4), "little")
        return cls(prevtx, prevtxidx, scriptsig, script, sequence)


class TXOut:

    def __init__(self, value, scriptpk, script):
        self.value = value
        self.scriptpk = scriptpk
        self.script = script

    def __str__(self):
        out = {
            "value_btc": satoshi_to_btc(self.value),
            "scriptpk": self.script.cmds,
            "type": self.script.get_type(),
        }
        return json.dumps(out, indent=4)

    @classmethod
    def parse(cls, bs):
        value = int.from_bytes(bs.read(8), "little")
        scriptpk_len = varint2int(bs)
        scriptpk = bs.read(scriptpk_len)
        script = Script.parse(scriptpk)
        return cls(value, scriptpk, script)
