FROM python:3.6.5-slim

RUN apt-get update && \
    apt-get install -y openssh-client git zip && \
    rm -rf /var/lib/apt/lists/*

ADD https://releases.hashicorp.com/terraform/0.12.31/terraform_0.12.31_linux_amd64.zip /usr/local/bin/terraform.zip
RUN cd /usr/local/bin && unzip terraform.zip && rm terraform.zip
ADD https://github.com/gruntwork-io/terragrunt/releases/download/v0.23.13/terragrunt_linux_amd64 /usr/local/bin/terragrunt
RUN chmod +x /usr/local/bin/terra*

COPY config /root/.ssh/config

COPY container /app
WORKDIR /app

ENTRYPOINT ["/bin/bash", "./entrypoint.sh"]