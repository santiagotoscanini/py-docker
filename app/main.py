import ctypes
import os
import shutil
import subprocess
import sys
import tempfile


def main():
    command = sys.argv[3]
    args = sys.argv[4:]

    with tempfile.TemporaryDirectory() as tmp_dir:
        command_dir = os.path.dirname(command)
        tmp_command_dir = tmp_dir + command_dir

        # Currently, On macOS with Apple Silicon, mounting /proc file system inside chrooted directory is mandatory.
        # Otherwise, running /usr/local/bin/docker-explorer binary will result in following error:
        # rosetta error: Unable to open /proc/self/exe: 2

        # Copy the binaries and chroot into the temporary directory
        os.makedirs(tmp_command_dir, exist_ok=True)
        shutil.copy(command, tmp_command_dir)
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
