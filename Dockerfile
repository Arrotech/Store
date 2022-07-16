FROM python:3.10.2-alpine3.15

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

ARG BUILD_DEPENDENCIES=""
ARG RUNTIME_DEPENDENCIES=""

RUN apk add --no-cache bash nano build-base postgresql-dev gcc python3-dev musl-dev libffi-dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

ENTRYPOINT ["/entrypoint"]

# FROM python:3.10.2-alpine3.15 AS compile-image

# ARG BUILD_DEPENDENCIES="build-base postgresql-dev gcc python3-dev musl-dev libffi-dev"
# ARG RUNTIME_DEPENDENCIES=""

# # RUN apk add --no-cache bash nano build-base postgresql-dev gcc python3-dev musl-dev libffi-dev

# RUN python -m venv /opt/venv
# ENV PATH="/opt/venv/bin:$PATH"

# COPY requirements.txt .
# RUN pip install -r requirements.txt

# COPY ./entrypoint /entrypoint
# RUN sed -i 's/\r$//g' /entrypoint
# RUN chmod +x /entrypoint

# COPY ./start /start
# RUN sed -i 's/\r$//g' /start
# RUN chmod +x /start

# COPY ./celery/worker/start /start-celeryworker
# RUN sed -i 's/\r$//g' /start-celeryworker
# RUN chmod +x /start-celeryworker

# COPY ./celery/beat/start /start-celerybeat
# RUN sed -i 's/\r$//g' /start-celerybeat
# RUN chmod +x /start-celerybeat

# COPY ./celery/flower/start /start-flower
# RUN sed -i 's/\r$//g' /start-flower
# RUN chmod +x /start-flower

# RUN pip install .

# FROM python:3.10.2-alpine3.15 AS build-image

# COPY --from=compile-image /opt/venv /opt/venv
# ENV PATH="/opt/venv/bin:$PATH"
# ENTRYPOINT ["/entrypoint"]

# FROM python:3.10.2-alpine3.15 AS builder

# ARG BUILD_DEPENDENCIES="bash nano build-base postgresql-dev gcc python3-dev musl-dev libffi-dev"

# RUN apk add --no-cache ${BUILD_DEPENDENCIES}

# RUN python -m venv /opt/venv
# ENV PATH="/opt/venv/bin:$PATH"

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt \
#     && find /opt/venv \
#         \( -type f -a -name test -o -name tests \) \
#         -o \( -type d -a -name '*.pyc' -o -name '*.pyo*' \) \
#         -exec rm -rf '{}' \+

# FROM python:3.10.2-alpine3.15

# WORKDIR /app

# RUN apk add --no-cache bash nano

# COPY --from=builder /opt/venv /opt/venv

# COPY ./entrypoint /entrypoint
# RUN sed -i 's/\r$//g' /entrypoint
# RUN chmod +x /entrypoint

# COPY ./start /start
# RUN sed -i 's/\r$//g' /start
# RUN chmod +x /start

# COPY ./celery/worker/start /start-celeryworker
# RUN sed -i 's/\r$//g' /start-celeryworker
# RUN chmod +x /start-celeryworker

# COPY ./celery/beat/start /start-celerybeat
# RUN sed -i 's/\r$//g' /start-celerybeat
# RUN chmod +x /start-celerybeat

# COPY ./celery/flower/start /start-flower
# RUN sed -i 's/\r$//g' /start-flower
# RUN chmod +x /start-flower

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1
# ENV PATH="/opt/venv/bin:$PATH"

# ENTRYPOINT ["/entrypoint"]