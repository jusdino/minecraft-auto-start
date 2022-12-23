from constructs import Construct
from aws_cdk.aws_iam import Role, IGrantable, PolicyStatement, Effect
from aws_cdk.aws_ec2 import SecurityGroup, Vpc
from aws_cdk.aws_ecs import TaskDefinition, Cluster
from aws_cdk.aws_ssm import StringParameter


class GrantingTaskDefinition(TaskDefinition):
    """
    Implementing our own TaskDefinition to make up for some feature gaps
    """
    def __init__(
            self,
            vanilla_task_definition: TaskDefinition,
            execution_role: Role
            ):
        """
        We have to implement this class as a wrapper because jsii kind of bypasses some expected inheritance behavior.
        There may be a way to reconnect inheritance and clean this up, but I haven't found it yet.
        """
        self.vanilla_task_definition = vanilla_task_definition
        self._execution_role = execution_role

    def __getattr__(self, attribute_name: str):
        return getattr(self.vanilla_task_definition, attribute_name)

    @classmethod
    def from_task_definition_arn(cls, scope: Construct, id: str, task_definition_arn: str) -> TaskDefinition:
        """
        Block invoking this method because it will yield a broken object
        """
        raise NotImplementedError

    @classmethod
    def from_task_definition_attributes(cls, *args, task_role: Role, execution_role: Role, **kwargs):
        """
        Tweaking the signature here a bit to require task_role and execution_role
        """
        task_definition = super().from_task_definition_attributes(*args, task_role=task_role, **kwargs)
        return cls(task_definition, execution_role=execution_role)

    def grant_run(self, grantable: IGrantable):
        statement = PolicyStatement(
            actions=[
                "ecs:RunTask",
                "iam:PassRole"
            ],
            effect=Effect.ALLOW,
            resources=[
                self.task_definition_arn,
                self.task_role.role_arn,
                self.execution_role.role_arn
            ]
        )
        grantable.grant_principal.add_to_policy(statement=statement)
    
    @property
    def execution_role(self) -> Role:
        """
        Special handling of execution_role because we can't provide it in the
        from_task_definition_attributes factory method.
        """
        return super().execution_role or self._execution_role


class Launcher(Construct):
    """
    Just look up existing resources until we migrate them to CDK
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        region = self.node.try_get_context('region')
        account_id = self.node.try_get_context('account_id')
        task_name = self.node.try_get_context('launcher_task_definition')
        task_role_arn = self.node.try_get_context('launcher_task_role_arn')
        execution_role_arn = self.node.try_get_context('launcher_execution_role_arn')
        cluster_name = self.node.try_get_context('launcher_cluster_name')
        security_group_id = self.node.try_get_context('launcher_security_group_id')
        vpc_name = self.node.try_get_context('vpc_name')
        parameter_name = self.node.try_get_context('launcher_network_config_parameter_name')

        security_group = SecurityGroup.from_security_group_id(
            self, 'LauncherSecurityGroup',
            security_group_id=security_group_id
        )
        vpc = Vpc.from_lookup(
            self, 'Vpc',
            vpc_name=vpc_name
        )
        task_role = Role.from_role_arn(
            self, 'TaskRole', role_arn=task_role_arn
        )
        execution_role = Role.from_role_arn(
            self, 'ExecutionRole', role_arn=execution_role_arn
        )
        self.task_definition = GrantingTaskDefinition.from_task_definition_attributes(
            self, 'LauncherTask',
            task_definition_arn=f'arn:aws:ecs:{region}:{account_id}:task-definition/{task_name}',
            task_role=task_role,
            execution_role=execution_role
        )
        self.cluster = Cluster.from_cluster_attributes(
            self, 'LauncherCluster',
            cluster_name=cluster_name,
            security_groups=[security_group],
            vpc=vpc
        )
        self.network_config_parameter = StringParameter.from_string_parameter_name(
            self, 'LauncherNetworkConfigParameter',
            string_parameter_name=parameter_name
        )
