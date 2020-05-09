#!/usr/bin/env bash
set -e

echo "$KNOWN_HOSTS" >> ~/.ssh/known_hosts
echo "$SSH_AGENT_KEY" > ~/.ssh/id_rsa.pem
chmod 400 ~/.ssh/id_rsa.pem
[ -z "$SERVER_NAME" ] && exit 1

TARGET_SERVER_PATH="infra-live/${INFRA_LIVE_PATH}/${SERVER_NAME}"
echo "Cloning '$INFRA_LIVE_CLONE_URL'"
git clone -q "$INFRA_LIVE_CLONE_URL" infra-live
if [ ! -f "${TARGET_SERVER_PATH}/terragrunt.hcl" ]; then
  echo "Configuration file not found at ${TARGET_SERVER_PATH}/terragrunt.hcl"
  echo "Generating from template..."
  mkdir -p "${TARGET_SERVER_PATH}"
  sed "s/__SERVER_NAME__/${SERVER_NAME}/g" "infra-live/templates/${ENVIRONMENT}/minecraft/terragrunt.hcl" >"$TARGET_SERVER_PATH/terragrunt.hcl"
fi
echo "Launching server at $TARGET_SERVER_PATH"
cd "${TARGET_SERVER_PATH}"
cat terragrunt.hcl
terragrunt apply -input=false --auto-approve
