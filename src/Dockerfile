# pull official base image
FROM python:3.9

# set work directory
WORKDIR /usr/src/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
#RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# copy project
COPY . /usr/src/
CMD ["gunicorn", "main:app", "--workers", "4",  "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]