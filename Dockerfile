FROM python:slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app/backend

RUN ["python", "manage.py", "makemigrations", "--noinput"]
RUN ["python", "manage.py", "migrate", "--noinput"]

RUN ["python", "manage.py", "collectstatic", "--noinput"]

EXPOSE $PORT

CMD python manage.py runserver 0.0.0.0:$PORT