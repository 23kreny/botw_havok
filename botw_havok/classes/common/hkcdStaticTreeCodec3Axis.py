from typing import List

from ...binary import BinaryReader, BinaryWriter
from ...binary.types import UInt8
from .hkObject import hkObject

if False:
    from ...hkfile import HKFile
    from ...container.util.hkobject import HKObject


class hkcdStaticTreeCodec3Axis(hkObject):
    xyz: List[UInt8]

    def deserialize(self, hkFile: "HKFile", br: BinaryReader, obj: "HKObject"):
        self.xyz = [br.read_uint8() for _ in range(3)]

    def serialize(self, hkFile: "HKFile", bw: BinaryWriter, obj: "HKObject"):
        [bw.write_uint8(UInt8(num)) for num in self.xyz]

    def asdict(self):
        return {"xyz": self.xyz}

    @classmethod
    def fromdict(cls, d: dict):
        inst = cls()

        inst.xyz = d["xyz"]

        return inst
