FROM python:3.9-bullseye

WORKDIR /frontend

ADD . /frontend

RUN pip install -r requirements.txt

ARG PORT
ENV PORT=$PORT

EXPOSE $PORT

CMD python ./app.py