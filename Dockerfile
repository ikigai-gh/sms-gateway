FROM python:3.11-alpine

RUN addgroup -S -g 1337 sms_gateway && adduser -S -u 1337 sms_gateway -G sms_gateway

USER sms_gateway:sms_gateway

WORKDIR /sms_gateway_app

RUN pip install requests

COPY --chown=sms_gateway:sms_gateway . /sms_gateway_app

CMD ["python", "sms_gateway.py"]
