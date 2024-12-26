FROM rust:1.81-slim as build

# Install necessary build dependencies
RUN apt update && apt install -y \
    python3.11 \
    python3.11-dev \
    make \
    build-essential \
    python3.11-venv \
    git

# Set working directory and create packages directory
WORKDIR /build
RUN mkdir -p /build/packages

# Clone both repositories at the same level
RUN cd .. && \
    git clone https://github.com/RotomLearn/poke-engine.git && \
    git clone https://github.com/RotomLearn/pokey-engine.git

# Copy requirements and project files
COPY requirements.txt requirements.txt

ARG GEN

RUN python3 -m venv venv && \
    . venv/bin/activate && \
    # pip24 is required for --config-settings
    pip install --upgrade pip==24.2 && \
    # Install other requirements to the packages directory
    pip install -v --target /build/packages -r requirements.txt && \
    # Install pokey-engine from the cloned repository
    pip install -v --force-reinstall --no-cache-dir ../pokey-engine/ \
    --config-settings="build-args=--features poke-engine/${GEN:-gen4} --no-default-features" && \
    cp -r /build/venv/lib/python3.11/site-packages/pokey_engine* /build/packages/ && \
    pip uninstall -y poke-engine && pip install -v --force-reinstall \
    --no-cache-dir ../poke-engine/poke-engine-py \
    --config-settings="build-args=--features poke-engine/${GEN} --no-default-features" && \
    cp -r /build/venv/lib/python3.11/site-packages/poke_engine* /build/packages/

# Second stage
FROM python:3.11-slim
WORKDIR /foul-play
COPY config.py /foul-play/config.py
COPY constants.py /foul-play/constants.py
COPY data /foul-play/data
COPY run.py /foul-play/run.py
COPY fp /foul-play/fp
COPY teams /foul-play/teams
COPY --from=build /build/packages/ /usr/local/lib/python3.11/site-packages/
ENV PYTHONIOENCODING=utf-8
CMD ["python3", "run.py"]
