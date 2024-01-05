FROM python:3.9-bullseye

WORKDIR /backend

ADD . /backend

RUN pip install -r requirements.txt

EXPOSE 5001

CMD python ./app.py


