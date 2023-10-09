import os
import boto3
import subprocess
import json

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
    # Specify the AWS region where you want to list EC2 instances
    region = 'eu-west-1'  # Change this to your desired region

    # Initialize the STS client to assume the role
    sts = boto3.client('sts')

    # Retrieve the CUSTOMER prefix from the Lambda environment variable
    customer_prefix = os.environ.get('CUSTOMER', '')

    try:
        # Assume the role
        assumed_role = sts.assume_role(
            RoleArn='arn:aws:iam::873579038761:role/Trusted-Role',
            RoleSessionName='AssumedRoleSession'
        )

        # Extract temporary credentials from the assumed role
        credentials = assumed_role['Credentials']

        # Initialize the EC2 resource client with the assumed role's credentials
        ec2 = boto3.resource(
            'ec2',
            region_name=region,
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )

        # Use the describe_instances() method to list EC2 instances
        response = ec2.instances.all()

        # Initialize a list to store instance names, VPC IDs, and private IPs
        instance_info = []

        # Print information about instances with the specified CUSTOMER prefix
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

        # If there are instances with the prefix
        if instance_info:
            # Get the unique VPC IDs
            unique_vpc_ids = set(vpc_id for _, vpc_id, _ in instance_info)

            # Call the check_vpc_peering.py script and pass the instance info and unique VPC IDs as arguments
            cmd_args = ["python", "check_vpc_peering.py"] + list(unique_vpc_ids)
            
            # Capture the output of the subprocess
            subprocess_output = subprocess.check_output(cmd_args)

            # Check if the peering status is active or not
            peering_status = "Active" in subprocess_output.decode()

            # Print the peering status
            print(f"Peering Status: {peering_status}")

            # If peering status is active, pass private IP and instance name to create_host.py
            if peering_status:
                for name, _, private_ip in instance_info:
                    subprocess.call(["python", "create_host.py", name, private_ip])

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
