import re
import json
import logging
from enum import Enum

from mozibgone.conf import MOZI_XOR_KEY, \
    MOZI_CONFIG_SIZE, MOZI_CONFIG_HEADER, \
    MOZI_CONFIG_TOTAL_SIZE, CONFIG_FIELDS

#todo: add json output

logger = logging.getLogger()
    
###! EXCEPTIONS !###

class MoziHeaderError(Exception):
    """
    An exception class when the header could not be found
    """
    def __repr__(self):
        return "Could not find Mozi config header within sample binary"

class MoziParsingError(Exception):
    """
    An exception class for errors when parsing the config
    """
    def __repr__(self):
        return "An error occurred while parsing the config"

class DecodeErrType(Enum):
    INCORRECT_HEADER = "Provided config does not start with magic byte sequence b'[ss]'"
    NO_SIGNATURE_A = "Provided binary does not contain signature A"
    NO_SIGNATURE_B = "Provided binary does not contain signature B"
    DEFAULT = "There was an error in decoding the config"

class MoziDecodeError(Exception):
    """
    An enum type for an error that has occurred during decoding.
    """

    def __init__(self, ty: DecodeErrType):
        self.ty = ty

    def __repr__(self):
        return self.ty.value

###! CLASSES !###

class DecConfigType(Enum):
    RAW = 0
    PARSED = 1
    SIG_A = 2
    SIG_B = 3

def decrypt_config(data, as_bytes = False):
    for i in range(len(data)):
        data[i] ^= MOZI_XOR_KEY[i % len(MOZI_XOR_KEY)]
    
    if not as_bytes:
        return ''.join([chr(i) for i in data])
    else:
        return bytes(data)

class MoziConfigDecoder:
    def __init__(self, data):
        self.data = data
        self.configs = dict()

    def decode_config(self):
        # the data we hold should just be the config and not the entire file
        if self.data[:4] != list(MOZI_CONFIG_HEADER):
            raise MoziDecodeError(DecodeErrType.INCORRECT_HEADER)
        try:
            start = 0
            end = start + MOZI_CONFIG_TOTAL_SIZE
            self.configs["raw"] = decrypt_config(self.data[start:end])
        except:
            raise MoziDecodeError(DecodeErrType.DEFAULT)

    def parse_config(self):
        for field, _ in CONFIG_FIELDS.items():
            regex = re.compile(f"\[{field}\](.*)\[/{field}\]")
            matches = regex.findall(self.configs["raw"])
            if len(matches) != 0:
                self.configs[field] = matches[0]
        try:
            self.configs["idp"] = True if "[idp]" in self.configs["count"] else False
            self.configs["count"] = self.configs["count"].replace("[idp]", "")
            self.configs["raw"] = self.configs["raw"][:MOZI_CONFIG_SIZE]\
                .rstrip('\x00')
        except KeyError:
            raise MoziDecodeError(DecodeErrType.DEFAULT)
        except Exception:
            raise MoziParsingError()
    
    def print_config(self, ty):
        """
        Prints the config.

        Defaults to parsed config and is called when MoziConfigDecoder.decode() is called with print.

        When called separately, the type of config to print can be defined.
        """
        try:
            logger.info(self.configs[ty])
        except KeyError as e:
            if e.args[0] == DecConfigType.PARSED:
                raise MoziParsingError()
            elif e.args[0] == DecConfigType.SIG_A:
                raise MoziDecodeError(DecodeErrType.NO_SIGNATURE_A)
            elif e.args[0] == DecConfigType.SIG_B:
                raise MoziDecodeError(DecodeErrType.NO_SIGNATURE_B)
            else:
                raise MoziDecodeError(DecodeErrType.DEFAULT)

    def dump_config(self, filename, ty: DecConfigType):
        with open(filename, "w") as f:
            f.write(self.configs[ty])

    def decode(self, print):
        self.decode_config()
        parsed = self.parse_config()
        if print:
            self.print_config(DecConfigType.PARSED)
        return parsed

class MoziDecoder:
    def __init__(self, path):
        self.path = path
        self.data = b""
        self.cfg_start = 0
        self.cfg_end = 0
        self.inner = None
    
    def read_file(self):
        with open(self.path, "rb") as f:
            self.data = f.read()
    
    def decode_cfg(self, print: bool):
        self.find_config()
        raw_cfg = list(self.data[self.cfg_start:self.cfg_end])
        self.inner = MoziConfigDecoder(raw_cfg)
        return self.inner.decode(print)

    def find_config(self):
        try:
            start = self.data.index(MOZI_CONFIG_HEADER)
        except ValueError:
            raise MoziHeaderError()
        else:
            self.cfg_start = start

        self.cfg_end = self.cfg_start + MOZI_CONFIG_SIZE

    #? could implement this better probably
    def dump_json(self, filename):
        s = json.dumps(self.inner.configs)
        with open(filename, "w") as f:
            f.write(s)

    def decode(self, print = False):
        self.read_file()
        self.decode_cfg(print)

        return self.inner.configs

if __name__ == "__main__":
    import sys

    filename = sys.argv[1]

    decoder = MoziDecoder(filename)
    decoder.decode()
    
    try:
        decoder.inner.print_config(DecConfigType.RAW)
        #decoder.inner.dump_config("test", DecConfigType.RAW)
        decoder.inner.parse_config()
        print(decoder.inner.configs)
    except Exception as e:
        print(e)