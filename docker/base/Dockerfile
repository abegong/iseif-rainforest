FROM ubuntu

RUN sudo apt-get update
RUN sudo apt-get -y install python-pip python-dev libffi-dev libssl-dev
RUN apt-get install libxml2-dev libxslt1-dev -y
RUN apt-get install tree -y
RUN mkdir -p /usr/src

WORKDIR /usr/src
COPY ./ /usr/src/app/

WORKDIR /usr/src/app
RUN pip install -r requirements.txt
