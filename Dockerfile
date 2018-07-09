FROM python:alpine

WORKDIR /tmp

COPY config.py /tmp/config.py
COPY kimsufi.py /tmp/kimsufi.py
COPY requirements.txt /tmp/requirements.txt

RUN pip install -r requirements.txt

CMD [ "python", "./kimsufi.py" ]
