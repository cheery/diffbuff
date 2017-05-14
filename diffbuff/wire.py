"""
    diffbuff.wire
    ~~~~~~~~~~~~~

    Wire format for diff buffers

    Requires testing, examples
"""
def decode(data, offset):
    val, offset = decode_leb128(data, offset)
    tag = val >> 4
    kind = val & 15

def decode_many(kind, data, offset):
    count, offset = decode_leb128(data, offset)
    top = offset + count
    output = []
    while offset < top:
        item, offset = decode_payload(kind, data, offset)
        output.append(item)
    assert offset == top, "stream corruption"
    return output

def decode_payload(kind, data, offset):
    if kind == INT:
        return decode_sleb128(data, offset)
    elif kind == PINT:
        return decode_many(INT, data, offset)
    elif kind == STR:
        length, offset = decode_leb128(data, offset)
        val = data[offset:offset+length]
        return val.decode('utf-8'), (offset + length)
    elif kind == PSTR:
        return decode_many(STR, data, offset)
    elif kind == MSG:
        return decode_many(UNION, data, offset)
    elif kind == PMSG:
        return decode_many(MSG, data, offset)
    elif kind == DATA:
        length, offset = decode_leb128(data, offset)
        return data[offset:offset+length], (offset + length)
    elif kind == PDATA:
        return decode_many(DATA, data, offset)
    elif kind == B32:
        return data[offset:offset+4], (offset + 4)
    elif kind == B64:
        return data[offset:offset+8], (offset + 8)
    elif kind == UNION:
        return decode(data, offset)
    elif kind == PUNION:
        return decode_many(UNION, data, offset)
    elif kind == SUNION:
        output, offset = decode_many(UNION, data, offset)
        return set(output), offset
    elif kind == MUNION:
        raw_dict, offset = decode_many(UNION, data, offset)
        assert len(raw_dict) & 1 == 0, "stream corruption"
        it = iter(raw_dict)
        output = dict()
        for i in it:
            output[i] = it.next()
        return output, offset
    elif kind == META_DATA:
        return decode_payload(DATA, data, offset)
    elif kind == META_MSG:
        return decode_payload(MSG, data, offset)
    else:
        assert False, kind

def encode(node):
    output = encode_leb128(node.tag << 4 | node.kind)
    output.extend(encode_payload(node.kind, node.value))
    return output

def encode_many(kind, values):
    output = []
    for value in values:
        output.extend(encode_payload(kind, value))
    return output

def encode_payload(kind, value):
    if kind == INT:
        return encode_sleb128(value)
    elif kind == PINT:
        return encode_many(INT, value)
    elif kind == STR:
        value = value.encode('utf-8')
        output = encode_leb128(len(value))
        output.extend(ord(c) for c in value)
        return output
    elif kind == PSTR:
        return encode_many(STR, value)
    elif kind == MSG:
        output = []
        for node in value:
            output.extend(encode(node))
        return encode_leb128(len(output)) + output
    elif kind == PMSG:
        return encode_many(MSG, value)
    elif kind == DATA:
        output = encode_leb128(len(value))
        output.extend(ord(c) for c in value)
        return output
    elif kind == PDATA:
        return encode_many(DATA, value)
    elif kind == B32:
        assert len(value) == 4, "B32 expects 4 bytes"
        return [ord(c) for c in value]
    elif kind == B64:
        assert len(value) == 8, "B64 expects 8 bytes"
        return [ord(c) for c in value]
    elif kind == UNION:
        return encode(value)
    elif kind == PUNION:
        return encode_many(UNION, value)
    elif kind == SUNION:
        return encode_many(UNION, value)
    elif kind == MUNION:
        return encode_many(UNION, flatten_dict(value))
    elif kind == META_DATA:
        return encode_payload(DATA, value)
    elif kind == META_MSG:
        return encode_payload(MSG, value)
    else:
        assert False, kind

def flatten_dict(value):
    for key, val in value.iteritems():
        yield key
        yield val

# http://en.wikipedia.org/wiki/Variable-length_quantity
def encode_leb128(value):
    output = [value & 0x7F]
    value >>= 7
    while value > 0:
        output.append(0x80 | (value & 0x7F))
        value >>= 7
    output.reverse()
    return output

def encode_sleb128(value):
    output = []
    more = true
    while more:
        byte = value & 0x7F
        value >>= 7
        if ((value ==  0 and byte & 0x40 == 0) or
           (value == -1 and byte & 0x40 != 0)):
           more = false
        output.append(byte | 0x80)
    output[0] &= 0x7F
    output.reverse()
    return output

def decode_leb128(data, offset):
    byte = data[offset]
    offset += 1
    value = byte & 0x7F
    while byte > 0x7F:
        byte = data[offset]
        offset += 1
        value = (value << 7) | (byte & 0x7F)
    return value, offset
    
def decode_sleb128(data, offset):
    byte = data[offset]
    offset += 1
    if byte & 0x40 != 0:
        value = (-1) << 7
    else:
        value = 0
    while byte & 0x80 != 0:
        value = (value | (byte & 0x7F)) << 7
        byte = data[offset]
        offset += 1
        value |= byte
    return value, offset

class Node(object):
    def init(self, tag, kind, value):
        self.tag = tag
        self.kind = kind
        self.value = value

INT   = 0
PINT  = 1
STR   = 2
PSTR  = 3
MSG   = 4
PMSG  = 5
DATA  = 6
PDATA = 7
B32   = 8
B64   = 9
UNION  = 0xA
PUNION = 0xB
SUNION = 0xC
MUNION = 0xD
META_DATA = 0xE
META_MSG  = 0xF
