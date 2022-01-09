FROM python:3

WORKDIR /monitor
COPY . .

RUN pip install -r requirements.txt
RUN CFLAGS="-fcommon" pip install RPi.GPIO

VOLUME /monitor/config

CMD ["python", "./container-monitor.py"]