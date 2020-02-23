#!/usr/bin/env bash
set -x

echo "$KNOWN_HOSTS" >> ~/.ssh/known_hosts
echo "$SSH_AGENT_KEY" > ~/.ssh/id_rsa.pem
chmod 400 ~/.ssh/id_rsa.pem

git clone -q "$INFRA_LIVE_CLONE_URL" infra-live
cd "infra-live/${TARGET_SERVER_PATH}"
terragrunt apply --auto-approve