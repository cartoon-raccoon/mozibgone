import subprocess
import logging

from mozibgone.conf import UPX_MAGIC, UPX_MAGIC_SIZE,\
    UPX_LSIZE, UPX_LVERSION, UPX_LFORMAT,\
    UPX_PPROGID, UPX_PFILESIZE, UPX_PBLOCKSIZE, UPX_TRAILER_OFFSET

FIELD_ORDER = [
    UPX_MAGIC_SIZE, #4
    UPX_LSIZE,      #2
    UPX_LVERSION,   #1
    UPX_LFORMAT,    #1
    UPX_PPROGID,    #4
    UPX_PFILESIZE,  #4
    UPX_PBLOCKSIZE, #4
]

# the path to output the unpacked file to, if given
# this is horrible coding but meh
unpack_output = None

logger = logging.getLogger()

def offset_to(field):
    """
    Gets the offset from the magic number to a specified field
    """
    idx = FIELD_ORDER.index(field)

    if idx == -1:
        pass # raise some error

    offset = 0
    for i in range(idx):
        offset += FIELD_ORDER[i][1]

    return offset

class NotUPXPackedErr(Exception):
    """
    Raised when trying to unpack a file that is not UPX packed
    """
    def __init__(self):
        self.errmsg = "The file in question is not packed with UPX."

class MoziUnpackerErr(Exception):
    """
    Generic error raised when something goes wrong
    """
    def __init__(self, errmsg):
        self.errmsg = errmsg

def get_upx_magic_idxs(data, magic):
    """
    Gets the indexes of the UPX magic number.
    Accepts a custom magic number.

    params:
    data - the data to sort through
    magic - the magic number to search for
    """
    curr = 0
    idxs = []
    while curr > -1:
        try:
            curr = data.index(magic, curr)
            idxs.append(curr)
            curr += 1
        except ValueError:
            break
        except Exception as e:
            raise MoziUnpackerErr(e)

    return idxs

def fix_p_info(data, idxs):
    # offset of the first magic number
    p_info = idxs[0]
    # offset of the trailer magic number
    trailer = idxs[-1]

    # normally if the p_info struct is corrupted, p_filesize and p_blocksize
    # have been zeroed out
    # so we find those values and restore them

    # get the offset of p_filesize from the p_info magic number
    p_filesize = p_info + offset_to(UPX_PFILESIZE)
    # same thing for p_blocksize
    p_blocksize = p_info + offset_to(UPX_PBLOCKSIZE)
    # compute the start of the value to set and get its value
    start = trailer + UPX_TRAILER_OFFSET
    value_to_set = data[start:start + 4]

    for i in range(4):
        data[p_filesize + i] = value_to_set[i]
        data[p_blocksize + i] = value_to_set[i]

    return data

def fix_upx_magic(data, idxs):
    """
    Replaces an obfuscated UPX magic number with the proper one.
    """

    for idx in idxs:
        for i in range(4):
            data[idx + i] = UPX_MAGIC[i]

    return data

class MoziUnpacker:
    """
    A class that can detect UPX packing on a binary and run UPX to unpack it.
    
    It can also detect corrupted UPX headers and run algorithms to fix them
    It can also be supplied with a custom magic number to use if the
    binary uses a custom magic number to break unpacking.
    """
    def __init__(self, path, magic = UPX_MAGIC, output = None):
        """
        Creates a new `MoziUnpacker` object.

        params:
        path - the path of the file being scanned.
        magic - a custom UPX magic number, if any
        output - the file to output the fixed data to. If None, outputs to the input file.
        """
        self.magic = magic
        self.is_custom = False if magic == UPX_MAGIC else True
        self.path = path
        self.output = self.path if output is None else output
        self.data = None
        self.hdr_idxs = []

        logger.debug(f"Using magic {self.magic}")

    def read_file(self):
        """
        Reads a file into memory
        """
        logger.debug(f"[debug] reading from {self.path}")
        with open(self.path, "rb") as f:
            self.data = f.read()

    def write_file(self):
        if self.data is None:
            logger.warn("[!] no data to write")
            return

        with open(self.output, "wb") as f:
            f.write(self.data)
        
        logger.debug(f"[debug] written data to {self.output}")

    def check_upx(self):
        """
        Checks if a file is UPX packed

        return: bool
        """
        if self.data is None:
            self.read_file()

        try:
            _ = self.data.index(self.magic)
            return True
        except ValueError:
            return False
        except Exception as e:
            raise MoziUnpackerErr(e)

    def exec_upx(self, output = None):
        """
        Executes UPX in a subprocess to perform the unpacking.
        """
        args = ["upx", "-d", self.path]

        if output is not None:
            args.extend(["-o", output])
        logger.debug(f"[debug] running upx with args {args[1:]}")

        res = subprocess.run(args, capture_output = True)
        
        code = res.returncode
        # output by upx is sent in the following format:
        # upx: <file>: <ExceptionType>: <error msg>
        # so we split by colon and return the error message
        output = str(res.stderr).split(':')

        err_msg = ""

        if len(output) == 4:
            err_msg = output[3]
        elif code != 0:
            raise MoziUnpackerErr(f"[ERROR] UPX returned error with output:\n> {str(res.stderr)}")
        
        return code, err_msg


    def fix_upx_hdrs(self, errmsg):
        """
        If exec_upx returns an error, this function evaluates the issue with the sample
        and runs the appropriate algorithm to fix it.

        Raises an exception if the file is not UPX packed/cannot be unpacked.

        params:
        errmsg - the error message returned by upx.
        """
        self.hdr_idxs = get_upx_magic_idxs(self.data, self.magic)

        logger.debug(f"[debug] got magic number at indexes {self.hdr_idxs}")

        if len(self.hdr_idxs) < 3:
            # warn that the file may not be fixable
            logger.warn("[!] missing one or more UPX magic numbers, file may not be able to be unpacked")
        elif len(self.hdr_idxs) > 3:
            logger.warn("[!] file contains more than 3 UPX magic numbers")

        data = list(self.data)

        if self.is_custom:
            logger.debug(f"[debug] using custom magic number, fixing magics now")
            self.data = bytes(fix_upx_magic(data, self.hdr_idxs))
            self.write_file()
            code, errmsg = self.exec_upx(unpack_output)

            if code == 0:
                return
            else:
                # update data to the latest version
                data = list(self.data)
                # # if we outputted to a different file
                # if unpack_output is not None:
                #     self.path = unpack_output

        if "p_info corrupted" in errmsg:
            data = fix_p_info(data, self.hdr_idxs)
        # catch for any stragglers that may have gotten past the magic number check
        elif "not packed by UPX" in errmsg:
            raise NotUPXPackedErr()
        else:
            raise MoziUnpackerErr(f"[ERROR] Cannot handle UPX error: `{errmsg}`")

        self.data = bytes(data)

    def unpack(self, unpack_out = None):
        self.read_file()
        unpack_output = unpack_out

        # self.check_upx() uses a custom magic if supplied
        # so if not present, just die anyway
        if not self.check_upx():
            raise NotUPXPackedErr()

        # first run UPX to check if it unpacks properly
        # if it works, great, just return
        code, errmsg = self.exec_upx(unpack_output)
        if code == 0:
            return

        # if UPX magic is present, run the fix and write it to the file
        self.fix_upx_hdrs(errmsg)
        self.write_file()

        code, errmsg = self.exec_upx(unpack_output)

        if code != 0:
            raise MoziUnpackerErr(errmsg)

if __name__ == "__main__":
    import sys
    
    file = sys.argv[1]

    unpacker = MoziUnpacker(file)

    unpacker.unpack()


