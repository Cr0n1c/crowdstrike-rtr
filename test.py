from crowdstrike import Crowdstrike

# Grab these from https://falcon.crowdstrike.com/support/api-clients-and-keys
# Ensure the following permissions: host [Read], Real time response (admin) [Write], Real time response [Read, Write]
# Ensure that you have created a script called "Install-RAT" inside RTR

client_id = "xxxxxxxxxxxx"
client_secret = "yyyyyyyyyyyyyy"

c = Crowdstrike(client_id, client_secret)       # Initializes the Object
c.get_host_ids(5000)                            # Get's ALL Hosts IDs ONLY. Next stage grabs meta about a host so that you can apply filtering 
c.get_host_information()                        # Get's ALL Meta about each host. Use this information to filter for what you want.

# Let's filter on just Windows hosts and Hostnames that start with "user-"
filter_hosts = [ host.get("device_id") for host in c.hosts_metadata 
                 if host.get("platform_name") == "Windows" and (host.get("hostname").lower().startswith("user-"))
               ]

c.set_session(filter_hosts)                     # Creates the session to execute commands against
c.run_command("runscript", "runscript -CloudFile='Install-RAT' -CommandLine=''")  
