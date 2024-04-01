FROM rust:1.81-slim as build

RUN apt update && apt install -y python3.11 make build-essential python3.11-venv

COPY requirements.txt requirements.txt

# Replace the poke-engine version in requirements.txt
# Matches and replaces `poke-engine/` followed by any non-space characters
ARG GEN
RUN if [ -n "$GEN" ]; then sed -i "s/poke-engine\/[^ ]*/poke-engine\/${GEN}/" requirements.txt; fi

RUN mkdir ./packages && \
    python3 -m venv venv && \
    . venv/bin/activate && \
    # pip24 is required for --config-settings
    pip install --upgrade pip==24.2 && \
    pip install -v --target ./packages -r requirements.txt

FROM python:3.11-slim

WORKDIR /foul-play

COPY config.py /foul-play/config.py
COPY constants.py /foul-play/constants.py
COPY data /foul-play/data
COPY run.py /foul-play/run.py
COPY fp /foul-play/fp
COPY teams /foul-play/teams

COPY --from=build /packages/ /usr/local/lib/python3.11/site-packages/

ENV PYTHONIOENCODING=utf-8

CMD ["python3", "run.py"]
