# f5Search.py
# * Author:    Rafael Lucchesi
# * Created:   2020/08/14
# 

Goal: query a DNS/LTM source file to output hostname, DNS resolution, virtual-servers, pools and wideIPs associated with an IP address.

!Note: LTM portion under development!

Script Input: -i IP address of the target backend server
		 		-f input .csv file
				-s bigip_gtm.conf/bigip.conf path
				-o output location path
				-d disable DNS resolution

Output: 	If a single IP is provided (-i), output is displayed to the screen only.
			If a single IP (-i) and output location (-o) were provided, output is displayed to the screen and an output text file is generated.
			If a .csv file is provided (-f) with a single IP (why?!), output is displayed to the screen only.
			If a .csv file is provided (-f) with multiple IPs, output gets writen to a subfolder named "YYYYMMDD_HHMM_F5Search" only.
				Note: If the output path was not defined, the subfolder will take the script's current directory as the reference.

			Output information
			# IP DNS resolution
			# Hostname used in the F5 with their Virtual-Servers and properties
			# List of Pools that reference one of the Virtual-Servers associated with that IP
			# List of WideIPs that reference one of those Pools

#

What is an F5 BigIp Load Balancer? (wiki summary)

F5, Inc. is an American company that specializes in application services and application delivery networking (ADN). F5 technologies focus on the delivery, security, performance, and availability of web applications, including the availability of computing, storage, and network resources.

F5's BIG-IP product family comprises hardware, modularized software, and virtual appliances that run the F5 TMOS operating system. Offerings include:
* Local Traffic Manager (LTM): Local load balancing based on a full-proxy architecture.
* BIG-IP DNS: Distributes DNS and application requests based on user, network, and cloud performance conditions.

