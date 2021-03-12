FROM python:3.7-alpine

LABEL maintainer="Erik <erikvlilja+syex@gmail.com>"

RUN apk add curl && \
		curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - && \
		apk remove curl

ENV PATH="/root/.poetry/bin:${PATH}"

RUN mkdir /app

COPY pyproject.toml /app/
COPY poetry.lock /app/

WORKDIR /app


RUN poetry install \
    && rm -rf ~/.config/pypoetry

COPY . /app

CMD ["poetry", "run", "python", "/app/app.py"]
