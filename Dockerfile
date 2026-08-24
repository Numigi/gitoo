FROM python:3.11-slim

LABEL maintainer="numigi <contact@numigi.com>"

# Install git (required by gitoo)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git-core && \
    git config --global user.name "Gitoo" && \
    git config --global user.email "root@localhost" && \
    rm -rf /var/lib/apt/lists/*

# Set up gitoo home
ENV GITOO_HOME=/home/gitoo/
RUN mkdir ${GITOO_HOME}

# Copy only necessary files for gitoo installation
COPY src ${GITOO_HOME}/src
COPY .git ${GITOO_HOME}/.git
COPY setup.cfg setup.py pyproject.toml ${GITOO_HOME}/

# Install setuptools_scm and dependencies first
RUN pip install --no-cache-dir "setuptools_scm>=8.0" setuptools wheel

# Install gitoo (setuptools_scm will use .git to determine version)
RUN pip install --no-cache-dir ${GITOO_HOME}

# Set entrypoint
ENTRYPOINT ["gitoo"]

# Default command
CMD ["install-all", "--conf_file", "gitoo.yml", "--destination", "/mnt/third-party-addons"]
