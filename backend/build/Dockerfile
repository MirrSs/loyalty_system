FROM python:3.11

RUN pip3 install pipenv

WORKDIR /usr/src/app/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get -y install libpq-dev gcc curl wget \
    && rm -rf /var/lib/apt/lists/*

COPY ./Pipfile ./Pipfile.lock ./

COPY ./src .

EXPOSE 8000

RUN pipenv install --system --deploy --dev

ENTRYPOINT ["bash","/usr/src/app/entrypoint.sh"]

