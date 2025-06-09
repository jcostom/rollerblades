FROM python:3.13.4-slim-bookworm AS builder

ARG TZ=America/New_York
RUN apt update && apt -yq install gcc make
RUN pip install requests

FROM python:3.13.4-slim-bookworm

ARG TZ=America/New_York
ARG PYVER=3.13

COPY --from=builder /usr/local/lib/python$PYVER/site-packages/ /usr/local/lib/python$PYVER/site-packages/

VOLUME "/config"

RUN mkdir /app
COPY ./rollerblades.py /app
RUN chmod 755 /app/rollerblades.py

ENTRYPOINT [ "python3", "-u", "/app/rollerblades.py" ]
