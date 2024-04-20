import glob
import hashlib
import os
import random
import shutil
import string
import zlib
from multiprocessing import Queue

from nicegui import app
from send2trash import send2trash


class Model:
    files_to_copy = []

    def check_equal(self, file1, file2, method):
        return method(file1) == method(file2)

    def crc32(self, path: str) -> str:
        with open(path, "rb") as f:
            return str(zlib.crc32(f.read()))

    def md5(self, path: str) -> str:
        SIZE = 65536

        # sha1, sha256, sha512
        md5 = hashlib.md5()

        with open(path, "rb") as f:
            while True:
                data = f.read(size=SIZE)

                if not data:  # data == ""
                    break

                md5.update(data)

        return md5.hexdigest()

    def get_postfix(self) -> str:
        return "".join(
            random.choices(string.ascii_uppercase + string.ascii_lowercase, k=5)
        )

    async def find_files_to_copy(self, source_folder: str) -> list[str]:
        files_to_copy = []

        exts_str: str = app.storage.general.get("exts", "")
        exts_list: list = [ext.strip() for ext in exts_str.split("|")]

        for ext in exts_list:
            files: list = glob.glob(
                os.path.join(source_folder, "**", f"*.{ext}"), recursive=True
            )  # can return empty list

            files_to_copy.extend(files)

        return files_to_copy

    def copy(self, q: Queue, dst, move=False) -> str:
        for e, file in enumerate(self.files_to_copy):
            basename = os.path.basename(file)
            new_path = os.path.join(dst, basename)
            if os.path.exists(new_path):
                if self.check_equal(file, new_path, self.md5):
                    if move:
                        send2trash(file)
                    continue
                else:
                    name, ext = basename.split(".")

                    new_path = os.path.join(dst, f"{name}_{self.get_postfix()}.{ext}")
            shutil.copy(file, new_path)

            if move:
                send2trash(file)

            q.put_nowait([e / len(self.files_to_copy), file])

        return "Done!"
