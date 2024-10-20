
import struct


class StreamWrite:
    def __init__(self, fileName):
        self.stream = open(fileName, 'wb')

    def write_char(self, value):
        res = value.encode('utf-8') 
        self.stream.write(struct.pack('c', res))

    def write_byte(self, value):
        self.stream.write(struct.pack('b', value))

    def write_int(self, value):
        self.stream.write(struct.pack('i', value))

    def write_long(self, value):
        self.stream.write(struct.pack('q', value))

    def write_short(self, value):
        self.stream.write(struct.pack('h', value))

    def write_float(self, value):
        self.stream.write(struct.pack('f', value))

    def write_double(self, value):
        self.stream.write(struct.pack('d', value))

    def write_string(self, value):
        s = value.encode('utf-8') 
        self.write_int(len(s))  
        self.stream.write(s)  

    def write_UTFstring(self, value):
        s = value.encode('utf-8')
        self.stream.write(s) 
        self.stream.write(b'\x00')

    def close(self):
        self.stream.close()


class StreamRead:
    def __init__(self, fileName):
        self.stream = open(fileName, 'rb')

    def read_char(self):
        return struct.unpack('c', self.stream.read(1))[0].decode('utf-8')

    def read_byte(self):
        return struct.unpack('b', self.stream.read(1))[0]

    def read_int(self):
        return struct.unpack('i', self.stream.read(4))[0]

    def read_long(self):
        return struct.unpack('q', self.stream.read(8))[0]

    def read_short(self):
        return struct.unpack('h', self.stream.read(2))[0]

    def read_float(self):
        return struct.unpack('f', self.stream.read(4))[0]

    def read_double(self):
        return struct.unpack('d', self.stream.read(8))[0]

    def read_string(self):
        length = self.read_int()
        string_bytes = self.stream.read(length)
        return string_bytes.decode('utf-8')

    def read_UTFstring(self):
        string_bytes = bytearray()
        while True:
            char = self.stream.read(1)
            if char == b'\x00':
                break
            string_bytes.extend(char)
        return string_bytes.decode('utf-8')

    def close(self):
        self.stream.close()