# FROM python:3.8.10-slim
FROM moh3azzain/odoo-dev-env:test

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
# RUN apt-get update --allow-releaseinfo-change -y && \
#     apt-get install -y --no-install-recommends \
#         ca-certificates \
#         curl \
#         dirmngr \
#         fonts-noto-cjk \
#         gnupg \
#         libssl-dev \
#         node-less \
#         npm \
#         python3-num2words \
#         python3-pdfminer \
#         python3-pip \
#         python3-phonenumbers \
#         python3-pyldap \
#         python3-qrcode \
#         python3-renderpm \
#         python3-setuptools \
#         python3-slugify \
#         python3-vobject \
#         python3-watchdog \
#         python3-xlrd \
#         python3-xlwt \
#         xz-utils \
#     && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.buster_amd64.deb \
#     && echo 'ea8277df4297afc507c61122f3c349af142f31e5 wkhtmltox.deb' | sha1sum -c - \
#     && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
#     && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# install latest postgresql-client
# RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
#     && GNUPGHOME="$(mktemp -d)" \
#     && export GNUPGHOME \
#     && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
#     && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
#     && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
#     && gpgconf --kill all \
#     && rm -rf "$GNUPGHOME" \
#     && apt-get update --allow-releaseinfo-change -y \
#     && apt-get install --no-install-recommends -y postgresql-client \
#     && rm -f /etc/apt/sources.list.d/pgdg.list \
#     && rm -rf /var/lib/apt/lists/*

# Install rtlcss (on Debian buster)
# RUN npm install -g rtlcss

# Install some deps, from the odoo docs
# RUN apt-get update --allow-releaseinfo-change -y && \
#     apt-get install -y --no-install-recommends \
#     python3-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev \
#     libtiff5-dev \
# #     libjpeg8-dev \ has an issue: https://github.com/Automattic/node-canvas/issues/524
#     libjpeg62-turbo \
#     libopenjp2-7-dev zlib1g-dev libfreetype6-dev \
#     liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev libxcb1-dev libpq-dev \
#     build-essential
#
# RUN pip3 install setuptools wheel
# RUN pip3 install -r requirements.txt

# Install Odoo
# ENV ODOO_VERSION 15.0
# ARG ODOO_RELEASE=20220718
# ARG ODOO_SHA=dc4a5b8c5be8f873e751539117f5aa41d9f7b217
# RUN curl -o odoo.deb -sSL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.${ODOO_RELEASE}_all.deb \
#     && echo "${ODOO_SHA} odoo.deb" | sha1sum -c - \
#     && apt-get update \
#     && apt-get -y install --no-install-recommends ./odoo.deb \
#     && rm -rf /var/lib/apt/lists/* odoo.deb

# Copy entrypoint script and Odoo configuration file
# COPY ./docker/entrypoint.sh /home/odoo/app/
COPY ./docker/odoo.conf /etc/odoo/

#https://stackoverflow.com/questions/27701930/how-to-add-users-to-docker-container
RUN useradd -rm -d /home/odoo -s /bin/bash -G sudo odoo
# Set permissions and Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
# RUN chown odoo /etc/odoo/odoo.conf \
#     && mkdir -p /var/lib/odoo \
#     && chown odoo /var/lib/odoo \
#     && mkdir -p /mnt/extra-addons \
#     && chown -R odoo /mnt/extra-addons
RUN chown odoo /etc/odoo/odoo.conf \
    && mkdir -p /var/lib/odoo \
    && chown odoo /var/lib/odoo

# VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]
# VOLUME ["/var/lib/odoo"]

# Set default user when running the container
USER odoo

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf
# ENV HOST=containers-us-west-81.railway.app
# ENV PORT=6788
# ENV USER=postgres
# ENV PASSWORD=nBhFugzBRKZhtDQZFZAf
# ENV DATABASE=railway

WORKDIR /home/odoo/app
COPY . .
COPY ./docker/wait-for-psql.py /usr/local/bin/wait-for-psql.py

ENTRYPOINT ["/home/odoo/app/docker/entrypoint.sh"]
CMD ["odoo"]
