FROM python:3.11.4-alpine3.18
RUN apk update
RUN apk add git
RUN apk add --no-cache --virtual .pynacl_deps build-base python3-dev libffi-dev

RUN python -m pip install --upgrade pip

RUN pip install mpyl==1.0.8
RUN pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple mpyl==163.2081

RUN mkdir -p /opt/mpyl
RUN mkdir -p /opt/workspace

COPY --link /mpyl_config.yml /opt/mpyl/mpyl_config.yml
COPY --link /run_properties.yml /opt/mpyl/run_properties.yml


ENV MPYL_CONFIG_PATH=/opt/mpyl/mpyl_config.yml
ENV MPYL_RUN_PROPERTIES_PATH=/opt/mpyl/run_properties.yml

WORKDIR /opt/


