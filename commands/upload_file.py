"""
    FFM by @JusticeRage

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from model.driver.input_api import *
from commands.command_manager import register_plugin
import base64
import hashlib
import os
import tqdm


class Upload:
    def __init__(self, *args, **kwargs):
        if len(args) < 3:
            raise RuntimeError("Received %d argument(s), expected 3." % len(args))
        if not os.path.exists(args[1]):
            raise RuntimeError("%s not found!" % args[1])
        # TODO: Verify if the remote file exists and prevent overwrite?
        self.target_file = args[1]
        self.destination = args[2]

    @staticmethod
    def regexp():
        return r"^\!upload"

    @staticmethod
    def usage():
        write_str("Usage: !upload [local file] [remote destination]\r\n", LogLevel.WARNING)

    @staticmethod
    def name():
        return "!upload"

    @staticmethod
    def description():
        return "Uploads a file to the remote machine."

    def execute(self):
        with open(self.target_file, 'rb') as f:
            md5 = hashlib.md5()
            with tqdm.tqdm(total=os.stat(self.target_file).st_size, unit="o", unit_scale=True) as progress_bar:
                contents = f.read(1024)
                while contents:
                    b64 = base64.b64encode(contents)
                    shell_exec("echo \"%s\" |base64 -d >> %s" % (b64.decode("ascii"), self.destination))
                    md5.update(contents)
                    progress_bar.update(len(contents))
                    contents = f.read(1024)
        md5sum = md5.hexdigest()
        remote_md5sum = shell_exec("md5sum %s |cut -d' ' -f1" % self.destination)
        write_str("Local MD5:  %s\r\nRemote MD5: %s\r\n" % (md5sum, remote_md5sum), LogLevel.WARNING)


register_plugin(Upload)
