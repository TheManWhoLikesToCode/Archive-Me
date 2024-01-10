FROM python:3.9-bullseye

WORKDIR /backend

ADD . /backend

ARG CLIENT_SECRET_JSON

RUN echo "$CLIENT_SECRET_JSON" > /backend/client_secret.json

RUN pip install -r requirements.txt

EXPOSE 5001

CMD python ./app.py
