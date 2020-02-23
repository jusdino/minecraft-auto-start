FROM python:3.6.5-slim

# install netcat
RUN apt-get update \
  && apt-get -y install netcat \
  && apt-get clean

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements
COPY container/requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip install -r requirements.txt

# add entrypoint.sh
COPY container/entrypoint.sh /usr/src/app/entrypoint.sh

# add app
COPY container /usr/src/app

# run server
ENTRYPOINT ["./entrypoint.sh"]
CMD ["run", "-h", "0.0.0.0"]
