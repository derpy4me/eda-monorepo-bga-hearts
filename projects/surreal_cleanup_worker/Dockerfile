FROM python:3.10-slim-bookworm

ARG wheel=surreal_cleanup_worker-0.1.0-py3-none-any.whl

RUN python -m pip install --upgrade pip

WORKDIR /code

COPY ./dist/$wheel /code/$wheel

RUN pip install --no-cache-dir --upgrade $wheel

ENTRYPOINT ["python3", "-m", "bce.surreal_cleanup_worker.core"]
