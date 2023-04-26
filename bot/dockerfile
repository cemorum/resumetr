FROM python:3.10.9

RUN apt-get update
RUN pip install --upgrade pip

COPY ./bot/ /bot
COPY ./requirements.txt /bot
COPY .env /bot
WORKDIR /bot

RUN pip install -r requirements.txt
CMD ["python", "main.py"]
