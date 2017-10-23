# K5-InterProject-Demo
Fully Automated Shared Service API Deployment on Fujitsu K5

Target - Fujitsu K5 IaaS Cloud Platform

Author: Graham Land<br>
Date: 18/1/17<br>
Twitter: @allthingsclowd<br>
Github: https://github.com/allthingsclowd/K5-InterProject-Demo/<br>
Blog: https://allthingscloud.eu

The python scripts in this repository can be used to create the shared services model below auto-magically :)

![image](https://cloud.githubusercontent.com/assets/9472095/22083347/9fd53558-ddc3-11e6-88a7-b3c45a13d96a.png)

Steps:

1. Copy all these files to the same directory
2. Edit the k5contractsettingsv10.py to include your K5 contract details<br>
_Warning_: *Ensure you use two 'disposable' projects within your contract and add their names and ids to the above file. 
Every resource in these projects will get purged so ensure you're not sharing it with other users.*
3. Launch the build_multi_project_demo.py script and relax! All the SSH keys, public ips, etc are returned to the console.
  By default the script builds 2 VMs per subnet and adds a single floating ip address per poroject. You can configure the number of servers per subnet by adjusting the 'count' parameter within the script.
4. When finished playing with the routing you can use the purge_project.py to reset everything.

Happy Stacking!
