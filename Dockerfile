FROM python:3.6.9-buster
RUN useradd -ms /bin/bash flag
USER flag
WORKDIR /home/flag

ADD . .
ENV PATH="/home/flag/.local/bin:${PATH}"
RUN python3 -m pip install --user -r requirements.txt
RUN pip install --user .
CMD python3 -m flag_access.main
