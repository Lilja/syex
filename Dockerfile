FROM python:3.7-alpine

LABEL maintainer="Erik <erikvlilja+syex@gmail.com>"

COPY . /app

WORKDIR /app


# install poetry, dependencies, then remove poetry
RUN apk add --no-cache libressl-dev musl-dev libffi-dev gcc
RUN pip --no-cache-dir install poetry poetry-setup \
    && poetry install \
    && rm -rf ~/.config/pypoetry

CMD ["poetry", "run", "python", "/app.py"]
