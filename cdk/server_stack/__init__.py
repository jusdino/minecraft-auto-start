from aws_cdk import Stack
from constructs import Construct

from persistent_stack import PersistentStack
from .profile import Profile


class ServerStack(Stack):
    """
    The Cfn Stack where we will keep common infrastructure items, shared across Minecraft servers
    """
    def __init__(self, scope: Construct, construct_id: str, persistent_stack: PersistentStack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.profile = Profile(self, 'ServerProfile', persistent_stack=persistent_stack)
