FROM python:slim

ARG TZ=America/New_York

RUN pip install requests

RUN mkdir /app
COPY ./rollerblades.py /app
RUN chmod 755 /app/rollerblades.py

ENTRYPOINT [ "python3", "-u", "/app/rollerblades.py" ]