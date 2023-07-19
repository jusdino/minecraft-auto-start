#!/bin/bash
set -x

export SERVER_NAME=__SERVER_NAME__
export DATA_BUCKET=__DATA_BUCKET_ID__

# Install early requirements
yum update -y
yum install -y amazon-cloudwatch-agent xfsprogs awscli

# Start CloudWatch logging
cat >"/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.d/config.json" <<JSON
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/data/screenlog.0",
            "log_group_name": "/aws/ec2/mas/__SUB_DOMAIN__/__SERVER_NAME__",
            "log_stream_name": "{instance_id}/screenlog",
            "retention_in_days": 30,
            "timezone": "UTC"
          },
          {
            "file_path": "/var/log/cloud-init-output.log",
            "log_group_name": "/aws/ec2/mas/__SUB_DOMAIN__/__SERVER_NAME__",
            "log_stream_name": "{instance_id}/cloud-init",
            "timezone": "UTC"
          }
        ]
      }
    }
  }
}
JSON
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.d/config.json

# Prepare data volume
export DATA_DIR=/data
mkfs -t xfs /dev/sdb
mkdir "$DATA_DIR"
mount /dev/sdb "$DATA_DIR"

# Start download of server data early
(
  cd "$DATA_DIR"
  aws s3 cp "s3://${DATA_BUCKET}/${SERVER_NAME}.tar.gz" - | tar -xzf -
) &

# Install java 17, jq
rpm --import https://yum.corretto.aws/corretto.key
curl -L -o /etc/yum.repos.d/corretto.repo https://yum.corretto.aws/corretto.repo
yum install -y jq screen
if [ __JAVA_VERSION__ -eq '8' ]; then
  amazon-linux-extras enable corretto8
  yum install -y java-1.8.0-amazon-corretto
elif [ __JAVA_VERSION__ -eq '17' ]; then
  yum install -y java-17-amazon-corretto
fi

cd "${DATA_DIR}"
env >"cloud-init.env"
cat >"change-set.json" <<JSON
{
  "Comment": "Move domain to holding",
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "__SERVER_NAME__.__SUB_DOMAIN__",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "__HOSTED_ZONE_ID__",
          "DNSName": "start.__SUB_DOMAIN__",
          "EvaluateTargetHealth": false
        }
      }
    }
  ]
}

JSON

# Mount s3 as filesystem for WorldEdit schematics
if [ ! -z '__S3_SCHEMATIC_PREFIX__' ]; then
  curl -fL https://github.com/kahing/goofys/releases/latest/download/goofys >/usr/bin/goofys && \
  chmod +x /usr/bin/goofys && \
  mkdir -p "/data/${SERVER_NAME}/plugins/WorldEdit/schematics" && \
  goofys "${DATA_BUCKET}:__S3_SCHEMATIC_PREFIX__/schematics" "/data/${SERVER_NAME}/plugins/WorldEdit/schematics"
fi

# Set up server launch script
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


# Move route53 to holding, release Elastic IP
ADDRESS_DATA=\$(aws ec2 describe-addresses --filter "Name=instance-id,Values=\$INSTANCE_ID")
ASSOCIATION_ID=\$(echo "\$ADDRESS_DATA" | jq -r '.Addresses[].AssociationId')
ALLOCATION_ID=\$(echo "\$ADDRESS_DATA" | jq -r '.Addresses[].AllocationId')

aws route53 change-resource-record-sets --hosted-zone-id "\$HOSTED_ZONE_ID" --change-batch "file://${DATA_DIR}/change-set.json"
aws ec2 disassociate-address --association-id "\$ASSOCIATION_ID"
aws ec2 release-address --allocation-id "\$ALLOCATION_ID"

# Copy data back to s3
size="\$(du -sb "${SERVER_NAME}" | IFS=\t awk '{print \$1}')"
tar -czf - "${SERVER_NAME}" | aws s3 cp --expected-size "\$size" - "s3://${DATA_BUCKET}/${SERVER_NAME}.tar.gz"

echo "Shutting down in 10 seconds..."
sleep 10
shutdown -h now
SCRIPT
chmod +x server.sh

# Wait for background server download to finish
wait
# Start server script in a screen so we can connect to Minecraft via ssh at need
screen -dm -L -S minecraft ./server.sh
