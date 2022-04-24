# syntax=docker/dockerfile:1

# Inspired by: https://github.com/michaeloliverx/python-poetry-docker-example
# Uses multi-stage builds requiring Docker 17.05 or higher
# See https://docs.docker.com/develop/develop-images/multistage-build/

###
# Creating a python base with shared environment variables
FROM python:3.10-bullseye as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYSETUP_PATH="/opt/pysetup" \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_PATH="/opt/pysetup/.venv" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.1.11

ENV PATH="$POETRY_HOME/bin:$POETRY_VIRTUALENVS_PATH/bin:$PATH"



###
# builder-base is used to install "production" dependencies
FROM python-base as builder-base

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

# We copy our Python requirements here to cache them
# and install only runtime deps using poetry
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-dev


###
# 'dev-base' stage installs all dev deps
FROM python-base as dev-base

# Copying poetry and venv into image since we already installed them in python-base
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# venv already has runtime deps installed we get a quicker install
WORKDIR $PYSETUP_PATH
RUN poetry install


###
FROM dev-base as development

WORKDIR /app
CMD ["poetry", "run", "jupyter", "notebook", "--no-browser", "--allow-root", "--ip=0.0.0.0"]


###
FROM dev-base as test

WORKDIR /app
CMD ["poetry", "run", "pytest"]


###
FROM python-base as pipeline_execution
# Copy only non-dev dependencies from builder-base,
# so we can avoid having poetry in the image
COPY --from=builder-base $POETRY_VIRTUALENVS_PATH $POETRY_VIRTUALENVS_PATH

WORKDIR /app
CMD ["python", "main.py"]
