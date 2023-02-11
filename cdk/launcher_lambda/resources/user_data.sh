#!/bin/bash
set -x

export SERVER_NAME=__SERVER_NAME__
export DATA_BUCKET=__DATA_BUCKET_ID__

# Prepare data volume
export DATA_DIR=/data
mkfs -t xfs /dev/sdb
mkdir "$DATA_DIR"
mount /dev/sdb "$DATA_DIR"

# Start download of server data early
(
  cd "$DATA_DIR"
  aws s3 cp "s3://${DATA_BUCKET}/${SERVER_NAME}.tar.gz" "${SERVER_NAME}.tar.gz"
  tar -xzvf "${SERVER_NAME}.tar.gz"
  rm "${SERVER_NAME}.tar.gz"
) &

# Install java 17, jq
rpm --import https://yum.corretto.aws/corretto.key
curl -L -o /etc/yum.repos.d/corretto.repo https://yum.corretto.aws/corretto.repo
yum install -y java-17-amazon-corretto-devel jq

env >"${DATA_DIR}/cloud-init.env"
cat >"${DATA_DIR}/change-set.json" <<JSON
{
  "Comment": "Move domain to holding",
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "__SERVER_NAME__.__SUB_DOMAIN__",
        "Type": "A",
        "TTL": 60,
        "ResourceRecords": [
          {
            "Value": "$(dig +short start.__SUB_DOMAIN__ | head -1)"
          }
        ]
      }
    }
  ]
}
JSON
cat >server.sh <<SCRIPT
#!/bin/bash
set -x

cd "$DATA_DIR"
export AWS_DEFAULT_REGION=__AWS_REGION__
export HOSTED_ZONE_ID=__HOSTED_ZONE_ID__
export INSTANCE_ID=$(curl http://169.254.169.254/latest/meta-data/instance-id)

(
  cd "${SERVER_NAME}"
  java -Xmx__MEMORY__ -Xms__MEMORY__ -jar server.jar
)
tar -czvf "${SERVER_NAME}.tar.gz" "${SERVER_NAME}"
aws s3 cp "${SERVER_NAME}.tar.gz" "s3://${DATA_BUCKET}/${SERVER_NAME}.tar.gz"

# Move route53 to holding, release Elastic IP
ADDRESS_DATA=\$(aws ec2 describe-addresses --filter "Name=instance-id,Values=\$INSTANCE_ID")
ASSOCIATION_ID=\$(echo "\$ADDRESS_DATA" | jq -r '.Addresses[].AssociationId')
ALLOCATION_ID=\$(echo "\$ADDRESS_DATA" | jq -r '.Addresses[].AllocationId')

aws route53 change-resource-record-sets --hosted-zone-id "\$HOSTED_ZONE_ID" --change-batch "file://${DATA_DIR}/change-set.json"
aws ec2 disassociate-address --association-id "\$ASSOCIATION_ID"
aws ec2 release-address --allocation-id "\$ALLOCATION_ID"

shutdown -h now
SCRIPT
chmod +x server.sh

# Wait for background server download to finish
wait
# Start server script in a screen so we can connect to Minecraft via ssh at need
screen -dm -L -S minecraft ./server.sh