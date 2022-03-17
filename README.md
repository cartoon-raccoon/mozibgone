# mozibgone

_A Mozi botnet UPX unpacker and config extractor_

This program operates on malware samples belonging to the Mozi botnet family. An analysis of the malware can be found [here](https://blog.netlab.360.com/mozi-another-botnet-using-dht/).

This program is designed to automate the preparation of the sample for analysis, such as circumventing the anti-unpacking measures taken to break UPX decompression, as well as to automate the extraction of the XOR-encrypted configuration string.

## Features

_Unpacking_

- Detection of UPX packing, and can fix broken headers to enable unpacking.
- Can make use of custom UPX magic numbers (which is sometimes used by malware authors to break standard UPX) to find and fix broken headers

Currently, this tool only supports unpacking for files that have a broken `p_info` or `l_info` header. Some Mozi samples utilize a custom form of UPX that cannot be fixed conventionally, and may require executing the sample to extract the executable from memory.

_Config Extraction_

- Can detect encrypted configuration within the sample and decrypt it
- Can parse the configuration with regular expressions to extract various fields
- Can dump the fields to a JSON file

## Usage

```text
usage: mozibgone.py [-h] [-u] [-e] [-a] [-m MAGIC] [-o OUTPUT] [-v] [-j JSON] file

Mozi botnet unpacker and config extractor

positional arguments:
  file                  the file to operate on

options:
  -h, --help            show this help message and exit
  -u, --unpack          unpack the file only
  -e, --extract         extract the configuration only
  -a, --all             unpack and extract - equivalent to -ue
  -m MAGIC, --magic MAGIC
                        a custom UPX magic number to use
  -o OUTPUT, --output OUTPUT
                        separate file for UPX to output to
  -v, --verbose         enables debug output
  -j JSON, --json JSON  dump the configuration to a json file
```
