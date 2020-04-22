from typing import List

from ..binary import BinaryReader, BinaryWriter
from ..binary.types import UInt32
from ..container.util.globalreference import GlobalReference
from ..container.util.localfixup import LocalFixup
from .base import HKBaseClass
from .common.hkReferencedObject import hkReferencedObject
from .hkpPhysicsSystem import hkpPhysicsSystem

if False:
    from ..hkfile import HKFile
    from ..container.util.hkobject import HKObject


class hkpPhysicsData(HKBaseClass, hkReferencedObject):
    """Physics data container, contains references
    to world info, physics systems
    """

    # worldCinfo: hkpWorldCinfo  # Doesn't seem to be used in BotW (?)
    systems: List[hkpPhysicsSystem]

    def __init__(self):
        HKBaseClass.__init__(self)

        self.systems = []

    def deserialize(self, hkFile: "HKFile", br: BinaryReader, obj: "HKObject"):
        HKBaseClass.deserialize(self, hkFile, br, obj)
        hkReferencedObject.deserialize(self, hkFile, br, obj)

        ###

        if hkFile.header.padding_option:
            br.align_to(16)

        # worldCinfo_offset = br.tell()
        hkFile._assert_pointer(br)

        # systemCount_offset = br.tell()
        hkFile._assert_pointer(br)
        systemCount = hkFile._read_counter(br)
        br.align_to(16)

        # systems_offset = br.read()
        for gr in obj.global_references:
            if gr.src_rel_offset == br.tell():
                system = hkpPhysicsSystem()
                self.systems.append(system)

                system.deserialize(
                    hkFile,
                    BinaryReader(
                        initial_bytes=gr.dst_obj.bytes,
                        big_endian=hkFile.header.endian == 0,
                    ),
                    gr.dst_obj,
                )

                hkFile.data.objects.remove(gr.dst_obj)

                hkFile._assert_pointer(br)
        br.align_to(16)

        obj.local_fixups.clear()
        obj.global_references.clear()

    def serialize(self, hkFile: "HKFile", bw: BinaryWriter, obj: "HKObject"):
        HKBaseClass.assign_class(self, hkFile, obj)
        hkReferencedObject.serialize(self, hkFile, bw, obj)

        ###

        if hkFile.header.padding_option:
            bw.align_to(16)

        # worldCinfo_offset = bw.tell()
        hkFile._write_empty_pointer(bw)

        hkFile._write_empty_pointer(bw)
        hkFile._write_counter(bw, UInt32(len(self.systems)))
        bw.align_to(16)

        for system in self.systems:
            gr = GlobalReference()
            gr.src_obj = obj
            gr.src_rel_offset = bw.tell()
            # gr.dst_obj = HKObject()
            obj.global_references.append(gr)

            hkFile._write_empty_pointer(bw)
            hkFile.data.objects.append(gr.dst_obj)

            system.serialize(
                hkFile, BinaryWriter(big_endian=hkFile.header.endian == 0), gr.dst_obj
            )

        bw.align_to(16)

        HKBaseClass.serialize(self, hkFile, bw, obj)

    def asdict(self):
        d = super().asdict()
        d.update(hkReferencedObject.asdict(self))
        d.update(
            {
                # "worldCinfo": self.worldCinfo,
                "systems": [ps.asdict() for ps in self.systems],
            }
        )

        return d

    @classmethod
    def fromdict(cls, d: dict):
        inst = cls()
        # inst.worldCinfo = d['worldCinfo']
        inst.systems = [hkpPhysicsSystem.fromdict(ps) for ps in d["systems"]]
        inst.__dict__.update(HKBaseClass.fromdict(d).__dict__)
        inst.__dict__.update(hkReferencedObject.fromdict(d).__dict__)

        return inst

    def __repr__(self):
        return f"{self.__class__.__name__}({self.systems})"
