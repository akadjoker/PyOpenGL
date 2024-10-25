
import struct


class ByteStream:
    def __init__(self):
        self.stream = None
        self.m_size = 0


    def load(self, fileName):
        self.stream = open(fileName, 'rb')
        self.m_size = self.stream.seek(0, 2)
        self.stream.seek(0)
    
    def create(self, fileName):
        self.stream = open(fileName, 'wb')
        self.m_size = 0


    def eof(self):
        if self.stream is None:
            return True
        return self.stream.tell() == self.m_size
    def position(self):
        return self.stream.tell()
    
    def size(self):
        return self.m_size
    
    
    def seek(self, pos, whence=0):
        """
        whence:
            0: relative to the beginning of the stream
            1: relative to the current position
            2: relative to the end of the stream
        """
        self.stream.seek(pos, whence)

    def write(self, data):
        if self.stream is None:
            return
        self.stream.write(data)
    
    def read(self, length):
        if self.stream is None:
            return
        return self.stream.read(length)

    def close(self):
        if self.stream is None:
            return
        self.stream.close()

    def write_char(self, value):
        res = value.encode('utf-8') 
        self.write(struct.pack('c', res))

    def write_byte(self, value):
        self.write(struct.pack('b', value))

    def write_int(self, value):
        self.write(struct.pack('i', value))

    def write_long(self, value):
        self.write(struct.pack('q', value))

    def write_short(self, value):
        self.write(struct.pack('h', value))

    def write_float(self, value):
        self.write(struct.pack('f', value))

    def write_double(self, value):
        self.write(struct.pack('d', value))

    def write_string(self, value):
        s = value.encode('utf-8') 
        self.write_short(len(s))  
        self.write(s)  
    
    def write_string_size(self, value,len):
        s = value.encode('utf-8') 
        for i in range(len):
            self.write_byte(s[i])
        
     

    def write_UTFstring(self, value):
        s = value.encode('utf-8')
        self.write(s) 
        self.write(b'\x00')


    def read_char(self):
        return struct.unpack('c', self.read(1))[0].decode('utf-8')

    def read_byte(self):
        return struct.unpack('b', self.read(1))[0]

    def read_int(self):
        return struct.unpack('i', self.read(4))[0]

    def read_long(self):
        return struct.unpack('q', self.read(8))[0]

    def read_short(self):
        return struct.unpack('h', self.read(2))[0]

    def read_float(self):
        return struct.unpack('f', self.read(4))[0]

    def read_double(self):
        return struct.unpack('d', self.read(8))[0]

    def read_string(self):
        length = self.read_short()
        string_bytes = self.read(length)
        return string_bytes.decode('utf-8')

    def read_string_size(self,length):
        string_bytes = bytearray()
        for i in range(length):
            char = self.stream.read(1)
            string_bytes.extend(char)
        return string_bytes.decode('utf-8')

    def read_UTFstring(self):
        string_bytes = bytearray()
        while True:
            char = self.stream.read(1)
            if char == b'\x00':
                break
            string_bytes.extend(char)
        return string_bytes.decode('utf-8')