ARG PGHOST
ARG PGDATABASE
ARG DATABASE_URL
ARG PGUSER
ARG PGPORT
ARG PGPASSWORD

ARG PORT

# FROM python:3.8.10-slim
FROM moh3azzain/odoo-dev-env:test

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

ENV HOST=$PGHOST
ENV USER=$PGUSER
ENV PASSWORD=$PGPASSWORD
ENV DATABASE=$PGDATABASE
ENV DBPORT=$PGPORT

ENV HTTPPORT=$PORT

# Copy Odoo configuration file
COPY ./docker/odoo.conf /etc/odoo/

RUN useradd -rm -d /home/odoo -s /bin/bash -G sudo odoo

RUN chown odoo /etc/odoo/odoo.conf \
    && mkdir -p /var/lib/odoo \
    && chown odoo /var/lib/odoo

# VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]
# VOLUME ["/var/lib/odoo"]

# Set default user when running the container
USER odoo

# Expose Odoo services
# EXPOSE 8069 8071 8072
EXPOSE ${HTTPPORT:-8069}

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf

WORKDIR /home/odoo/app
COPY . .
COPY ./docker/wait-for-psql.py /usr/local/bin/wait-for-psql.py

ENTRYPOINT ["/home/odoo/app/docker/entrypoint.sh"]
CMD ["odoo"]
