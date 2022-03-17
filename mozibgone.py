#!/usr/bin/env python3

import argparse
import logging
import sys
import re

import mozibgone
from mozibgone.extract import *
from mozibgone.unpack import *

desc = "Mozi botnet unpacker and config extractor"

# set up argument parsing
parser = argparse.ArgumentParser(description=desc)

parser.add_argument(
    "-u", "--unpack", action='store_true',
    help="unpack the file only"
)
parser.add_argument(
    "-e", "--extract", action='store_true',
    help="extract the configuration only"
)
parser.add_argument(
    "-a", "--all", action='store_true',
    help="unpack and extract - equivalent to -ue"
)
parser.add_argument(
    "-m", "--magic", help="a custom UPX magic number to use"
)
parser.add_argument(
    "-o", "--output", help="separate file for UPX to output to"
)
parser.add_argument(
    "-v", "--verbose", action='store_true',
    help="output extra information"
)
parser.add_argument(
    "-j", "--json", help="dump the configuration to a json file"
)
parser.add_argument("file", help="the file to operate on")

# set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)

def parse_magic(magic_str):
    regex = re.compile("(0x[a-fA-F0-9]{2})")
    # split the string by matches and filter out empty strings
    matches = list(filter(lambda i: i != '', regex.split(magic_str)))

    b = bytearray()
    for m in matches:
        # if we encounter a byte
        # byteorder shouldn't matter cause it's just 1 byte lol
        if "0x" in m:
            b.extend(int(m, 16).to_bytes(1, "little"))
        else: # else, just convert the string to bytes
            b.extend(bytes(m, "ascii"))
    
    logger.debug(f"[debug] magic number parsed into {b}")
    
    return b

def main():
    args = parser.parse_args()

    if args.file == "":
        logger.error("[ERROR] No file provided")
        sys.exit(1)

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    magic = mozibgone.conf.UPX_MAGIC

    if args.magic is not None:
        magic = parse_magic(args.magic)

    all = False
    file = args.file
    output = args.output

    if not args.unpack and not args.extract and not args.all:
        all = True
    else:
        all = args.all

    if args.unpack or all:
        try:
            logger.info(f"[*] Unpacking file '{file}'")
            unpacker = MoziUnpacker(file, magic = magic)
            unpacker.unpack(output)
        #todo: better exception handling
        except NotUPXPackedErr:
            logger.error(f"[ERROR] The file '{file}' does not seem to be packed with UPX")
            sys.exit(1)
        except MoziUnpackerErr as e:
            logger.error(e.errmsg)
            sys.exit(1)
        # except Exception as e:
        #     logger.error(e)
        #     sys.exit(1)
        else:
            logger.info(f"[*] Successfully unpacked '{file}'")

    if args.extract or all:
        decoder = MoziDecoder(file if output is None else output)
        config = decoder.decode()

        #todo: fix this into something nicer
        print(config)

        if args.json is not None:
            decoder.dump_json(args.json)


if __name__ == "__main__":
    main()
