[![progress-banner](https://backend.codecrafters.io/progress/docker/07826762-dbf8-4c12-9881-92598674cd72)](https://app.codecrafters.io/users/codecrafters-bot?r=2qF)

### Docker-explorer

We have [this utility](https://github.com/codecrafters-io/docker-explorer/blob/master/main.go) that exposes
`echo`, `echo_stderr`, `mypid`, `ls`, `touch` and `exit`. So we don't run the native ones.

### Docker container

We're using linux-specific syscalls. so we need to run the code inside a Docker container.

We need to add this shell alias.

```sh
alias mydocker='docker build -t mydocker . && docker run --cap-add="SYS_ADMIN" mydocker'
```
It's used to build and run the Dockerfile with our code.

(The `--cap-add="SYS_ADMIN"` flag is required to create
[PID Namespaces](https://man7.org/linux/man-pages/man7/pid_namespaces.7.html))

We can now execute it like:

```sh
mydocker run ubuntu:latest /usr/local/bin/docker-explorer echo hey
```
