import cfn_resource
import boto3

handler = cfn_resource.Resource()


def validate_props(props):

    # Let's make sure we have all props we expect
    missing_props = []
    for p in ('Size', 'Zone', 'IOPS', 'Encrypted'):
        if p not in props:
            missing_props.append(p)

    if missing_props:
        return 'Missing resource properties: {}'.format(', '.join(missing_props))


@handler.create
def create_volumes(event, context):

    print(event, context)
    return

    # Get properties
    props = event['ResourceProperties']
    prop_error = validate_props(props)

    # Check if we have property errors
    if prop_error:
        return prop_error

    # Create volume
    client = boto3.client('ec2')
    client.create_volume(
        VolumeType='io1',
        Size=props['Size'],
        AvailabilityZone=props['Zone'],
        Iops=props['IOPS'],
        Encrypted=props['Encrypted'],
    )


@handler.update
def update_volumes(event, context):
    pass


@handler.delete
def delete_volumes(event, context):
    pass
