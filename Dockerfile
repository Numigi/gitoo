FROM python:3.7-slim
MAINTAINER numigi <contact@numigi.com>

ARG GITOO_VERSION
RUN pip install gitoo==${GITOO_VERSION}
