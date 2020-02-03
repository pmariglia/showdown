FROM pmariglia/gambit-ubuntu-docker

RUN apt-get update && apt-get install -y python3.6 python3-pip

WORKDIR /showdown

COPY requirements.txt /showdown/requirements.txt

RUN pip3 install -r requirements.txt

COPY config.py /showdown/config.py
COPY constants.py /showdown/constants.py
COPY data /showdown/data
COPY run.py /showdown/run.py
COPY showdown /showdown/showdown
COPY teams /showdown/teams

ENV PYTHONIOENCODING=utf-8
ENV GAMBIT_PATH=gambit-enummixed

CMD ["python3", "run.py"]
