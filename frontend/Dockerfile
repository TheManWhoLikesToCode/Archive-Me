FROM python:3.9-bullseye

WORKDIR /frontend

ADD . /frontend

RUN pip install -r requirements.txt

EXPOSE 5000

CMD python ./app.py