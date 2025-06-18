FROM python:3.10-slim-bookworm

ARG wheel=bga_filter_worker-0.1.0-py3-none-any.whudo

RUN python -m pip install --upgrade pip

WORKDIR /code

COPY ./dist/$wheel /code/$wheel

RUN pip install --no-cache-dir --upgrade $wheel

ENTRYPOINT ["python3", "-m", "bce.bga_filter_worker.core"]
