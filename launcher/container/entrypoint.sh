#!/usr/bin/env bash
set -e

echo "$KNOWN_HOSTS" >> ~/.ssh/known_hosts
echo "$SSH_AGENT_KEY" > ~/.ssh/id_rsa.pem
chmod 400 ~/.ssh/id_rsa.pem
[ -z "$SERVER_NAME" ] && exit 1

TARGET_SERVER_PATH="infra-live/${AWS_REGION}/dev/public/apps/minecraft/${SERVER_NAME}"
git clone -q "$INFRA_LIVE_CLONE_URL" infra-live
if [ ! -f "${TARGET_SERVER_PATH}/terraform.hcl" ]; then
  mkdir -p "${TARGET_SERVER_PATH}"
  sed "s/__SERVER_NAME__/${SERVER_NAME}/g" "infra-live/templates/minecraft/terragrunt.hcl" >"$TARGET_SERVER_PATH/terragrunt.hcl"
fi
cd "${TARGET_SERVER_PATH}"
terragrunt apply -input=false --auto-approve
