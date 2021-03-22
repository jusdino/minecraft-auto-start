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

CdkStack(app, "mas", context=context, env=env)

app.synth()
