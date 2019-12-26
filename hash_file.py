import sys
import hashlib

# BUF_SIZE is totally arbitrary, change for your app!
BUF_SIZE = 65536  # lets read stuff in 64kb chunks!


def get_hash_for_file(file_path):
    # md5 = hashlib.md5()
    sha1 = hashlib.sha1()

    with open(file_path, "rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            # md5.update(data)
            sha1.update(data)

    # print("MD5: {0}".format(md5.hexdigest()))
    return sha1.hexdigest()
