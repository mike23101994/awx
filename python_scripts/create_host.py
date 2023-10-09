import requests
import json
import sys

base_url = 'http://awx.iswcloudapp.com/api/v2'  # Base URL for the API
oauth2_token_value = '260frl1TmFPVEto2b9G3urY256xLyh'  # Your token value from controller

def get_inventory_id(token, inventory_name):
    url = f'{base_url}/inventories/'
    
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers, verify=False)

        if response.status_code == 200:
            inventories_data = response.json()
            inventory = next((inv for inv in inventories_data['results'] if inv['name'] == inventory_name), None)

            if inventory:
                return inventory['id']
            else:
                print(f"Inventory '{inventory_name}' not found.")
        else:
            print(f"Failed to retrieve inventories. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred while getting inventory ID: {str(e)}")
    
    return None

def add_host_to_inventory(token, inventory_id, host_name, host_ip, inventory_name):
    url = f'{base_url}/inventories/{inventory_id}/hosts/'
    
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    new_host_data = {
        "name": host_name,
        "description": f"A host for {inventory_name}",
        "enabled": True,
        "variables": f"ansible_host: {host_ip}"
    }

    payload = json.dumps(new_host_data)

    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)

        if response.status_code == 201:
            host_data = response.json()
            print(f"Host '{host_data['name']}' with IP '{host_data['variables']}' added successfully to inventory '{inventory_name}'.")
        else:
            print(f"Failed to add the host. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred while adding the host: {str(e)}")

def main(name, ip):

    instance_name = name
    private_ip = ip

    if "web" in instance_name:
        inventory_name = "web-inventory"
    elif "etl" in instance_name:
        inventory_name = "etl-inventory"

    inventory_id = get_inventory_id(oauth2_token_value, inventory_name)
    
    if inventory_id is not None:
        add_host_to_inventory(oauth2_token_value, inventory_id, instance_name, private_ip, inventory_name)

if __name__ == "__main__":
    main(name, ip)
