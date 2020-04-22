from ...binary import BinaryReader, BinaryWriter
from ...binary.types import UInt8, UInt16
from .hkcdStaticTreeCodec3Axis import hkcdStaticTreeCodec3Axis

if False:
    from ...hkfile import HKFile
    from ...container.util.hkobject import HKObject


class hkcdStaticTreeCodec3Axis6(hkcdStaticTreeCodec3Axis):
    hiData: UInt8
    loData: UInt16

    def deserialize(self, hkFile: "HKFile", br: BinaryReader, obj: "HKObject"):
        super().deserialize(hkFile, br, obj)

        self.hiData = br.read_uint8()
        self.loData = br.read_uint16()

    def serialize(self, hkFile: "HKFile", bw: BinaryWriter, obj: "HKObject"):
        super().serialize(hkFile, bw, obj)

        bw.write_uint8(UInt8(self.hiData))
        bw.write_uint16(UInt16(self.loData))

    def asdict(self):
        d = super().asdict()
        d.update(
            {"hiData": self.hiData, "loData": self.loData,}
        )
        return d

    @classmethod
    def fromdict(cls, d: dict):
        inst = cls()
        inst.__dict__.update(super().fromdict(d).__dict__)

        inst.hiData = d["hiData"]
        inst.loData = d["loData"]

        return inst
