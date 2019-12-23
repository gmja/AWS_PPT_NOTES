#####################################  IAM ROLE ############################
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:*"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": "ec2:Describe*",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:CreateSnapshot",
                "ec2:DeleteSnapshot",
                "ec2:CreateTags",
                "ec2:ModifySnapshotAttribute",
                "ec2:ResetSnapshotAttribute"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}


#####################################  Create EBS snapshot all region ###########################
# Backup all in-use volumes in all regions

import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    # Get list of regions
    regions = ec2.describe_regions().get('Regions',[] )

    # Iterate over regions
    for region in regions:
        print "Checking region %s " % region['RegionName']
        reg=region['RegionName']

        # Connect to region
        ec2 = boto3.client('ec2', region_name=reg)
    
        # Get all in-use volumes in all regions  
        result = ec2.describe_volumes( Filters=[{'Name': 'status', 'Values': ['in-use']}])
        
        for volume in result['Volumes']:
            print "Backing up %s in %s" % (volume['VolumeId'], volume['AvailabilityZone'])
        
            # Create snapshot
            result = ec2.create_snapshot(VolumeId=volume['VolumeId'],Description='Created by Lambda backup function ebs-snapshots')
        
            # Get snapshot resource 
            ec2resource = boto3.resource('ec2', region_name=reg)
            snapshot = ec2resource.Snapshot(result['SnapshotId'])
        
            volumename = 'N/A'
        
            # Find name tag for volume if it exists
            if 'Tags' in volume:
                for tags in volume['Tags']:
                    if tags["Key"] == 'Name':
                        volumename = tags["Value"]
        
            # Add volume name to snapshot for easier identification
            snapshot.create_tags(Tags=[{'Key': 'Name','Value': volumename}])
			
###############################

Ref Link : https://www.codebyamir.com/blog/automated-ebs-snapshots-using-aws-lambda-cloudwatch