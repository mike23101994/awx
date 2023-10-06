import requests
import json

base_url = 'http://awx.iswcloudapp.com/api/v2'  # Base URL for the API

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
            web_inv_inventory = next((inventory for inventory in inventories_data['results'] if inventory['name'] == inventory_name), None)

            if web_inv_inventory:
                return web_inv_inventory['id']
            else:
                print("Inventory 'web-inv' not found.")
        else:
            print(f"Failed to retrieve inventories. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred while getting inventory ID: {str(e)}")
    
    return None

def add_host_to_inventory(token, inventory_id, host_name, host_ip):
    url = f'{base_url}/inventories/{inventory_id}/hosts/'
    
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    new_host_data = {
        "name": host_name,
        "description": "A test host",
        "enabled": True,
        "variables": f"ansible_host: {host_ip}"
    }

    payload = json.dumps(new_host_data)

    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)

        if response.status_code == 201:
            host_data = response.json()
            print(f"Host '{host_data['name']}' with IP '{host_data['variables']}' added successfully to inventory 'web-inv'.")
        else:
            print(f"Failed to add the host. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error occurred while adding the host: {str(e)}")

def main():
    oauth2_token_value = '260frl1TmFPVEto2b9G3urY256xLyh'  # your token value from controller
    inventory_name = 'web-inv'  # Replace with the name of your inventory

    inventory_id = get_inventory_id(oauth2_token_value, inventory_name)
    
    if inventory_id is not None:
        host_name = "test-host"
        host_ip = "172.31.21.111"
        add_host_to_inventory(oauth2_token_value, inventory_id, host_name, host_ip)

if __name__ == "__main__":
    main()
