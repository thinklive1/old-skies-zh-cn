"""Bounded SCOM parsing and minimal pre-wrap translation detours.

The original string pool, globals, exports, and existing fixups remain intact.
Existing code cells change only at two recorded source-line instructions.
No whole-game serializer is used.
"""
import struct


def parse(data, offset=0):
    start = offset
    if data[offset:offset+4] != b'SCOM':
        raise ValueError('SCOM signature mismatch')
    offset += 4
    def integer():
        nonlocal offset
        if offset + 4 > len(data): raise ValueError('Truncated SCOM integer')
        result = struct.unpack_from('<i', data, offset)[0]; offset += 4
        return result
    def take(size):
        nonlocal offset
        if size < 0 or offset + size > len(data): raise ValueError('Truncated SCOM payload')
        result = data[offset:offset+size]; offset += size
        return result
    def cstring():
        nonlocal offset
        end = data.find(b'\0', offset)
        if end < 0 or end-offset > 300: raise ValueError('Invalid SCOM name')
        value = data[offset:end].decode('ascii'); offset = end+1
        return value
    version = integer()
    if version != 90: raise ValueError('Unsupported SCOM version')
    gsize, count, ssize = integer(), integer(), integer()
    if count < 0: raise ValueError('Negative code size')
    globals_ = take(gsize)
    code = list(struct.unpack('<'+'i'*count, take(count*4)))
    strings = take(ssize)
    fix_count = integer(); types = take(fix_count)
    positions = [integer() for _ in range(fix_count)]
    if any(p < 0 or p >= count for p in positions): raise ValueError('Fixup outside code')
    imports = [cstring() for _ in range(integer())]
    tail_start = offset
    exports = []
    for _ in range(integer()):
        name = cstring(); pointer = integer() & 0xffffffff
        exports.append(dict(name=name, type=pointer>>24, pointer=pointer & 0xffffff))
    sections = []
    for _ in range(integer()): sections.append(dict(name=cstring(), offset=integer()))
    if take(4) != b'\xfe\xca\xef\xbe': raise ValueError('SCOM trailer mismatch')
    return dict(version=version, globals=globals_, code=code, strings=strings,
                fixups=list(zip(types, positions)), imports=imports,
                exports=exports, sections=sections, tail=data[tail_start:offset],
                offset=start, end=offset)


def serialize(script):
    code = script['code']; fixups = script['fixups']
    result = b'SCOM' + struct.pack('<4i', script['version'], len(script['globals']),
                                    len(code), len(script['strings']))
    result += script['globals'] + struct.pack('<'+'i'*len(code), *code) + script['strings']
    result += struct.pack('<i', len(fixups)) + bytes(t for t, _ in fixups)
    result += b''.join(struct.pack('<i', p) for _, p in fixups)
    result += struct.pack('<i', len(script['imports']))
    result += b''.join(s.encode('ascii')+b'\0' for s in script['imports'])
    return result + script['tail']


def translate_scrollers(blob, instruction_table):
    """Translate and wrap selected mail/news in measured Unicode lines."""
    from pixel_wrap import patch
    return patch(blob, instruction_table)
