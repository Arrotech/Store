FROM python:3.10.2-alpine3.15

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

ARG BUILD_DEPENDENCIES=""
ARG RUNTIME_DEPENDENCIES=""

RUN apk add --no-cache bash nano build-base postgresql-dev gcc python3-dev musl-dev libffi-dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


# FROM python:3.10.2-alpine3.15

# WORKDIR /app

# RUN apk add --no-cache bash postgresql-dev gcc python3-dev musl-dev

# COPY --from=builder /app /app

COPY ./entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# ENV PYTHONPATH="${PYTHONPATH}:/app/dependencies"

ENTRYPOINT ["/entrypoint"]


