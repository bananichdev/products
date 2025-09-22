FROM python:3.13-alpine

WORKDIR /usr/local/app
COPY . /usr/local/app
RUN pip install uv
EXPOSE 8443
