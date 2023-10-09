import os
import boto3
import subprocess
import json
from create_host import main

def get_instance_vpc_id(ec2, instance_id):
    try:
        instance = ec2.Instance(instance_id)
        return instance.vpc_id
    except Exception as e:
        print(f"Error getting VPC ID for {instance_id}: {str(e)}")
        return None

def get_instance_private_ip(ec2, instance_id):
    try:
        instance = ec2.Instance(instance_id)
        return instance.private_ip_address
    except Exception as e:
        print(f"Error getting private IP for {instance_id}: {str(e)}")
        return None

def lambda_handler(event, context):
   
    region = 'eu-west-1'  # Change this to your desired region

    sts = boto3.client('sts')
    customer_prefix = os.environ.get('CUSTOMER', '')

    try:

        assumed_role = sts.assume_role(
            RoleArn='arn:aws:iam::873579038761:role/Trusted-Role',
            RoleSessionName='AssumedRoleSession'
        )


        credentials = assumed_role['Credentials']

        ec2 = boto3.resource(
            'ec2',
            region_name=region,
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )

        response = ec2.instances.all()

        instance_info = []

        for instance in response:
            instance_id = instance.id
            instance_name = ''
            vpc_id = get_instance_vpc_id(ec2, instance_id)
            private_ip = get_instance_private_ip(ec2, instance_id)
            

            # Get the instance name tag if available
            for tag in instance.tags or []:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']

            # Check if the instance name starts with the specified CUSTOMER prefix
            if instance_name.startswith(customer_prefix):
                instance_info.append((instance_name, vpc_id, private_ip))
                print(f'{instance_info}')

        # If there are instances with the prefix
        if instance_info:
            # Get the unique VPC IDs
            unique_vpc_ids = set(vpc_id for _, vpc_id, _ in instance_info)

            cmd_args = ["python", "check_vpc_peering.py"] + list(unique_vpc_ids)
            
            subprocess_output = subprocess.check_output(cmd_args)

            peering_status = "Active" in subprocess_output.decode()

            print(f"Peering Status: {peering_status}")

            # If peering status is active, pass private IP and instance name to create_host.py
            if peering_status:
                for name, _, private_ip in instance_info:
                    #subprocess.run(["python3", "create_host.py", name, private_ip])
                    main(name,private_ip)

        return {
            'statusCode': 200,
            'body': 'EC2 instances listed successfully.'
        }

    except Exception as e:
        # Handle any errors that may occur
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
