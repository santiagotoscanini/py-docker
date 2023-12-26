FROM python:3.11-alpine

ADD . /app
WORKDIR /app

RUN sed -i -e 's/\r$//' /app/docker.sh

ENTRYPOINT ["/app/docker.sh"]
