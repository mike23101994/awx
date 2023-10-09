import sys
import boto3

def assume_role_and_check_peering(source_vpc_id, vpc_ids):
    try:
        # Initialize the STS client to assume the role
        sts = boto3.client('sts')
        
        # Assume the role
        assumed_role = sts.assume_role(
            RoleArn='arn:aws:iam::873579038761:role/Trusted-Role',
            RoleSessionName='AssumedRoleSession'
        )

        # Extract temporary credentials from the assumed role
        credentials = assumed_role['Credentials']

        # Initialize the EC2 client with the assumed role's credentials
        ec2 = boto3.client(
            'ec2',
            region_name='eu-west-1',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )

        # Initialize a dictionary to store peering status for each VPC
        peering_status = {}

        # Continue with checking VPC peering as before
        for vpc_id in vpc_ids:
            response = ec2.describe_vpc_peering_connections(
                Filters=[
                    {
                        'Name': 'requester-vpc-info.vpc-id',
                        'Values': [source_vpc_id]
                    },
                    {
                        'Name': 'accepter-vpc-info.vpc-id',
                        'Values': [vpc_id]
                    }
                ]
            )

            if response['VpcPeeringConnections']:
                peering_status[vpc_id] = "Active"
            else:
                peering_status[vpc_id] = "Inactive"
        for vpc_id, status in peering_status.items():
            print(f"VPC ID: {vpc_id}")
            print(f"VPC Peering Status: {status}")
            print("-" * 30)
        
        return peering_status

    except Exception as e:
        print(f"Error: {str(e)}")
        return {}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_vpc_peering.py <source_vpc_id> <accepter_vpc_id1> <accepter_vpc_id2> ...")
        sys.exit(1)

    source_vpc_id = 'vpc-073ff6f707df9d0f9'
    accepter_vpc_ids = sys.argv[1:]

    peering_status = assume_role_and_check_peering(source_vpc_id, accepter_vpc_ids)

    # Print the peering status for each VPC
    for vpc_id, status in peering_status.items():
        print(f"VPC ID: {vpc_id}")
        print(f"VPC Peering Status: {status}")
        print("-" * 30)
