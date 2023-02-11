from aws_cdk.aws_route53 import HostedZone
from constructs import Construct
# We'll import the whole module here to dance around the massive module crushing IntelliJ
from aws_cdk import aws_ec2 as ec2


class Networking():
    """
    Network related resources for Minecraft servers
    """
    def __init__(self, scope: Construct, **kwargs) -> None:
        super().__init__()
        self.vpc = ec2.Vpc.from_lookup(
            scope, 'Vpc',
            vpc_name=scope.node.try_get_context('vpc_name')
        )
        self.subnet = self.vpc.public_subnets[0]
        self.security_group = ec2.SecurityGroup(
            scope, 'SecurityGroup',
            vpc=self.vpc,
            allow_all_outbound=True,
            description='For Minecraft servers'
        )
        self.security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4('0.0.0.0/0'),
            connection=ec2.Port.tcp(22),
            description='SSH'
        )
        self.security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4('0.0.0.0/0'),
            connection=ec2.Port.tcp(8123),
            description='HTTP in for Dynmap plugin'
        )
        self.security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4('0.0.0.0/0'),
            connection=ec2.Port.tcp(25565),
            description='Minecraft tcp'
        )
        self.security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4('0.0.0.0/0'),
            connection=ec2.Port.udp(25565),
            description='Minecraft udp'
        )
