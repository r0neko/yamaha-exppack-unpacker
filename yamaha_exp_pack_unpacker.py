import sys, struct, os

# Yamaha Expansion Pack Unpacker
# for unencrypted packages!

# Written by Talnaci Alexandru
# Copyright: Yamaha Corporation

print("Yamaha Expansion Pack Unpacker(for UNENCRYPTED packages)")
print("""Copyright: Yamaha Corporation(c)
           Talnaci Alexandru(reverse engineered the format)""")
if len(sys.argv) != 2:
    print("Usage: %s <expansion pack>.ppf" %(sys.argv[0]))
else:
    print("Using file %s" %(sys.argv[1]))
    file = open(sys.argv[1], "rb")
    if not file:
        print "File cannot be opened!"
    else:
        header = file.read(4)
        if "XPFH" in header:
            print("Found Header!")
            if file.read(4) == "\x00\x00\x00\x00":
                tmp_euid = None
                wr_allowed = False
                title = ""
                while(1):
                    skip = True
                    cmd = file.read(4)
                    # print(cmd)
                    if "EUID" in cmd: # we ignore EUID...
                        length = struct.unpack('>I', file.read(4))[0]
                        tmp_euid = file.read(length)
                    elif "ETIT" in cmd and wr_allowed == False:
                        length = struct.unpack('>I', file.read(4))[0]
                        title = file.read(length)
                        if not os.path.exists(title):
                            os.makedirs(title)
                        print("Expansion Pack Title: %s" %(title))
                        wr_allowed = True
                        skip = False
                    elif "EICQ" in cmd:
                        length = struct.unpack('>I', file.read(4))[0]
                        print("     => Reading icon...")
                        open("%s\icon.png" %(title), "wb").write(file.read(length))
                        skip = False
                        file.seek(file.tell() + 2)
                    elif "BLOB" in cmd:
                        length = struct.unpack('>I', file.read(4))[0]
                        file_title = None
                        file_extension = None
                        while(1): # second file parser
                            ct = file.read(4)
                            if ct == "EUID": # ignore EUID
                                length = struct.unpack('>I', file.read(4))[0]
                                tmp_feuid = file.read(length)
                                if file.read(2) != b"\x00\x00":
                                    file.seek(file.tell() - 2)
                            elif ct == "ETIT":
                                length = struct.unpack('>I', file.read(4))[0]
                                file_title = file.read(length)
                                x = b"\x00"
                                while x == b"\x00":
                                    x = file.read(1)
                                file.seek(file.tell() - 1)
                            elif ct == "EEXT":
                                length = struct.unpack('>I', file.read(4))[0]
                                file_extension = file.read(length)
                                x = b"\x00"
                                while x == b"\x00":
                                    x = file.read(1)
                                file.seek(file.tell() - 1)
                            elif ct == "EICO":
                                length = struct.unpack('>I', file.read(4))[0]
                                eico = file.read(length)
                            elif ct == "FBIN":
                                length = struct.unpack('>I', file.read(4))[0]
                                print("     => Reading %s/%s.%s" %(title, file_title, file_extension))
                                open("%s/%s.%s" %(title, file_title, file_extension), "wb").write(file.read(length))
                                x = b"\x00"
                                while x == b"\x00":
                                    x = file.read(1)
                                file.seek(file.tell() - 1)
                                break
                        skip = False
                    if skip: file.read(2) # we skip the last 2 bytes!
                    if file.tell() == os.fstat(file.fileno()).st_size:
                        break
                print("Unpack complete!")
                file.close()
            else:
                print("File format Error! Aborting...")
        else:
            print("Unrecognized expansion pack header! Aborting...")
