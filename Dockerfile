#FROM python:3.11-bullseye as python-base
FROM swr.cn-north-4.myhuaweicloud.com/srpx/python:3.10.16-slim-bullseye as py310

# variables
ARG username=bkitsm
ARG pypi_index_url=https://pypi.org/simple/
ARG replace_debian_source=false

# 设置环境变量
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV LC_ALL=C.UTF-8  LANG=C.UTF-8

# 工作目录
WORKDIR /app

# 安装系统依赖
RUN sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list \
    && apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    pkg-config \
    default-libmysqlclient-dev \
    python3-dev \
    libssl-dev \
    libffi-dev \
    vim strace tini \
    && rm -rf /var/lib/apt/lists/*

# install python packages
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=/app/requirements.txt \
    python -m venv /app/venv \
    && /app/venv/bin/pip install --upgrade pip \
    && /app/venv/bin/pip install -r /app/requirements.txt -i "${pypi_index_url}"


# build frontend
#FROM node:20-bullseye-slim as node-builder
FROM node:18.18.2-slim AS node-installer

# pnpm
# RUN npm install -g pnpm@9
ENV NODE_OPTIONS="--max_old_space_size=4096"

# build frontend
WORKDIR /app

COPY . .
RUN yarn config set registry https://mirrors.tencent.com/npm/
RUN cd /app/frontend && yarn install
RUN cd /app/frontend && yarn build

# final image
FROM py310 as base-app

# install vim and chromium
RUN groupadd -r ${username}  \
    && useradd -r -g ${username} ${username}  \
    && mkdir -p /data/ /app/ /home/${username} \
    && chown -R ${username}:${username} /data/ /app/ /home/${username}

# move code and python packages
COPY --chown=${username}:${username} . /app/code/
COPY --from=node-builder --chown=${username}:${username} /app/static/assets /app/code/static/assets
COPY --from=python-builder --chown=${username}:${username} /app/venv /app/venv

ARG version
RUN echo ${version} > /app/code/VERSION

# set user
USER ${username}

# set workdir
WORKDIR /app/code

# set python env
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD python manage.py runserver 0.0.0.0:8000
