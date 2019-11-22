FROM python:3.7-slim
LABEL maintainer="numigi <contact@numigi.com>"

RUN apt-get update && apt-get install -y --no-install-recommends \
        git-core \
    && \
    git config --global user.name "Gitoo" && \
    git config --global user.email "root@localhost" && \
    rm -rf /var/lib/apt/lists/*

ARG GITOO_VERSION
RUN pip install gitoo==${GITOO_VERSION}

ENTRYPOINT ["gitoo"]
