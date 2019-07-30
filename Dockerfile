FROM pmariglia/gambit-ubuntu-docker

RUN apt-get install -y python3.6 python3-pip

WORKDIR /showdown

COPY requirements.txt /showdown/requirements.txt
COPY requirements-nash.txt /showdown/requirements-nash.txt

RUN pip3 install -r requirements.txt

RUN pip3 install -r requirements-nash.txt

COPY config.py /showdown/config.py
COPY constants.py /showdown/constants.py
COPY data /showdown/data
COPY run.py /showdown/run.py
COPY showdown /showdown/showdown
COPY teams /showdown/teams
COPY websocket_communication /showdown/websocket_communication

ENV PYTHONIOENCODING=utf-8
ENV GAMBIT_PATH=gambit-enummixed

CMD ["python3", "run.py"]
