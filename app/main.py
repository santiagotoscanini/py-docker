import ctypes
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from app.docker_image import pull_image


def is_debug():
    codecrafters_yml = (Path(__file__).parent.parent / "codecrafters.yml").read_text()
    return "debug: true" in codecrafters_yml


def main():
    logging.basicConfig(level=logging.DEBUG if is_debug() else logging.INFO)

    image_tag = "latest"
    image = sys.argv[2].split(":")
    if len(image) == 2:
        image_tag = image[1]

    command = sys.argv[3]
    args = sys.argv[4:]

    with tempfile.TemporaryDirectory() as tmp_dir:
        pull_image(image[0], image_tag, tmp_dir)

        # Currently, On macOS with Apple Silicon, mounting /proc file system inside chrooted directory is mandatory.
        # Otherwise, running /usr/local/bin/docker-explorer binary will result in following error:
        # rosetta error: Unable to open /proc/self/exe: 2

        # TODO: check pivot_root
        os.chroot(tmp_dir)

        # Loads the C standard library (libc) into Python. The None argument is to load it in the current process.
        libc = ctypes.cdll.LoadLibrary(None)

        # https://www.man7.org/linux/man-pages/man2/unshare.2.html
        # "The flags argument is a bit mask that specifies which parts of the execution context should be unshared."
        # CLONE_NEWPID is defined here:
        # https://github.com/torvalds/linux/blob/037266a5f7239ead1530266f7d7af153d2a867fa/include/uapi/linux/sched.h#L32
        CLONE_NEWPID = 0x20000000
        libc.unshare(CLONE_NEWPID)

        completed_process = subprocess.run([command, *args], capture_output=True)
        if completed_process.stdout:
            stdout = completed_process.stdout.decode("utf-8")
            print(stdout, end='')
        if completed_process.stderr:
            stderr = completed_process.stderr.decode("utf-8")
            print(stderr, file=sys.stderr, end='')

        sys.exit(completed_process.returncode)


if __name__ == "__main__":
    main()
