from dotenv import dotenv_values

# Use this only if running via cron
config = dotenv_values("/opt/fortigate-netbox/env_vars/.env-config")
secrets = dotenv_values("/opt/fortigate-netbox/env_vars/.env-secrets")

# Use this only if running outside of cron
# config = dotenv_values("env_vars/.env-config")
# secrets = dotenv_values("env_vars/.env-secrets")
