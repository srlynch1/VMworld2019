import boto3


def handler(context, inputs):
    client = boto3.client('route53', region_name=inputs['region'])
    response = client.change_resource_record_sets(
    HostedZoneId=inputs['zoneId'],
    ChangeBatch={
        'Comment': 'string',
        'Changes': [
            {
                'Action': "UPSERT",
                'ResourceRecordSet': {
                    'Name': inputs['name'],
                    'Type': 'A',
                    'AliasTarget': {
                            'HostedZoneId': inputs['aliasHostedZoneId'],
                            'DNSName': inputs['DNSName'],
                            'EvaluateTargetHealth': False
                        },
                }
            },
        ]
    }
)