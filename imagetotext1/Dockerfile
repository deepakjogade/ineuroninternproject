# syntax=docker/dockerfile:1

FROM python:3.8

WORKDIR /imagetotext1

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /imagetotext1

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]