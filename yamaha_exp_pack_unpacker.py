import sys
import struct
import os

# Yamaha Expansion Pack Unpacker
# for unencrypted packages!
# Special 2026 Update for Python 3 (after 8 years, much lolz) 
# Written by Talnaci Alexandru
# Copyright: Yamaha Corporation


print("Yamaha Expansion Pack Unpacker v1 (for UNENCRYPTED packages)")
print("""Copyright: Yamaha Corporation (c)
Talnaci Alexandru (reverse engineered the format)""")

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <expansion pack>.ppf")
    sys.exit(1)

print(f"Using file {sys.argv[1]}")

try:
    file = open(sys.argv[1], "rb")
except OSError:
    print("File cannot be opened!")
    sys.exit(1)

header = file.read(4)
if b"XPFH" not in header:
    print("Unrecognized expansion pack header! Aborting...")
    file.close()
    sys.exit(1)

print("Found Header!")

if file.read(4) != b"\x00\x00\x00\x00":
    print("File format Error! Aborting...")
    file.close()
    sys.exit(1)

tmp_euid = None
wr_allowed = False
title = ""

while True:
    skip = True
    cmd = file.read(4)

    if not cmd:
        break

    if cmd == b"EUID":  # ignore EUID
        length = struct.unpack(">I", file.read(4))[0]
        tmp_euid = file.read(length)

    elif cmd == b"ETIT" and not wr_allowed:
        length = struct.unpack(">I", file.read(4))[0]
        title = file.read(length).decode(errors="ignore")

        if not os.path.exists(title):
            os.makedirs(title)

        print(f"Expansion Pack Title: {title}")
        wr_allowed = True
        skip = False

    elif cmd == b"EICQ":
        length = struct.unpack(">I", file.read(4))[0]
        print("     => Reading icon...")
        with open(os.path.join(title, "icon.png"), "wb") as f:
            f.write(file.read(length))
        skip = False
        file.seek(file.tell() + 2)

    elif cmd == b"BLOB":
        length = struct.unpack(">I", file.read(4))[0]
        file_title = None
        file_extension = None

        while True:
            ct = file.read(4)

            if ct == b"EUID":
                length = struct.unpack(">I", file.read(4))[0]
                file.read(length)
                if file.read(2) != b"\x00\x00":
                    file.seek(file.tell() - 2)

            elif ct == b"ETIT":
                length = struct.unpack(">I", file.read(4))[0]
                file_title = file.read(length).decode(errors="ignore")
                x = b"\x00"
                while x == b"\x00":
                    x = file.read(1)
                file.seek(file.tell() - 1)

            elif ct == b"EEXT":
                length = struct.unpack(">I", file.read(4))[0]
                file_extension = file.read(length).decode(errors="ignore")
                x = b"\x00"
                while x == b"\x00":
                    x = file.read(1)
                file.seek(file.tell() - 1)

            elif ct == b"EICO":
                length = struct.unpack(">I", file.read(4))[0]
                file.read(length)

            elif ct == b"FBIN":
                length = struct.unpack(">I", file.read(4))[0]
                print(f"     => Reading {title}/{file_title}.{file_extension}")
                out_path = os.path.join(title, f"{file_title}.{file_extension}")
                with open(out_path, "wb") as f:
                    f.write(file.read(length))
                x = b"\x00"
                while x == b"\x00":
                    x = file.read(1)
                file.seek(file.tell() - 1)
                break

        skip = False

    if skip:
        file.read(2)  # skip last 2 bytes

    if file.tell() == os.fstat(file.fileno()).st_size:
        break

print("Unpack complete!")
file.close()
