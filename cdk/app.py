#!/usr/bin/env python3

from aws_cdk import core

from cdk_stack import CdkStack


app = core.App()
env = {
    'account': app.node.try_get_context("account_id"),
    'region': app.node.try_get_context("region")
}
context = {
    'account_id': app.node.try_get_context("account_id"),
    'region': app.node.try_get_context("region"),
    'kms_key_id': app.node.try_get_context("kms_key_id"),
    'servers_table_name': app.node.try_get_context("servers_table_name")
}

environment_name = app.node.try_get_context('environment')
stack_name = "mas" if environment_name == 'prod' else f'mas-{environment_name}'

tags = {
    'environment': environment_name,
    'stack_name': stack_name
}

stack = CdkStack(app, stack_name, context=context, env=env)
# tags=tags in the constructor doesn't seem to work as advertised in core.Stack docs
for k, v in tags.items():
    core.Tags.of(stack).add(k, v)

app.synth()
