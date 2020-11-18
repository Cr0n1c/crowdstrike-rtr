# crowdstrike-rtr

This is a Python3 implementation of the Crowdstrike API to automate tasks against bulk assets. The major takeaways here are that you will need to create tokens (in the GUI for now) and pass in the client_id and the client_secret. They will require Falcon RTR Administrator access (to run "any" command). To access the built in commands only, just ensure that you have Falcon RTR access.

This tool is meant as a prototype only and used in non malicious ways.

## .installation

This library is meant to be used in Python3.x and requires the "requests" library. Easiest way to install is via "pip".

    pip3 install requests

## .usage

Super easy usage!!! If you just want to use the test script then go for it, located [here]https://github.com/Cr0n1c/crowdstrike-rtr/blob/main/test.py

    from crowdstrike import Crowdstrike
    
    client_id = "xxxxxxxx" 
    client_secret = "yyyyyyyyyy"
    
    c = Crowdstrike(client_id, client_secret)

Now you have a Crowdstrike object initialized and ready to use. Next steps would be to grab all assets, the API maxes out at 5000 and I haven't implemented filtering at this stage (yet). After we get the IDs then we get the metadata about each ID so we can apply more tactful filters.

    c.get_host_ids(5000)                            # Get's ALL Hosts IDs ONLY. Next stage grabs meta about a host so that you can apply filtering 
    c.get_host_information()                        # Get's ALL Meta about each host. Use this information to filter for what you want.

Once we have this data, we can apply our own filters. In this example, let's grab just Windows systems (you can get super granular here).

    filter_hosts = [ host.get("device_id") for host in c.hosts_metadata 
                     if host.get("platform_name") == "Windows"
                   ]

Now we can create a session specific to this filtered group.

    c.set_session(filter_hosts)

Finally, let's run a command such as a directory listing.

    results = c.run_command("ls", "ls")  

Now we can iterate through the systems looking at the output.

    for k, v in results.items():
        print("\n" + ("=" * 100))
        print([i.get("hostname") for i in c.hosts_metadata if i.get("device_id") == k][0])
        print("-" * 100)
        print(v.get("stdout"))

Other things we can check is to see if any errors happened.

    for k, v in results.items():
        if v.get("errors") != [] or v.get("stderr") != "":
            for host in c.hosts_metadata:
                if host.get("device_id") == k:
                    print({"id": k, "error": v.get("errors"), "stderr": v.get("stderr"), "hostname": host.get("hostname")})

There you have it! 
        
                    
