FROM python:3

WORKDIR /status_monitor
COPY . .

RUN pip install -r requirements.txt
RUN CFLAGS="-fcommon" pip install RPi.GPIO
CMD ["python", "./container-monitor.py"]