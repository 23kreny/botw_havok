from typing import List, Union

from ...binary import BinaryReader, BinaryWriter
from ...binary.types import String, UInt32, UInt64
from ...container.util.localreference import LocalReference
from .hkMultiThreadCheck import hkMultiThreadCheck
from .hkpLinkedCollidable import hkpLinkedCollidable
from .hkReferencedObject import hkReferencedObject
from .hkSimpleProperty import hkSimpleProperty

if False:
    from ...hkfile import HKFile
    from ...container.util.hkobject import HKObject


class hkpWorldObject(hkReferencedObject):
    # world: None = None
    userData: Union[UInt32, UInt64]
    collidable: hkpLinkedCollidable
    multiThreadCheck: hkMultiThreadCheck

    name: String

    properties: List[hkSimpleProperty]

    def __init__(self):
        self.properties = []

    def deserialize(self, hkFile: "HKFile", br: BinaryReader, obj: "HKObject"):
        super().deserialize(hkFile, br, obj)

        if hkFile.header.padding_option:
            br.align_to(16)

        hkFile._assert_pointer(br)  # Empty 'world' pointer

        if hkFile.header.pointer_size == 8:
            self.userData = br.read_uint64()
        elif hkFile.header.pointer_size == 4:
            self.userData = br.read_uint32()
        else:
            raise NotImplementedError()

        # ----

        self.collidable = hkpLinkedCollidable()
        self.collidable.deserialize(hkFile, br, obj)

        self.multiThreadCheck = hkMultiThreadCheck()
        self.multiThreadCheck.deserialize(hkFile, br, obj)

        if hkFile.header.padding_option:
            br.align_to(16)

        namePointer_offset = br.tell()
        hkFile._assert_pointer(br)

        propertiesCount_offset = br.tell()
        hkFile._assert_pointer(br)
        propertiesCount = hkFile._read_counter(br)

        for lfu in obj.local_fixups:
            br.step_in(lfu.dst)
            if lfu.src == namePointer_offset:
                self.name = br.read_string()
            elif lfu.src == propertiesCount_offset:
                for _ in range(propertiesCount):
                    prop = hkSimpleProperty()
                    prop.deserialize(hkFile, br, obj)

                    self.properties.append(prop)
            br.step_out()

    def serialize(self, hkFile: "HKFile", bw: BinaryWriter, obj: "HKObject"):
        super().serialize(hkFile, bw, obj)

        ###

        if hkFile.header.padding_option:
            bw.align_to(16)

        hkFile._write_empty_pointer(bw)

        if hkFile.header.pointer_size == 8:
            bw.write_uint64(UInt64(self.userData))
        elif hkFile.header.pointer_size == 4:
            bw.write_uint32(UInt32(self.userData))
        else:
            raise NotImplementedError()

        # ----

        self.collidable.serialize(hkFile, bw, obj)
        self.multiThreadCheck.serialize(hkFile, bw, obj)
        if hkFile.header.padding_option:
            bw.align_to(16)

        obj.local_references.append(
            LocalReference(hkFile, bw, obj, bw.tell(), self.name)
        )
        hkFile._write_empty_pointer(bw)  # 'name' pointer

        obj.local_references.append(
            LocalReference(hkFile, bw, obj, bw.tell(), self.properties)
        )

    def asdict(self):
        d = super().asdict()
        d.update(
            {
                # "world": self.world,
                "userData": self.userData,
                "collidable": self.collidable.asdict(),
                "multiThreadCheck": self.multiThreadCheck.asdict(),
                "name": self.name,
            }
        )

        return d

    @classmethod
    def fromdict(cls, d: dict):
        inst = cls()
        inst.memSizeAndRefCount = d["memSizeAndRefCount"]
        # inst.world = d["world"]
        inst.userData = d["userData"]
        inst.collidable = hkpLinkedCollidable.fromdict(d["collidable"])
        inst.multiThreadCheck = hkMultiThreadCheck.fromdict(d["multiThreadCheck"])
        inst.name = d["name"]

        return inst
