FROM pmariglia/gambit-docker as debian-with-gambit

FROM python:3.8-slim

COPY --from=debian-with-gambit /usr/local/bin/gambit-enummixed /usr/local/bin

WORKDIR /showdown

COPY requirements.txt /showdown/requirements.txt
COPY requirements-docker.txt /showdown/requirements-docker.txt

RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements-docker.txt

COPY config.py /showdown/config.py
COPY constants.py /showdown/constants.py
COPY data /showdown/data
COPY run.py /showdown/run.py
COPY showdown /showdown/showdown
COPY teams /showdown/teams

ENV PYTHONIOENCODING=utf-8
ENV GAMBIT_PATH=gambit-enummixed

CMD ["python3", "run.py"]
