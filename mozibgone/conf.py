# the hardcoded key used in every mozi sample.
MOZI_XOR_KEY = b"\x4e\x66\x5a\x8f\x80\xc8\xac\x23\x8d\xac\x47\x06\xd5\x4f\x6f\x7e"

# the first 4 bytes of the XOR-ed config. It always begins with [ss].
MOZI_CONFIG_HEADER = b"\x15\x15\x29\xd2" # b"[ss]" ^ XOR_KEY[:4]

# the size of the Mozi config string
MOZI_CONFIG_TOTAL_SIZE = 524

# the size of the actual Mozi config
MOZI_CONFIG_SIZE = 428

# the first ECDSA384 signature, xored
MOZI_SIGNATURE_A = \
b"\x4C\xB3\x8F\x68\xC1\x26\x70\xEB\
\x9D\xC1\x68\x4E\xD8\x4B\x7D\x5F\
\x69\x5F\x9D\xCA\x8D\xE2\x7D\x63\
\xFF\xAD\x96\x8D\x18\x8B\x79\x1B\
\x38\x31\x9B\x12\x69\x73\xA9\x2E\
\xB6\x63\x29\x76\xAC\x2F\x9E\x94\xA1"

# the second ECDSA384 signature, xored
MOZI_SIGNATURE_B = \
b"\x4C\xA6\xFB\xCC\xF8\x9B\x12\x1F\
\x49\x64\x4D\x2F\x3C\x17\xD0\xB8\
\xE9\x7D\x24\x24\xF2\xDD\xB1\x47\
\xE9\x34\xD2\xC2\xBF\x07\xAC\x53\
\x22\x5F\xD8\x92\xFE\xED\x5F\xA3\
\xC9\x5B\x6A\x16\xBE\x84\x40\x77\x88"

# the magic UPX number that marks UPX data within the executable.
UPX_MAGIC = b"UPX!"

# name and size in bytes of the upx checksum
UPX_CHECKSUM = ("l_checksum", 4)
# name and size in bytes of the upx magic number
UPX_MAGIC_SIZE = ("l_magic", 4)
# name and size in bytes of the l_lsize field
UPX_LSIZE = ("l_lsize", 2)
# name and size in bytes of the l_version field
UPX_LVERSION = ("l_version", 1)
# name and size in bytes of the l_format field
UPX_LFORMAT = ("l_format", 1)
# name and size in bytes of the p_progid field
UPX_PPROGID = ("p_progid", 4)
# name and size in bytes of the p_filesize field
UPX_PFILESIZE = ("p_filesize", 4)
# name and size in bytes of the p_blocksize field
UPX_PBLOCKSIZE = ("p_blocksize", 4)

# the offset from the UPX trailer magic number to read the data from
# 6 doublewords (4 bytes) away from the start of the magic number
UPX_TRAILER_OFFSET = 6 * 4

# (name, has_suffix) e.g. [ss], [/ss]
# taken from https://blog.netlab.360.com/mozi-another-botnet-using-dht/
CONFIG_FIELDS = {
    # declaration
    "ss" : "bot role",
    "cpu" : "cpu arch",
    "nd" : "new DHT node",
    "count" : "url to report to",
    # control
    "atk" : "ddos attack type",
    "ver" : "verify",
    "hp" : "DHT id prefix",
    "dip" : "address to get new sample",
    # subtasks
    "rn" : "execute command",
    "dr" : "download and exec payload",
    "idp" : "report bot info", # bot id, ip, port, file name, gateway, cpu arch
}

DHT_BOOTSTRAP_NODES = [
    "dht.transmissionbt.com:6881",
    "router.bittorrent.com:6881",
    "router.utorrent.com:6881",
    "bttracker.debian.org:6881",
    "212.129.33.59:6881",
    "82.221.103.244:6881",
    "130.239.18.159:6881",
    "87.98.162.88:6881",
]