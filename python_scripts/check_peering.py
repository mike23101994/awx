import boto3

# Initialize the Boto3 EC2 client
ec2_client = boto3.client('ec2')

# Initialize the Boto3 VPC client
vpc_client = boto3.client('ec2')

# Define the EC2 instance ID, Security Group ID, Route Table ID, Subnet ID, and VPC ID
instance_id = 'your_instance_id'
security_group_id = 'your_security_group_id'
route_table_id = 'your_route_table_id'
subnet_id = 'your_subnet_id'
vpc_id = 'your_vpc_id'

# Function to check if a VPC is peered with another VPC
def is_vpc_peered(vpc_id):
    response = vpc_client.describe_vpc_peering_connections(
        Filters=[
            {
                'Name': 'status-code',
                'Values': ['active']
            },
            {
                'Name': 'accepter-vpc-info.vpc-id',
                'Values': [vpc_id]
            }
        ]
    )
    return len(response['VpcPeeringConnections']) > 0

# Function to check if a resource (e.g., instance, security group, route table, subnet) is associated with a VPC
def is_resource_in_vpc(resource_id, resource_type):
    try:
        if resource_type == 'instance':
            response = ec2_client.describe_instances(InstanceIds=[resource_id])
            vpc_id_of_resource = response['Reservations'][0]['Instances'][0]['VpcId']
        elif resource_type == 'security_group':
            response = ec2_client.describe_security_groups(GroupIds=[resource_id])
            vpc_id_of_resource = response['SecurityGroups'][0]['VpcId']
        elif resource_type == 'route_table':
            response = ec2_client.describe_route_tables(RouteTableIds=[resource_id])
            vpc_id_of_resource = response['RouteTables'][0]['VpcId']
        elif resource_type == 'subnet':
            response = ec2_client.describe_subnets(SubnetIds=[resource_id])
            vpc_id_of_resource = response['Subnets'][0]['VpcId']
        else:
            return False

        return is_vpc_peered(vpc_id_of_resource)
    except Exception as e:
        return False

# Check if the EC2 instance is part of a peered VPC
if is_resource_in_vpc(instance_id, 'instance'):
    print(f"The EC2 instance with ID {instance_id} is part of a peered VPC.")
else:
    print(f"The EC2 instance with ID {instance_id} is not part of a peered VPC.")

# Check if the Security Group is part of a peered VPC
if is_resource_in_vpc(security_group_id, 'security_group'):
    print(f"The Security Group with ID {security_group_id} is part of a peered VPC.")
else:
    print(f"The Security Group with ID {security_group_id} is not part of a peered VPC.")

# Check if the Route Table is part of a peered VPC
if is_resource_in_vpc(route_table_id, 'route_table'):
    print(f"The Route Table with ID {route_table_id} is part of a peered VPC.")
else:
    print(f"The Route Table with ID {route_table_id} is not part of a peered VPC.")

# Check if the Subnet is part of a peered VPC
if is_resource_in_vpc(subnet_id, 'subnet'):
    print(f"The Subnet with ID {subnet_id} is part of a peered VPC.")
else:
    print(f"The Subnet with ID {subnet_id} is not part of a peered VPC.")
