FROM python:3.8.0-slim

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
CMD ["-b", "0.0.0.0:5000"]
