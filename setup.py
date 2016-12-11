#!/usr/bin/env python2.7

import argparse
import boto3

from botocore.exceptions import ClientError

parser = argparse.ArgumentParser(description='')
parser.add_argument('stackname', metavar='STACK_NAME', help='CloudFormation stack name')
parser.add_argument('instance_type', metavar='INSTANCE_TYPE', help='Instance type (e.g., r3.8xlarge)')
parser.add_argument('zone', metavar='AVAILABILITY_ZONE', help='Availability zone (e.g., us-east-1a)')
parser.add_argument('ami', metavar='AMI', help='AMI image to use')
parser.add_argument('key_name', metavar='KEY_NAME', help='Name of EC2 key pair')
parser.add_argument('--force', action='store_true', help='Peform a stack update if stack exists')

args = parser.parse_args()

# Load template
template = open('template.yaml').read()

# CloudFormation client
client = boto3.client('cloudformation')

# Collect parameters for stack
stack_params = [
    {
        'ParameterKey': 'InstanceType',
        'ParameterValue': args.instance_type,
    },
    {
        'ParameterKey': 'AMI',
        'ParameterValue': args.ami,
    },
    {
        'ParameterKey': 'KeyName',
        'ParameterValue': args.key_name,
    },
    {
        'ParameterKey': 'Zone',
        'ParameterValue': args.zone,
    },
]

# Stack capabilities
stack_caps = ('CAPABILITY_NAMED_IAM', 'CAPABILITY_IAM')

# Create CloudFormation stack
print('Creating stack...')

do_stack_update = False
try:
    client.create_stack(
        StackName=args.stackname,
        TemplateBody=template,
        Parameters=stack_params,
        Capabilities=stack_caps
    )

    # Wait till stack is created
    waiter = client.get_waiter('stack_create_complete')
    waiter.wait(StackName=args.stackname)

except ClientError as e:

    # For force option, just try to update stack instead
    if e.response['Error']['Code'] == 'AlreadyExistsException' and args.force:
        do_stack_update = True

    # If the error is not about stack existing or we're not forcing, re-raise
    else:
        raise

# Perform a stack update if we chose to
if do_stack_update:
    print ('Stack existed, doing an update...')
    client.update_stack(
        StackName=args.stackname,
        TemplateBody=template,
        Parameters=stack_params,
        Capabilities=stack_caps
    )

    # Wait till stack is updated
    waiter = client.get_waiter('stack_update_complete')
    waiter.wait(StackName=args.stackname)

print('Done.')
