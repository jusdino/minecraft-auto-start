from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from stacks.persistent import PersistentStack
from .networking import Networking
from .profile import Profile


class ServerStack(Stack):
    """
    The Cfn Stack where we will keep common infrastructure items that are shared across Minecraft servers
    """
    def __init__(self, scope: Construct, construct_id: str, persistent_stack: PersistentStack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        environment_name = self.node.try_get_context('environment')
        self.networking = Networking(self)
        self.profile = Profile(self, 'ServerProfile', persistent_stack=persistent_stack, networking=self.networking)
        self.key_pair = ec2.CfnKeyPair(
            self, 'KeyPair',
            key_name=f'mas-{environment_name}-2',
            public_key_material=self.node.try_get_context('public_key')
        )
