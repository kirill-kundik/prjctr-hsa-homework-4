FROM python:3.11-alpine

RUN mkdir /app

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY ./index.html ./index.html
COPY ./main.py ./main.py

EXPOSE 8080

CMD python main.py
