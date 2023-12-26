# CC-Docker

Basic implementation of Docker-like process isolation in Python.

### Docker container

We're using linux-specific syscalls (chroot, namespaces, etc). so we need to run the code inside a Docker container.

In order to do it easily, we need to add this shell alias.

```sh
alias ddocker='docker build -t mydocker . && docker run --cap-add="SYS_ADMIN" mydocker'
```
It's used to build and run the Dockerfile with our code.

(The `--cap-add="SYS_ADMIN"` flag is required to create
[PID Namespaces](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html))

We can now execute it like:

```sh
ddocker run ubuntu:latest echo hey
```

This tries to emulate the following command:

```sh
docker run ubuntu:latest echo hey
```

Which basically pulls the `ubuntu:latest` image and runs the `echo hey` command inside it.