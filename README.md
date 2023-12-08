# Fortigate Netbox

I have found there to be very little plugins or interaction between Fortigate and Netbox out there so I have started this application in hopes that it will expand in the future.  The current implementation is very limited to serve a specific purpose but will grow as time permits and contributors assist.

This application is not a plugin that integrates directly to Netbox but rather a separate program that relies on python.  It uses the fortigate_api and pynetbox pip libraries to interact with both systems.

## Current features:
- Takes the specified interface(s) on a Fortigate and creates/assigns an IP to the corresponding device + interface(s) in Netbox
  - This is particularly useful for DHCP enabled interfaces
  - Currently connecting to only one Fortigate is supported

#### Required environment variables:

**.env-config**
```
FG_HOST
FG_USERNAME
FG_WAN
NB_HOST
NB_HTTP_VERIFY
NB_DEVICE_NAME

```
**.env-secret**
```
FG_PASSWORD
NB_TOKEN
```

#### Some notes
- The FG_USERNAME should be a read-only REST API account for best security practices
- The NB_TOKEN needs to have valid read and write permissions for all IPAM and Device objects
- The FG_WAN variable is a filter so it will look for all interfaces with the name in Netbox
  - If no matching interfaces are found a message will be returned
- NB_DEVCE_NAME must be set and must be a valid device name in Netbox
- NB_HTTP_VERIFY is always false if using self-signed certificates
- Interface updates
  - If the IP address is the same between Fortigate and Netbox no updates are done
  - If the IP address in Netbox is different than Fortigate the IP address is deleted from Netbox, created new and assigned to the interface
  - If the Fortigate interface is 0.0.0.0/0 (Unassigned) the interface is skipped
  - If the Fortigate interface has no ip address assigned one is created and assigned

A sample has been provided in Fortigate-Netbox > env_vars 

## Ways to run the application
### Traditional application (non-docker)

Take the Fortigate-Netbox directory and move it to the desired server folder.  It is highly suggested to run in a venv but not required.  The requirements are located within the directory

The .env files that need to be created are referenced above.  The config and secret env file separation is required.

### Container (Kubernetes)

The application is originally designed to run in a container and developed using the python-alpine image for minimal space usage.  As I run k3s all examples are based on a Kubernetes yaml file.  An example deployment has been provided as well.  If running in docker adapt the docker-compose file as necessary.

**Create a secret for the .env-config**
```
kubectl create secret generic -n some-namespace some-secret --from-file=.env-config
```

**Create a secret for the .env-secrets**
```
kubectl create configmap -n some-namespace some-configmap --from-file=.env-config
```

## Frequency to run

The application by itself is designed to run once, however it can be run on a schedule with whatever Linux cron or daemon process that is desired.  For example to use as a crontab in a Kubernetes container create a configmap from a file with the following contents (The following example runs every 15 minutes):

**cron**
```
# min    hour     day      month    weekday    command
*/15        *        *        *        *          /opt/fortigate-netbox/bin/python3 /opt/fortigate-netbox/main.py
```

**Configmap**
```
kubectl create configmap -n some-namespace some-configmap --from-file=cron
```

Insert this configmap into the container during startup as a volumemount so that is overrides the default root crontab.