# Build the python application
FROM python:3.11.7-alpine3.18 as base

RUN apk upgrade --no-cache && apk add --no-cache gcc libc-dev libffi-dev

ENV VIRTUAL_ENV=/opt/fortigate-netbox
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

COPY Fortigate-Netbox/ /opt/fortigate-netbox
RUN pip install -r /opt/fortigate-netbox/requirements.txt

# Copy the python application for running
FROM python:3.11.7-alpine3.18

RUN apk upgrade --no-cache

COPY --from=base /opt/fortigate-netbox /opt/fortigate-netbox
WORKDIR /opt/fortigate-netbox

# COPY cron /etc/crontabs/root
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT /entrypoint.sh