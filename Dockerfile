FROM python:3.7-alpine

LABEL maintainer="Erik <erikvlilja+syex@gmail.com>"

# copy poetry files
COPY poetry.lock pyproject.toml ./

# install poetry, dependencies, then remove poetry
RUN pip --no-cache-dir install poetry poetry-setup \
    && poetry config settings.virtualenvs.create false \
    && poetry install \
    && pip uninstall poetry -y \
    && rm -rf ~/.config/pypoetry

WORKDIR /app

CMD python3 app.py
