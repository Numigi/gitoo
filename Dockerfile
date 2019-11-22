FROM python:3.7-slim
LABEL maintainer="numigi <contact@numigi.com>"

RUN apt-get update && apt-get install -y --no-install-recommends \
        git-core \
    && \
    git config --global user.name "Gitoo" && \
    git config --global user.email "root@localhost" && \
    rm -rf /var/lib/apt/lists/*

ENV GITOO_HOME=/home/gitoo/
RUN mkdir ${GITOO_HOME}

COPY src ${GITOO_HOME}/src
COPY .git ${GITOO_HOME}/.git
COPY setup.cfg setup.py ${GITOO_HOME}
RUN pip install ${GITOO_HOME}

ENTRYPOINT ["gitoo"]
