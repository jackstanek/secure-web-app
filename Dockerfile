FROM python:3.6.9-buster
ADD .
RUN python3 -m pip install -r requirements.txt
ENTRYPOINT