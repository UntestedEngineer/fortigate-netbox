from pprint import pprint
from libs import fortigate
from libs import netbox
from config import config


if __name__ == "__main__":
    
    if not config['FG_HOST']:
        print("Fortigate host be set")

    elif not config['FG_USERNAME']:
        print("Fortigate username must be set")

    elif not config['FG_PASSWORD']:
        print("Fortigate password must be set")

    elif not config['NB_HOST']:
        print("Netbox host must be set")

    elif not config['NB_TOKEN']:
        print("Netbox token must be set")

    elif not config['NB_DEVICE_NAME']:
        print("Netbox device name must be set")

    # Make sure Fortigate interface exists with provided environment variable
    elif len(fortigate.get_fortigate_wan()) == 0:    
        print("Specified Fortigate interface(s) does not exist")

    else:
        # Iterate through list of WAN interfaces returned from Fortigat
        for wan in fortigate.get_fortigate_wan():
            
            fg_wan_name = wan['fg_wan_name']
            fg_wan_ip = wan['fg_wan_ip']

            pprint(f"{fg_wan_name} {fg_wan_ip}")

            nb_functions = netbox.NetboxInteraction(fg_wan_name, fg_wan_ip)

            # If Netbox interface does not exist go iterate to next WAN interface
            if (nb_functions.get_netbox_interface_ip(fg_wan_name)) == None:
                continue

            # Do not update netbox IP if Fortigate WAN IP matches Netbox assignment
            elif nb_functions.get_netbox_interface_ip(fg_wan_name)[0] == fg_wan_ip:
                print(f"Matching interface IP between Fortigate and Netbox")

            # If Netbox interface has no IP assigned create an IP and assign
            elif "Not Assigned" in nb_functions.get_netbox_interface_ip(fg_wan_name)[0]:
                print(f"Netbox {fg_wan_name} is not assigned an IP address, creating one.")
                nb_functions.create_netbox_interface_ip(fg_wan_name, fg_wan_ip)
            
            # If Netbox interface IP does not match Fortigate WAN then delete Netbox IP and create new assignment
            elif nb_functions.get_netbox_interface_ip(fg_wan_name)[0] != fg_wan_ip:
                
                old_nb_ip = nb_functions.get_netbox_interface_ip(fg_wan_name)[0]

                if "Deleted" in nb_functions.delete_netbox_interface_ip(fg_wan_name):
                    print(f"Netbox IP does not match Fortigate {fg_wan_name} interface IP")
                    print(f"Deleting {old_nb_ip} and creating new IP")
                    nb_functions.create_netbox_interface_ip(fg_wan_name, fg_wan_ip)
                
                else:
                    print(f"Problem with Netbox IP, skipping {fg_wan_name}.  Investigate manually")
                    continue

           