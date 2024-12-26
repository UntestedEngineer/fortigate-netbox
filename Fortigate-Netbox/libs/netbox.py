import pynetbox
from pprint import pprint

import config

class NetboxInteraction:
            
    # Define Netbox connector with environment variables
    try:
        nb = pynetbox.api(
        config.config['NB_HOST'], token=config.secrets['NB_TOKEN']
        )

    except Exception as ex:
        print(ex)
        
    def __init__(self, fg_wan_name, fg_wan_ip):
        self.fg_wan_name = fg_wan_name
        self.fg_wan_ip = fg_wan_ip

    # Validate whether HTTP is set to true or false.  Must be set to false for self-signed certificates
    def validate_http_verify(self):
        if config.config['NB_HTTP_VERIFY'].lower() != "true" and config.config['NB_HTTP_VERIFY'].lower() != "false":
            print(f"Netbox HTTP verify must be true or false")

            return
        
        else:
            self.nb.http_session.verify = eval(config.config['NB_HTTP_VERIFY'])
        
    # Get Netbox IP for further processing
    def get_netbox_interfaces(self, fg_wan_name):

        self.validate_http_verify()

        nb_interfaces = []

        # Retrieve WAN interfaces name from Fortigate library for query
        nb_interfaces = self.nb.dcim.interfaces.filter(device=config.config['NB_DEVICE_NAME'], name=fg_wan_name)

        return nb_interfaces
          
    def get_netbox_interface_ip(self, fg_wan_name):

        # Check for non-existent interface in netbox
        if len(self.get_netbox_interfaces(fg_wan_name)) == 0:
            print(f"Netbox interface does not exist, skipping")
            return            

        NB_FG_WAN_IP = {}

        # Iterate through paramters of interfaces that are returned
        for self.nb_interface in self.get_netbox_interfaces(fg_wan_name):       
        
            try:
                nb_ip_addresses = self.nb.ipam.ip_addresses.get(interface_id=self.nb_interface.id)

            except Exception as ex:
                print("Error", ex)

            # Condition to match if interface is not assigned
            if nb_ip_addresses == None:
                NB_FG_WAN_IP['address'] = "Not Assigned"
                NB_FG_WAN_IP['id'] = "Not Assigned"
            
            else:
                # Convert returned tuple data to dictionary
                nb_wan_ip = dict((x, y) for x, y in nb_ip_addresses)

                NB_FG_WAN_IP['address'] = nb_wan_ip['address']
                NB_FG_WAN_IP['id'] = nb_wan_ip['id']

            return [NB_FG_WAN_IP['address'], NB_FG_WAN_IP['id']]
    
    def create_netbox_interface_ip(self, fg_wan_name, fg_wan_ip):
        
        self.validate_http_verify()

        # # Detect VRF ID, default is none (Global table)
        # nb_vrf = os.getenv('NB_VRF_ID')
        
        # if os.getenv('NB_VRF_ID') == "":
        #     nb_vrf = None
        
        # Loop through interfaces and add IPs while assigning the interface at the same time
        for self.nb_interface in self.get_netbox_interfaces(fg_wan_name):
            try:
                nb_create_ip = self.nb.ipam.ip_addresses.create(
                    address=fg_wan_ip,
                    tenant=config.config['NB_TENANT_ID'],
                    assigned_object_type="dcim.interface",
                    assigned_object_id=self.nb_interface.id
                    )     
                    
            except Exception as ex:
                print(ex)
                
            else:
                pprint(dict(nb_create_ip))
        return

    # Delete existing Netbox IP address
    def delete_netbox_interface_ip(self, fg_wan_name):
         
        self.validate_http_verify()
  
        try:
            nb_delete_ip = self.nb.ipam.ip_addresses.get(id=self.get_netbox_interface_ip(fg_wan_name)[1])
            nb_delete_ip.delete()
                
        except Exception as ex:
            print(ex)

        else:
            return f"Deleted {nb_delete_ip}"

        return