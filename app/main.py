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
        # Copy the binaries and chroot into the temporary directory
        os.makedirs(tmp_command_dir, exist_ok=True)
        shutil.copy(command, tmp_command_dir)
        os.chroot(tmp_dir)

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
