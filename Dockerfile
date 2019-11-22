FROM python:3.7-slim
LABEL maintainer="numigi <contact@numigi.com>"

ARG GITOO_VERSION
RUN pip install gitoo==${GITOO_VERSION}
