import ipaddress
from fortigate_api import FortigateAPI

import config

def get_fortigate_wan():

    # Define Fortigate connector with environment variables
    try:
        fgt = FortigateAPI(
            host=config.config['FG_HOST'], username=config.config['FG_USERNAME'], password=config.secrets['FG_PASSWORD']
        )
    
    except Exception as ex:
        print(ex)

    # Get all interfaces
    fg_interfaces = fgt.interface.get()

    FG_WAN_LIST = []

    for fg_interface in fg_interfaces:
        
        # Convert returned subnet to cidr notation
        ip_plus_subnet = fg_interface['ip'].replace(" ", "/")
        ip_plus_cidr = ipaddress.IPv4Interface(ip_plus_subnet)
          
        # Filter for only WAN interfaces as defined in the environment variable
        if config.config['FG_WAN'] in fg_interface['name']:

            # If Fortigate WAN interface has no IP assigned skip to next iteration
            if str(ip_plus_cidr) == "0.0.0.0/0":
                print(f"{fg_interface['name']} is not assigned an IP, skipping")
                continue
            
            FG_WAN_LIST.append({'fg_wan_name': fg_interface['name'], 'fg_wan_ip': str(ip_plus_cidr)})
  
    return FG_WAN_LIST
