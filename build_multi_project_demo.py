#!/usr/bin/python
"""Summary: This script reads all the parameters from the k5contractsettingsV10.py file and then builds the complete environment detailed here - 
from the ground up.

CAUTION : You'll need two free projects to use this script. And the accompanying purge script obliterates everything in those projects, ensure you're happy to loose everything.
Be very careful using the purge script - there's no undo button.

Target - Fujitsu K5 IaaS Cloud Platform

Author: Graham Land
Date: 18/1/17
Twitter: @allthingsclowd
Github: https://github.com/allthingscloud
Blog: https://allthingscloud.eu

"""

from k5contractsettingsV10 import *
from k5APIwrappersV18 import *



def create_k5_infra(k5token, name, opposite_name, cidr, cidr2, project, az, ext_net, imageid, flavorid, volsize, count):
    # create first network
    name = name + "-net"
    # Create a network

    net_id = create_network(k5token, name, az , region).json()['network'].get('id')
    print "\nFirst Network ID ", net_id

    # Create a subnet

    subnet_id = create_subnet(k5token, name, net_id, 4, cidr, az, region).json()['subnet'].get('id')
    print "\nFirst Subnet ID ", subnet_id

    # create second network
    net2name = name + "2"
    # Create a network

    net_id2 = create_network(k5token, net2name, az , region).json()['network'].get('id')
    print "\nSecond Network ID ", net_id2

    # Create a subnet

    subnet_id2 = create_subnet(k5token, net2name, net_id2, 4, cidr2, az, region).json()['subnet'].get('id')
    print "\nSecond Subnet ID ", subnet_id2

    # Create a router

    router_id = create_router(k5token, name, True, az, region).json()['router'].get('id')
    print "\nRouter ID ", router_id

    # Attach first subnet to router
    add_interface = add_interface_to_router(k5token, router_id, subnet_id, region)
    print "\nFirst Subnet Added to Router  ", add_interface.json()

    # Attach second subnet to router
    add_interface2 = add_interface_to_router(k5token, router_id, subnet_id2, region)
    print "\nSecond Subnet Added to Router  ", add_interface2.json()

    add_ext_gateway = update_router_gateway(k5token, router_id, ext_net, region)
    print "\nExt Gateway ", add_ext_gateway.json()

    # Create security group
    security_group = create_security_group(k5token,  name, "Demo Security Group created by API", region).json()['security_group']
    print "\nNew Security Group created ", security_group

    sg_id = security_group.get('id')
    sg_name = security_group.get('name')

    # add rules to security group - ssh, rdp & icmp
    ssh = create_security_group_rule(k5token, sg_id, "ingress", "22", "22", "tcp", region)
    rdp = create_security_group_rule(k5token, sg_id, "ingress", "3389", "3389", "tcp", region)
    icmp = create_security_group_rule(k5token, sg_id, "ingress", "0", "0", "icmp", region)
    print "\nSecurity Group Rules Added to Security Group\nSSH\n", ssh.json(), "\nRDP\n", rdp.json(), "\nICMP\n", icmp.json()

    # create a port for interproject routing to subnet 1
    port1 = create_port(k5token, opposite_name + "-net-IPL", net_id, sg_id, az, region).json()['port']
    port1_id = port1.get('id')
    port1_ip = port1['fixed_ips'][0].get('ip_address')
    print "\nInterProject Route Port 1 created ", port1

    # create a port for interproject routing to subnet 2
    port2 = create_port(k5token, opposite_name + "-net2-IPL", net_id2, sg_id, az, region).json()['port']
    port2_id = port2.get('id')
    port2_ip = port2['fixed_ips'][0].get('ip_address')
    print "\nInterProject Route Port 2 created ", port2

    # create ssh-key pair
    newkp = create_keypair(k5token, name, project, az, region).json()['keypair']
    print "\nNew Keypair ", newkp
    newkp_id = newkp.get('id')
    newkp_pvk = newkp.get('private_key')
    newkp_pbk = newkp.get('public_key')
    newkp_name = newkp.get('name')
    print "\nPrivate Key:\n",  newkp_pvk

    # store private key details
    ServerDetails = "Private Key:\n=========\n" +str(newkp_pvk)  + "\n\nServer Details\n=========\n"

    # simple little routine to ensure only 1 global ip is assigned per group of servers
    # deploys 'count' number of servers on each subnet
    public = True
    while count > 0:
        # deploy servers on subnet 1
        NewServerSub1 = create_server(k5token, name, project, net_id, sg_id, ext_net, imageid, flavorid, newkp_name, sg_name, volsize, public, az, region, count)
        public = False
        ServerDetails = ServerDetails + str(count) + ". " + NewServerSub1 + "\n"
        # deploy servers on subnet 2
        NewServerSub2 = create_server(k5token, net2name, project, net_id2, sg_id, ext_net, imageid, flavorid, newkp_name, sg_name, volsize, public, az, region, count)
        ServerDetails = ServerDetails + str(count) + ". " + NewServerSub2 + "\n"
        count = count - 1
    ServerDetails = ServerDetails + "\n=========\n"

    return (ServerDetails, router_id, port1_id, port1_ip, port2_id, port2_ip)

def create_server(k5token, name, Projectid, net_id, sg_id, ext_net, imageid, flavorid, newkp_name, sg_name, volsize, public, az, region, count):

    name = name + "-svr" + count
    # create a port for the server
    port = create_port(k5token, name, net_id, sg_id, az, region).json()['port']
    port_id = port.get('id')
    port_ip = port['fixed_ips'][0].get('ip_address')
    global_ip = "None"

    #print k5token, name, imageid, flavorid, newkp_name, sg_name, az, volsize,  port_id, project, region

    # get a global ip for this server port
    if public:
        global_ip = create_global_ip(k5token, ext_net, port_id, az, region).json()['floatingip'].get('floating_ip_address')

    # create server
    buildserver = create_server_with_port(k5token, name, imageid, flavorid, newkp_name, sg_name, az, volsize,  port_id, Projectid, region).json()

    print "\nBuild Server Result ", buildserver
    server_id = buildserver['server'].get(id)
    #print create_server_with_port(k5token, name, imageid, flavorid, newkp_name, sg_name, az, volsize,  port_id, demoProjectid, region).json()

    #serverdetails = show_server(k5token, server_id, demoProjectid, region)

    print "\nPrivate IP:\n",  port_ip, "\nGlobal IP \n", global_ip
    return "[ "+ str(name) + " | " + str(port_ip) + " | " + str(global_ip) + "]"

def main():
    # Define some standard values, so they're not complicating things later
    ubuntuServer = "ffa17298-537d-40b2-a848-0a4d22b49df5" # This is the image to use
    p1_flavor = "1901" # This is the P-1 "flavor" code to use
    
    ProjectAk5token = get_scoped_token(adminUser, adminPassword, contract, demoProjectAid, region).headers['X-Subject-Token']
    print "Project A Scoped Token - ", ProjectAk5token

    ProjectBk5token = get_rescoped_token(ProjectAk5token, demoProjectBid, region).headers['X-Subject-Token']
    print "Project B Scoped Token - ", ProjectBk5token

    projectAcidr1 = "192.168.10.0/24"
    projectAcidr2 = "192.168.11.0/24"
    projectBcidr1 = "192.168.100.0/24"
    projectBcidr2 = "192.168.101.0/24"

    # create infrastructure for Project A and return the two interProject ports
    print "Starting build of Project A..."
    projectA = create_k5_infra(ProjectAk5token, "ProjA", projectAcidr1, projectAcidr2 ,demoProjectAid, az2, extaz2, ubuntuServer, p1_flavor, "3", 2)
    print "\nCreated Project A Infrastructure", projectA

    print "\nStarting build of Project B..."
    # create infrastructure for Project B and return the two interProject ports
    projectB = create_k5_infra(ProjectBk5token, "ProjB", projectBcidr1, projectBcidr2 ,demoProjectBid, az2, extaz2, ubuntuServer, p1_flavor, "3", 2)
    print "\nCreated Project B Infrastructure", projectB

    print "\nCreating InterProject Connection 1..."
    interProjectroute1 = inter_project_connection_create(ProjectAk5token, projectA[1], projectB[2], region)
    print "Created first interProject link ", interProjectroute1

    print "\nCreating InterProject Connection 2..."
    interProjectroute2 = inter_project_connection_create(ProjectAk5token, projectA[1], projectB[4], region)
    print "Created first interProject link ", interProjectroute2    


    staticRoutes = [{"nexthop": projectB[3], "destination": projectAcidr1},
                    {"nexthop": projectB[5], "destination": projectAcidr2 }]

    print "\nNew Static Routes ", staticRoutes

    appliedRoutes = update_router_routes(ProjectBk5token, projectB[1], staticRoutes, region)
    print "\n Applied Routes ", appliedRoutes

    print "\n Infrastructure Build Complete \n Project A Servers \n", projectA[0], "\n Project B Servers \n", projectB[0]




if __name__ == "__main__":
    main()





