import subprocess
import sys


def main():
    command = sys.argv[3]
    args = sys.argv[4:]

    completed_process = subprocess.run([command, *args], capture_output=True)
    if completed_process.stdout:
        stdout = completed_process.stdout.decode("utf-8")
        print(stdout, end='')
    if completed_process.stderr:
        stderr = completed_process.stderr.decode("utf-8")
        print(stderr, file=sys.stderr, end='')


if __name__ == "__main__":
    main()
