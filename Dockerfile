FROM python:3.7-alpine as base
LABEL maintainer="oijkn"
LABEL description="Infpyng can ping multiple hosts at once and write data to InfluxDB"

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN pip install --prefix /install --no-cache-dir -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local
COPY . /app/infpyng

WORKDIR /app/infpyng

RUN apk add --no-cache fping

CMD ["python", "infpyng.py"]
