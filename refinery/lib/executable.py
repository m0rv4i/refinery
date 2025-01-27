#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module implements an abstraction layer executable loader for PE, ELF, and MachO files.
The provided interface is the same for all executables. It powers the following units:

- `refinery.vsnip`
- `refinery.vsect`
- `refinery.vaddr`
"""
from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple
from os import devnull as DEVNULL
from abc import ABC, abstractmethod
from enum import auto, IntEnum, Enum
from functools import lru_cache

from macholib.MachO import MachO
from pefile import PE as PEFile, SectionStructure, MACHINE_TYPE, DIRECTORY_ENTRY
from elftools.elf.elffile import ELFFile

from refinery.lib.structures import MemoryFile
from refinery.lib.types import INF, ByteStr

if TYPE_CHECKING:
    from typing import Callable, ParamSpec, TypeVar, Generator, Optional, Union, Iterable, List
    _T = TypeVar('_T')
    _P = ParamSpec('_P')


class ParsingFailure(ValueError):
    def __init__(self, kind):
        super().__init__(F'unable to parse input as {kind} file')


_MACHO_ARCHS = {
    1        : 'VAX',
    6        : 'MC680x0',
    7        : 'X86',
    16777223 : 'X86_64',
    10       : 'MC98000',
    11       : 'HPPA',
    12       : 'ARM',
    13       : 'MC88000',
    14       : 'SPARC',
    15       : 'I860',
    18       : 'POWERPC',
    16777234 : 'POWERPC64',
}


def align(alignment: int, value: int) -> int:
    if alignment >= 2:
        incomplete_chunk_count = value % alignment
        if incomplete_chunk_count > 0:
            value += alignment - incomplete_chunk_count
    return value


def exeroute(
    data           : bytearray,
    handler_elf    : Callable[_P, _T],
    handler_macho  : Callable[_P, _T],
    handler_pe     : Callable[_P, _T],
    *args,
    **kwargs
) -> _T:
    if data[:2] == B'MZ':
        try:
            parsed = PEFile(data=data, fast_load=True)
        except Exception as E:
            raise ParsingFailure('PE') from E
        else:
            return handler_pe(parsed, *args, **kwargs)
    if data[:4] == B'\x7FELF':
        try:
            parsed = ELFFile(MemoryFile(data))
        except Exception as E:
            raise ParsingFailure('ELF') from E
        else:
            return handler_elf(parsed, *args, **kwargs)
    if set(data[:4]) <= {0xFE, 0xED, 0xFA, 0xCE, 0xCF}:
        class InMemoryMachO(MachO):
            def __init__(self): super().__init__(DEVNULL)
            def load(self, _): return super().load(MemoryFile(data))
        try:
            parsed = InMemoryMachO()
            assert parsed.headers
        except Exception as E:
            raise ParsingFailure('MachO') from E
        else:
            return handler_macho(parsed, *args, **kwargs)
    raise ValueError('Unknown executable format')


class Range(NamedTuple):
    lower: int
    upper: int

    def range(self):
        return range(self.lower, self.upper + 1)

    def __len__(self):
        return self.upper - self.lower

    def __contains__(self, addr: int):
        return self.lower <= addr <= self.upper


class BoxedOffset(NamedTuple):
    box: Range
    position: int


class Location(NamedTuple):
    physical: BoxedOffset
    virtual: BoxedOffset


class Arch(IntEnum):
    X8632 = auto()
    X8664 = auto()
    ARM32 = auto()
    ARM64 = auto()
    MIPS16 = auto()
    MIPS32 = auto()
    MIPS64 = auto()
    PPC32 = auto()
    PPC64 = auto()
    SPARC = auto()
    SPARCV9 = auto()


class LT(str, Enum):
    PHYSICAL = 'offset'
    VIRTUAL = 'address'


class Section(NamedTuple):
    name: str
    physical: Range
    virtual: Range


class Segment(NamedTuple):
    physical: Range
    virtual: Range
    sections: Optional[List[Section]]
    name: Optional[str] = None

    def as_section(self) -> Section:
        if self.name is None:
            raise ValueError('Unable to convert nameless segment to section.')
        return Section(self.name, self.physical, self.virtual)


class CompartmentNotFound(LookupError):
    def __init__(self, lt: LT, location: int):
        super().__init__(F'Unable to find a segment that contains the {lt.value} 0x{location:X}.')
        self.location_type = lt
        self.location = location


class Executable(ABC):

    _data: ByteStr
    _head: Union[PEFile, ELFFile, MachO]
    _base: Optional[int]

    @classmethod
    def Load(self, data: ByteStr, base: Optional[int] = None) -> Executable:
        return exeroute(
            data,
            ExecutableELF,
            ExecutableMachO,
            ExecutablePE,
            data,
            base,
        )

    def __init__(self, head: Union[PEFile, ELFFile, MachO], data: ByteStr, base: Optional[int] = None):
        self._data = data
        self._head = head
        self._base = base

    @staticmethod
    def _ascii(string: Union[str, ByteStr]) -> str:
        if isinstance(string, str):
            return string
        for k, b in enumerate(string):
            if b == 0:
                string = string[:k]
                break
        return string.decode('latin-1')

    def _rebase_usr_to_img(self, addr: int) -> int:
        return addr - self.base + self.image_defined_base()

    def _rebase_img_to_usr(self, addr: int) -> int:
        return addr - self.image_defined_base() + self.base

    @property
    def base(self):
        if self._base is None:
            return self.image_defined_base()
        return self._base

    def location_from_address(self, address: int) -> Location:
        return self.lookup_location(address, LT.VIRTUAL)

    def location_from_offset(self, offset: int) -> Location:
        return self.lookup_location(offset, LT.PHYSICAL)

    def image_defined_size(self) -> int:
        size = 0
        for segment in self.segments():
            size = max(size, segment.physical.upper)
        for section in self.sections():
            size = max(size, section.physical.upper)
        return size

    def image_defined_address_space(self) -> Range:
        upper = 0
        lower = INF
        for segment in self.segments():
            upper = max(upper, segment.virtual.upper)
            lower = min(lower, segment.virtual.lower)
        for section in self.sections():
            upper = max(upper, section.virtual.upper)
            lower = min(lower, section.virtual.lower)
        if upper < lower:
            raise RuntimeError(F'The computed address space upper bound 0x{upper:X} is less than the computed lower bound 0x{lower:X}.')
        return Range(lower, upper)

    def lookup_location(self, location: int, lt: LT) -> Location:
        for segment in self.segments():
            if lt is LT.PHYSICAL and location in segment.physical:
                return Location(
                    BoxedOffset(segment.physical, location),
                    BoxedOffset(segment.virtual, segment.virtual.lower + location - segment.physical.lower)
                )
            if lt is LT.VIRTUAL and location in segment.virtual:
                return Location(
                    BoxedOffset(segment.physical, segment.physical.lower + location - segment.virtual.lower),
                    BoxedOffset(segment.virtual, location)
                )
        else:
            raise CompartmentNotFound(lt, location)

    @abstractmethod
    def image_defined_base(self) -> int:
        ...

    @abstractmethod
    def arch(self) -> Arch:
        ...

    @abstractmethod
    def sections(self) -> Generator[Section, None, None]:
        ...

    @abstractmethod
    def segments(self, populate_sections=False) -> Generator[Segment, None, None]:
        ...


class ExecutablePE(Executable):

    _head: PEFile

    def image_defined_base(self) -> int:
        return self._head.OPTIONAL_HEADER.ImageBase

    def image_defined_size(self, overlay=True, sections=True, directories=True, certificate=True, memdump=False) -> int:
        """
        This fuction determines the size of a PE file, optionally taking into account the
        pefile module overlay computation, section information, data directory information,
        and certificate entries.
        """
        pe = self._head

        overlay_value = overlay and pe.get_overlay_data_start_offset() or 0
        sections_value = sections and super().image_defined_size() or 0
        memdump_value = memdump and self.image_defined_address_space().upper or 0
        cert_entry = pe.OPTIONAL_HEADER.DATA_DIRECTORY[DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_SECURITY']]

        if directories:
            directories_value = max((
                pe.get_offset_from_rva(d.VirtualAddress) + d.Size
                for d in pe.OPTIONAL_HEADER.DATA_DIRECTORY
                if d.name != 'IMAGE_DIRECTORY_ENTRY_SECURITY'
            ), default=0)
            if certificate:
                # The certificate overlay is given as a file offset
                # rather than a virtual address.
                cert_value = cert_entry.VirtualAddress + cert_entry.Size
            else:
                cert_value = 0
            directories_value = max(directories_value, cert_value)
        else:
            directories_value = 0

        return max(
            overlay_value,
            sections_value,
            directories_value,
            memdump_value
        )

    def sections(self) -> Generator[Section, None, None]:
        sections: Iterable[SectionStructure] = iter(self._head.sections)
        ib = self.image_defined_base()
        for section in sections:
            p_lower = section.PointerToRawData
            p_upper = p_lower + section.SizeOfRawData
            v_lower = section.VirtualAddress + ib
            v_lower = self._rebase_img_to_usr(v_lower)
            v_upper = v_lower + section.Misc_VirtualSize
            yield Section(
                self._ascii(section.Name),
                Range(p_lower, p_upper),
                Range(v_lower, v_upper),
            )

    def segments(self, populate_sections=False) -> Generator[Segment, None, None]:
        for section in self.sections():
            yield Segment(
                section.physical,
                section.virtual,
                [section] if populate_sections else None
            )

    def arch(self) -> Arch:
        arch = self._head.FILE_HEADER.Machine
        arch = MACHINE_TYPE[arch]
        try:
            return {
                'IMAGE_FILE_MACHINE_I386'   : Arch.X8632,
                'IMAGE_FILE_MACHINE_AMD64'  : Arch.X8664,
                'IMAGE_FILE_MACHINE_ARM'    : Arch.ARM32,
                'IMAGE_FILE_MACHINE_THUMB'  : Arch.ARM32,
                'IMAGE_FILE_MACHINE_ARMNT'  : Arch.ARM64,
                'IMAGE_FILE_MACHINE_MIPS16' : Arch.MIPS16,
            }[arch]
        except KeyError:
            raise LookupError(F'Unsupported architecture: {arch}')


class ExecutableELF(Executable):

    _head: ELFFile

    @lru_cache(maxsize=1)
    def image_defined_base(self) -> int:
        return min(self._pt_load())

    @lru_cache(maxsize=1)
    def _pt_load(self):
        PT_LOAD = {}
        if not self._head.num_segments():
            raise LookupError('The elftools parser did not find any segments in this file.')
        for segment in self._head.iter_segments():
            if segment.header.p_type == 'PT_LOAD':
                PT_LOAD[segment.header.p_vaddr] = segment
        if not PT_LOAD:
            raise LookupError('Could not find any PT_LOAD segment.')
        return PT_LOAD

    def _convert_section(self, section) -> Section:
        p_lower = section['sh_offset']
        v_lower = section['sh_addr']
        v_lower = self._rebase_img_to_usr(v_lower)
        v_upper = v_lower + align(section['sh_addralign'], section.data_size)
        p_upper = p_lower + section.data_size
        return Section(
            self._ascii(section.name),
            Range(p_lower, p_upper),
            Range(v_lower, v_upper),
        )

    def sections(self) -> Generator[Section, None, None]:
        for section in self._head.iter_sections():
            if section.is_null():
                continue
            yield self._convert_section(section)

    def segments(self, populate_sections=False) -> Generator[Segment, None, None]:
        for segment in self._head.iter_segments():
            header = segment.header
            p_lower = header.p_offset
            v_lower = header.p_vaddr
            v_lower = self._rebase_usr_to_img(v_lower)
            p_upper = p_lower + header.p_filesz
            v_upper = v_lower + header.p_memsz
            if not populate_sections:
                sections = None
            else:
                sections = [
                    self._convert_section(section)
                    for section in self._head.iter_sections()
                    if segment.section_in_segment(section)
                ]
            yield Segment(Range(p_lower, p_upper), Range(v_lower, v_upper), sections)

    def arch(self) -> Arch:
        arch = self._head.header['e_machine']
        try:
            return {
                'EM_SPARC'   : Arch.SPARC,
                'EM_SPARCV9' : Arch.SPARCV9,
                'EM_386'     : Arch.X8632,
                'EM_X86_64'  : Arch.X8664,
                'EM_MIPS'    : Arch.MIPS32,
                'EM_PPC'     : Arch.PPC32,
                'EM_PPC64'   : Arch.PPC64,
                'EM_ARM'     : Arch.ARM32,
            }[arch]
        except KeyError:
            raise LookupError(F'Unsupported architecture: {arch}')


class ExecutableMachO(Executable):

    _head: MachO

    @lru_cache(maxsize=1)
    def image_defined_base(self) -> int:
        return min(seg.vmaddr for seg, _ in self._macho_segments() if seg.vmaddr > 0)

    def _macho_segments(self):
        for header in self._head.headers:
            for header, segment, sections in header.commands:
                if not header.get_cmd_name().startswith('LC_SEGMENT'):
                    continue
                if segment.filesize <= 0:
                    continue
                yield segment, sections

    def segments(self, populate_sections=False) -> Generator[Segment, None, None]:
        for segment, sections in self._macho_segments():
            v_lower = segment.vmaddr
            v_lower = self._rebase_img_to_usr(v_lower)
            p_lower = segment.fileoff
            v_upper = v_lower + segment.vmsize
            p_upper = p_lower + segment.filesize
            segment_name = self._ascii(segment.segname)
            if not populate_sections:
                sections = None
            else:
                sections = [
                    self._convert_section(section, segment_name)
                    for section in sections
                ]
            yield Segment(
                Range(p_lower, p_upper),
                Range(v_lower, v_upper),
                sections,
                segment_name
            )

    def sections(self) -> Generator[Section, None, None]:
        for segment in self.segments(populate_sections=True):
            yield segment.as_section()
            yield from segment.sections

    def _convert_section(self, section, segment: str) -> Section:
        name = self._ascii(section.sectname)
        p_lower = section.offset
        v_lower = section.addr
        v_lower = self._rebase_img_to_usr(v_lower)
        p_upper = p_lower + section.size
        v_upper = v_lower + align(section.align, section.size)
        return Section(
            F'{segment}/{name}',
            Range(p_lower, p_upper),
            Range(v_lower, v_upper),
        )

    def arch(self) -> Arch:
        cputype = self._head.headers[0].header.cputype
        try:
            arch = _MACHO_ARCHS[cputype]
        except KeyError:
            arch = F'UNKNOWN(0x{cputype:X})'
        try:
            return {
                'X86'       : Arch.X8632,
                'X86_64'    : Arch.X8664,
                'ARM'       : Arch.ARM32,
                'SPARC'     : Arch.SPARC,
                'POWERPC'   : Arch.PPC32,
                'POWERPC64' : Arch.PPC64,
            }[arch]
        except KeyError:
            raise LookupError(F'Unsupported architecture: {arch}')
