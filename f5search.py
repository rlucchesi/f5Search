# 
# * Author:    Rafael Lucchesi
# * Created:   2020/08/14
#
# Goal: query a GTM/LTM source file to output hostname, DNS resolution, virtual-servers, pools and wideIPs associated with an IP address.
#
# !Note: LTM portion under construction!
#
# Script Input: -i IP address of the target backend server
#		 		-f input .csv file
#				-s bigip_gtm.conf/bigip.conf path
#				-o output location path
#
# Output: 	If a single IP was provided (-i), output is displayed to the screen.
#			If a .csv file was provided, output gets writen to a subfolder named "YYYYMMDD_HHMM_F5Search".
#			If the output path was not defined, the subfolder will take the script's current directory as the reference.
#
#			# IP DNS resolution
#			# Hostname used in the F5 (and their Virtual-Servers)
#			# List of Pools that list those Virtual-Servers
#			# List of WideIPs that list those Pools
#
############################################################################################################################################

import pdb
# pdb.set_trace()
import os
# os.getcwd()
from random import randint
# randint(start,finish)
from datetime import datetime
# now = datetime.now()
# dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
import sys
import pandas as pd

# allow STDIN input
#for line in sys.stdin:
#    print(line)

#####################
### Variables
#####################

# Script help string
helpStrList = [ "", "Search F5 database based on IP addresses.",
 "Usage: F5_backendSearch -s filepath -i/f ip_address/input csv file [-o outputPath]", "", "Options:",
  "	ip_address	ip address of a backend server. Outputs to screen if a single IP is provided",
   "	-s		source file location (bigip_gtm.conf / bigip.conf)", "	-i		single target ip address",
    "	-f		csv file name/location (1 IPv4 per line, starting at A2)",
     "	-g		generates a template csv file to be used as input file (./myBook.csv)",
      "	-o		output directory location (ip_address.txt output file per node)", "	-h		show help", ""]

# List of nodes to be searched
inputNodeList = [ ]

# List to hold F5 source file contents
f5SourceList = [ ]

# csv file path/location
ui_CsvStr = str()

# F5 source file location (bigip_gtm.conf / bigip.conf)
ui_f5SourceLocationStr = str()

# User defined output directory
ui_outputPathStr = str()

# List holding objects to be outputed
scriptOutputObjList = [ ]


#####################
### Script Functions
#####################
def localDateTime(isDirPar = 0):
	"""
	Produces a string with the current date and time
	"""
	now = datetime.now()
	if isDirPar == 0:
		# dd/mm/YY H:M:S
		return now.strftime("%d/%m/%Y %H:%M:%S")
	else:
		# yyyymmdd_hhmm_f5Search
		return now.strftime("%Y%m%d_%H%M_f5Search")

def printHelp():
	for i in helpStrList:
		print(i)

def trimString(inputStrPar, delimiterPar, wantedPortionPar):
	"""
	Trim a string based on a delimiter and returns the specified portion of it
	input: 	inputStrPar, string to be trimmed/divided
			delimiterPar, character used to divide the string in multiple portions
			wantedPortionPar, (starts at 0) integer that tells the function which part of the string is wanted
	"""
	tempList = inputStrPar.split(delimiterPar)
	return tempList[wantedPortionPar]

def splitOnOccurrence(inputStrPar, delimiterPar, occurPositionPar):
	"""
	Split a string on the determined occurrence of a character and returns a string with everything after it.
	input:	inputStrPar, string to be trimmed/divided
			delimiterPar, character used to divide the string in multiple portions
			occurPositionPar, number to determine on which occurrence of delimiterPar the inputStr must be split
	"""
	tempList = inputStrPar.split(delimiterPar) 
	return delimiterPar.join(tempList[occurPositionPar:]) 

def genCsv():
	"""
	Generates a csv template to be used as input file by the script
	input: none
	output: myBook.csv, csv template file
	"""
	df = pd.DataFrame({'ipAddress_begin@A2': ['10.0.0.0', '10.0.0.1', '...']})
	df.to_csv(r'myBook.csv', encoding='utf-8', index = False)


def readInput():
	"""
	Deal with user input.
	input: 	inputNodeList[input], an IPv4 address
			ui_CsvStr, csv file location with indefinite number of records
	output: inputNodeList, dictionary of input IPv4 addresses
	"""
	global inputNodeList
	global ui_f5SourceLocationStr
	global ui_CsvStr
	global ui_outputPathStr
	isIp = 0
	isFile = 0
	isOutput = 0
	isSource = 0
	for input in sys.argv[1::]:
		try:
			if input[0] == "-":
				if input[1] == "g":
					print("Template input csv file generated (./myBook.csv)")
					genCsv()
					return False
				elif input[1] == "f":
					if isIp == 0:
						isFile += 1
				elif input[1] == "i":
					if isFile == 0:
						isIp += 1
				elif input[1] == "o":
					isOutput += 1
				elif input[1] == "s":
					isSource += 1
				else:
					raise
			elif isIp == 1 and isFile == 0 and input[0].isnumeric():
				inputNodeList.append(input)
				isIp += 1
			elif isFile == 1 and isIp == 0:
				ui_CsvStr = input
				isFile += 1
			elif isOutput == 1:
				ui_outputPathStr = input
				isOutput += 1
			elif isSource == 1:
				ui_f5SourceLocationStr = input
				isSource += 1
			else:
				raise
		except:
			printHelp()

	## return True
	# if source and ip are given
	if isSource >= 1 and isIp != isFile:
	 	return True
	# if source, csv and output path are given
	#elif isSource >= 1 and isIp < isFile and isOutput >= 1:
	#	return True
	else:
		printHelp()
		return False


def readCsv(filePathStrPar):
	"""
	Read contents of an input csv file
	input: filePathStrPar, a string contaning the csv file location
	output: list, a list with the IP address(es) in the csv file
	"""
	# build data frame
	df = pd.read_csv(filePathStrPar)
	# return contents of column 0
	return list(df[df.columns[0]])
	############################################################# check and only insert valid IPv4 addresses


def readF5Source(sourceFilePathPar):
	"""
	Loads the contents of an F5 source file (bigip_gtm.conf / bigip.conf) into memory
	input: sourceFilePathPar, a string contaning the F5 source file location
	output: list, a list with the contents of the source file
	"""
	# build data frame
	df = pd.read_csv(sourceFilePathPar, engine='python', delimiter="\r\n", header=None)
	# return contents of column 0
	return list(df[df.columns[0]])


def genOutputPath(ui_outputPathStrPar):
	"""
	Generates the output path string to be used to write results to memory (Windows and Unix compatible)
	input: ui_outputPathStrPar, a string contaning the prefered output file location (user input)
	output: outputPath, a string with the processed absolute path
	"""
	outputPath = str()

	## produce file output path
	# if Windows file system
	if os.name == 'nt':
		## build system output path portion
		# if output path is N/A or relative
		if len(ui_outputPathStrPar) == 0 or ui_outputPathStrPar[0] == '.':
			outputPath = os.getcwd()
			if len(ui_outputPathStrPar) > 2:
				# if relative path
				if outputPath[-1] == '\\':
					outputPath += ui_outputPathStrPar[2::]
				else:
					outputPath += ui_outputPathStrPar[1::]
		# else output path is absolute or a subdir name
		else:
			# absolute path
			if len(ui_outputPathStrPar) > 1 and ui_outputPathStrPar[1] == ':':
				outputPath = ui_outputPathStrPar
			# subdir name
			else:
				outputPath = os.getcwd()
				outputPath += ui_outputPathStrPar
					
		## add custom folder name to output path
		# add backward slash to the end of the output path if missing
		if outputPath[-1] != '\\':
			outputPath += '\\'	
		outputPath += localDateTime(1) + '\\'

	# else: unix compatible file system
	else:
		## build system output path portion
		# if output path is N/A or relative
		if len(ui_outputPathStrPar) == 0 or ui_outputPathStrPar[0] == '.':
			outputPath = os.getcwd()
			# if relative path
			if len(ui_outputPathStrPar) > 1:
				if outputPath[-1] == '/':
					outputPath += ui_outputPathStrPar[2::]
				else:
					outputPath += ui_outputPathStrPar[1::]
		# else output path is absolute or a subdir name
		else:
			# absolute path
			if ui_outputPathStrPar[0] == '/':
				outputPath = ui_outputPathStrPar
			# subdir name
			else:
				outputPath = os.getcwd()
				outputPath += '/' + ui_outputPathStrPar
					
		## add custom folder name to output path
		# add backward slash to the end of the output path if missing
		if outputPath[-1] != '/':
			outputPath += '/'	
		outputPath += localDateTime(1) + '/'

	return outputPath


def getOutput(scriptOutputObjListPar, ui_outputPathStrPar):
	"""
	Generates the output path string to be used to write results to memory (Windows and Unix compatible)
	input: ui_outputPathStrPar, a string contaning the prefered output file location (user input)
	output: outputPath, a string with the processed absolute path
	"""
	outputPath = str()
	fileAbsPathStr = str()
	singleItemList = [ ]

	# if single IP input, print output to the screen
	if len(inputNodeList) < 2:
		# produce stdout output
	 	for line in scriptOutputObjListPar:
	 		print(line)
	# else create output subdir and txt files
	else:
		# build outputPath directory
		outputPath = genOutputPath(ui_outputPathStrPar)
		try:
			# create dir
			os.mkdir(outputPath, mode=0o777, dir_fd=None)
			# write to output file
			## append instead of write?!
			for item in scriptOutputObjListPar:
				if type(item) == type(str()):
					lineList = item.split(" ")
					# if new IP address, create new file
					if lineList[0] == '========' and lineList[2] == '========':
						fileAbsPathStr = outputPath + lineList[1] + '.txt'
						# write to a new filehandle
						with open(fileAbsPathStr, 'w') as filehandle:
							filehandle.write('%s\n' % item)
					# else append to current filehandle
					else:
						with open(fileAbsPathStr, 'a') as filehandle:
							filehandle.write('%s\n' % item)
				else:
					# pdb.set_trace()
					singleItemList.append(str(item))
					for line in singleItemList:
						# append to current filehandle
						with open(fileAbsPathStr, 'a') as filehandle:
							filehandle.write('%s\n' % line)
					singleItemList.clear()
		except FileExistsError:
			outputPath += outputPath + str(randint(0,9))
	
	# create summary file (only server/pool/wideip names)

	return True


def printStrDict(dictPar):
	"""
	[Debug] Function used to print contents of a Dict that holds strings as values
	input: dictPar, a Dict that holds a string as the value
	output: prints to stdOut the "Key -> value" pair
	"""
	output = str()
	for k in dictPar.keys():
		output = output + k + " -> " + dictPar[k] + "\n"
	print(output)


def printListDict(dictPar):
	"""
	[Debug] Function used to print contents of a Dict that holds a List of strings as values
	input: dictPar, a Dict that holds a List of strings as values
	output: prints to stdOut the "Key -> value" pair. Each value is casted into a string, separating each index content with a comma ', '.
	"""
	output = str()
	for k in dictPar.keys():
		output = output + k + " -> " + (', '.join(dictPar[k])) + "\n"
	print(output)


def printInputPath(self):
	"""
	[Debug] Output the .csv file path entered by the user
	"""
	print ("printInputPath:", ui_CsvStr)

def printOuputPath(self):
	"""
	[Debug] Output the output file path entered by the user
	"""
	print("printOuputPath:", ui_outputPathStr)


#####################
### Class Definitions
#####################
class gtmServer (object):
	"""
	F5 GTM Server blueprint constructor. Builds server objects into memory for processing.
	"""
	def __init__(self, nameStrPar, ipAddrStrPar, datacenterStrPar, monitorListPar, productStrPar, vsdiscoveryStrPar, **vsDictPar):
		"""
		backend server constructor
		input: 	device-name (str)
				ip address (str)
				data center (str)
				monitor (str)
				product (str)
				virtual server discovery (str)
				virtual servers (dictionary)
		"""
		self.__devicename = nameStrPar
		self.__ipAddress = ipAddrStrPar
		self.__datacenter = datacenterStrPar
		self.__monitor = monitorListPar
		self.__product = productStrPar
		self.__vsDiscovery = vsdiscoveryStrPar
		# { name : destination (ip:port) }
		self.__virtualServers = vsDictPar

	def __str__(self):
		"""
		print method override
		"""
		vsOutput = str()
		vsKeys = self.__virtualServers.keys()
		for vsK in vsKeys:
			vsOutput += '\t\t' + str(vsK) + " | " + (', '.join(self.__virtualServers[vsK])) + '\n'
		if len(vsOutput) == 0:
			vsOutput = "\t\tNone\n"
		if len(self.__monitor) == 0:
			self.__monitor.append("None")
		return "\ngtm backend server name: " + self.__devicename + "\n\tIP address: " + self.__ipAddress + \
		"\n\tDatacenter: " + self.__datacenter + "\n\tMonitor: " + (', '.join(self.__monitor)) + "\n\tProduct: " + self.__product + \
		"\n\tVirtual-server-discovery: " + self.__vsDiscovery + "\n\tVirtual-Servers: \n" + vsOutput + "\n----"

	def getVsNameList(self):
		"""
		returns a list of virtual servers
		"""
		myOutputList = [ ]
		vsKeys = self.__virtualServers.keys()
		for vsK in vsKeys:
			myOutputList.append(vsK)
		return myOutputList


class gtmPool (object):
	"""
	F5 GTM Pool blueprint constructor. Builds pool objects into memory for processing.
	"""
	# Constructor
	def __init__(self, nameStrPar, alternateModeStrPar, dynamicRatioStrPar, fallbackIPStrPar, fallbackModeStrPar, lbModeStrPar, \
		verifyMemberAvailabilityStrPar, ttlStrPar, monitorListPar, **membersDictPar):
		self.__name = nameStrPar
		self.__alternateMode = alternateModeStrPar
		self.__dynamicRatio = dynamicRatioStrPar
		self.__fallbackIP = fallbackIPStrPar
		self.__fallbackMode = fallbackModeStrPar
		self.__lbMode = lbModeStrPar
		self.__verifyMemberAvailability = verifyMemberAvailabilityStrPar
		self.__ttl = ttlStrPar
		self.__monitor = monitorListPar
		# { member (server:vs) : details }
		self.__members = membersDictPar

	def __str__(self):
		"""
		print method override
		"""
		membersOutput = str()
		membersKeys = self.__members.keys()
		for memberK in membersKeys:
			membersOutput += '\t\t' + str(memberK) + " | " + (', '.join(self.__members[memberK])) + '\n'
		if len(membersOutput) == 0:
			membersOutput = "\t\tNone\n"
		if len(self.__monitor) == 0:
			self.__monitor.append("None")
		return "\ngtm pool name: " + self.__name + "\n\tAlternateMode: " + self.__alternateMode + \
		"\n\tDynamic Ratio: " + self.__dynamicRatio + "\n\tFallback IP: " + self.__fallbackIP + \
		"\n\tFallback Mode: " + self.__fallbackMode + "\n\tLoad Balancing Mode: " + self.__lbMode + \
		"\n\tVerify Member Availability: " + self.__verifyMemberAvailability + "\n\tTTL: " + str(self.__ttl) + \
		"\n\tMonitor: \n\t\t" + (', '.join(self.__monitor)) + '\n\tMembers (server:vs): \n' + membersOutput + "\n----"


class gtmWideIp (object):
	"""
	F5 GTM wideIp blueprint constructor. Builds wideIP objects into memory for processing.
	"""
	# Constructor
	def __init__(self, nameStrPar, descriptionStrPar, lastResortPoolStrPar, persistenceStrPar, poolLbModeStrPar, \
		ttlPersistenceStrPar, aliasesListPar, rulesListPar, **poolsDictPar):
		self.__name = nameStrPar
		self.__description = descriptionStrPar
		self.__lastResortPool = lastResortPoolStrPar
		self.__persistence = persistenceStrPar
		self.__poolLBmode = poolLbModeStrPar
		self.__ttlPersistence = ttlPersistenceStrPar
		self.__aliases = aliasesListPar
		self.__rules = rulesListPar
		# { pool name : details }
		self.__pools = poolsDictPar

	def __str__(self):
		"""
		print method override
		"""
		poolsOutput = str()
		poolsKeys = self.__pools.keys()
		for poolsK in poolsKeys:
			poolsOutput += '\t\t' + str(poolsK) + " | " + (', '.join(self.__pools[poolsK])) + '\n'
		if len(poolsOutput) == 0:
			poolsOutput = "\t\tNone\n"
		if len(self.__aliases) == 0:
			self.__aliases.append("None")
		if len(self.__rules) == 0:
			self.__rules.append("None")
		return "\ngtm wideip name: " + self.__name + "\n\tDescription: " + self.__description + \
		"\n\tLast Resort Pool: " + self.__lastResortPool + "\n\tPersistence: " + self.__persistence + \
		"\n\tPool Load Balancing Mode: " + self.__poolLBmode + "\n\tTTL Persistence: " + self.__ttlPersistence + \
		"\n\tAliases: \n\t\t" + (', '.join(self.__aliases)) + "\n\tRules: \n\t\t" + (', '.join(self.__rules)) + \
		'\n\tPools: \n' + poolsOutput + "\n----"

class F5gtm (object):
	"""
	F5 GTM blueprint constructor. Builds several dictionaries to put relevant info in memory for processing.
	"""
	# Constructor
	def __init__(self):
		## List of objects
		# Dictionary { key == server name : value == gtmServer object }
		self.__server = { }
		# Dictionary { key == pool name : value == gtmPool object }
		self.__pool = { }
		# Dictionary { key == wideip name : value == gtmWideIp object }
		self.__wideip = { }
		
		## Search dicts: used to hold keys to the server/pool/wideip Dicts, allowing the script to quickly efficiently browse through needed data.
		# Dictionary { key == IP address Str : value == gtmServer name Str }
		self.__ipServer = { }
		# Dictionary { key == server:vsname : value == list of gtmPools that contains it }
		self.__memberPool = { }
		# Dictionary { key == pool name : value == list of gtmWideIp that references it }
		self.__poolWideip = { }
		# Dictionary { key == wideIP : value == list of pool(s) referenced by it }
		self.__wideipPool = { }


	def load(self, f5SourceListArg):
		"""
		Loads F5 source file contents into memory, creating server, pool and wideip objects with their respective properties.
		input: 	f5SourceListArg, F5 source file contents converted into a List (array).
		output:	Function returns no output; however, it allows the script to manipulate the objects by populating the /
				following dictionaries within the object instance (self): self.__server, self.__pool, self.__wideip, /
																		  self.__ipServer, self.__memberPool, /
																		  self.__poolWideip, self.__wideipPool
		"""
		### Variables
		## file iteration
		# index to determine which block is being parsed
		curlyCount = 0
		# Lists to manipulate strings
		lineList = [ ]

		# block flags
		isServer = 0
		isAddresses = 0
		isVS = 0
		isPool = 0
		isPoolMember = 0
		isWideip = 0
		isWideipPools = 0
		w_isAlias = 0
		w_isRule = 0
		
		## temporary variables to hold object arguments
		# server/pool/wideip
		tmp_nameStr = str()
		tmp_monitorList = [ ]
		tmp_dictKeyStr = str()
		tmp_dictValuesList = [ ]
		tmp_dict = { } # [ dictKeyStr : dictValuesList ]
		
		# server only
		s_ipAddrList = [ ]
		s_datacenter = str()
		s_product = str()
		s_vsDiscovery = "disabled"

		# pool only
		p_alternateMode = "none"
		p_dynamicRatio = "disabled"
		p_fallbackIp = str()
		p_fallbackMode = str()
		p_lbMode = str()
		p_verifyMemberAvailability = "enabled"
		p_ttl = 30

		# wideIP only
		w_descriptionStr = str()
		w_lastResortPoolStr = str()
		w_persistenceStr = str()
		w_poolLBmodeStr = str()
		w_ttlPersistenceStr = str()
		w_aliasesList = [ ]
		w_rulesList = [ ]

		# iterate the List containing each line (string) of the Source file
		for lineStr in f5SourceListArg:
			if lineStr[-1] == '{':
				curlyCount += 1
			elif lineStr[-1] == '}':
				if curlyCount > 0:
					curlyCount -= 1
			
			# convert the line string into a list divided by whispaces
			lineList = lineStr.split(" ")

			#print(str(curlyCount) + " : " + lineStr)

			# determine which block is being parsed
			if curlyCount == 1:
				if len(lineList) > 1:
					if lineList[0] == "gtm":
						## set flag, extract and save block name (server/pool/wideip)
						if lineList[1] == "server":
							isServer = 1
						elif lineList[1] == "pool":
							isPool = 1
						else:
							isWideip = 1
						tmp_nameStr = splitOnOccurrence(lineStr, "/", 2)
						tmp_nameStr = trimString(tmp_nameStr, " ", 0)
					elif lineList[0] == "monitor":
						## extract and save monitor list
						# remove the "monitor" string
						lineList.remove("monitor")
						# remove any number of "and" string instances
						while (any("and" in i for i in lineList)):
							lineList.remove("and")
						# trim monitor name
						for i, monitor in enumerate(lineList):
							lineList[i] = splitOnOccurrence(monitor, "/", 2)
						# store monitor(s) List
						tmp_monitorList = lineList
					elif isServer == 1:
						## parse server properties
						if lineList[0] == "datacenter":
							s_datacenter = splitOnOccurrence(lineStr, "/", 2)
						elif lineList[0] == "product":
							s_product = lineList[1]
						elif lineList[0] == "virtual-server-discovery":
							s_vsDiscovery = lineList[1]
					elif isPool == 1:
						## parse pool properties
						if lineList[0] == "alternate-mode":
							p_alternateMode = lineList[1]
						elif lineList[0] == "dynamic-ratio":
							p_dynamicRatio = lineList[1]
						elif lineList[0] == "fallback-ip":
							p_fallbackIp = lineList[1]
						elif lineList[0] == "fallback-mode":
							p_fallbackMode = lineList[1]
						elif lineList[0] == "load-balancing-mode":
							p_lbMode = lineList[1]
						elif lineList[0] == "verify-member-availability":
							p_verifyMemberAvailability = lineList[1]
						elif lineList[0] == "ttl":
							p_ttl = lineList[1]
					elif isWideip == 1:
						## parse wideip properties
						if lineList[0] == "pool-lb-mode":
							w_poolLBmodeStr = lineList[1]
						elif lineList[0] == "persistence":
							w_persistenceStr = lineList[1]
						elif lineList[0] == "ttl-persistence":
							w_ttlPersistenceStr = lineList[1]
						elif lineList[0] == "last-resort-pool":
							#w_lastResortPoolStr = trimString(lineStr, "/", 2)
							w_lastResortPoolStr = splitOnOccurrence(lineStr, "/", 2)
						elif lineList[0] == "description":
							w_descriptionStr = lineList[1]
				elif isVS == 1:
					isVS = 0
				elif isPoolMember == 1:
					isPoolMember = 0
				elif isAddresses == 1:
					for addr in s_ipAddrList:
						# add ip <-> server name relation to the dictionary
						self.__ipServer[addr] = tmp_nameStr
					isAddresses = 0
				elif isWideipPools == 1:
					isWideipPools = 0
				elif w_isAlias == 1:
					w_isAlias = 0
				elif w_isRule == 1:
					w_isRule = 0
			elif curlyCount == 2:
				if len(lineList) > 1:
					if lineList[0] == "virtual-servers":
						isVS = 1
					elif lineList[0] == "members":
						isPoolMember = 1
					elif lineList[0] == "addresses":
						isAddresses = 1
					elif lineList[0] == "pools":
						isWideipPools = 1
					elif lineList[0] == "aliases":
						w_isAlias = 1
					elif lineList[0] == "rules":
						w_isRule = 1
				else:
					if isVS == 1 or isPoolMember == 1 or isWideipPools == 1:
						# closing a virtual-server/pool member/wideip: write to memory and reset valuesList before moving forward
						tmp_dict[tmp_dictKeyStr] = tmp_dictValuesList[:]
						tmp_dictValuesList.clear()
					elif w_isAlias == 1:
						if lineStr != "}":
							# if lineStr is a valid alias name, add to the list
							w_aliasesList.append(lineStr)
					elif w_isRule == 1:
						w_rulesList.append(splitOnOccurrence(lineStr, "/", 2))
			elif curlyCount == 3:
				if isAddresses == 1 and lineStr[0].isnumeric():
					# add IP to the server address List
					s_ipAddrList.append(trimString(lineStr, " ", 0))
				elif isVS == 1:
					if lineStr[-1] == '{':
						# extract and save virtual-server name
						if lineStr[0] == "/":
							lineStr = splitOnOccurrence(lineStr, "/", 2)
						tmp_dictKeyStr = trimString(lineStr, " ", 0)
					else:
						# save extra details as virtual-server values
						if lineList[0] == "monitor":
							# trim virtual-server monitor name
							lineStr = splitOnOccurrence(lineStr, "/", 2)
							lineStr = "monitor " + lineStr
						tmp_dictValuesList.append(lineStr)
				elif isPoolMember == 1:
					if lineStr[-1] == '{':
						# extract/trim pool member name
						lineStr = splitOnOccurrence(lineStr, "/", 2)
						lineStr = trimString(lineStr, " ", 0)
						
						# create needed member dict containing empty list if not there already
						if lineStr not in self.__memberPool:
							self.__memberPool[lineStr] = [ ]
						# add member (server:virtual-server) <-> pool name relation to the dictionary
						self.__memberPool[lineStr].append(tmp_nameStr)

						# save member ID (server:vs) to be used as a Dict key
						tmp_dictKeyStr = lineStr
					elif lineList[0] == "member-order":
						tmp_dictValuesList.insert(0, lineStr)
					else:
						# add random details to the List of member values
						tmp_dictValuesList.append(lineStr)
				elif isWideipPools == 1:
					if lineStr[-1] == '{':
						# extract/trim pool name
						lineStr = splitOnOccurrence(lineStr, "/", 2)
						lineStr = trimString(lineStr, " ", 0)

						## Add pool <-> wideip relation
						# create needed wideip dict containing empty list if not there already
						if tmp_nameStr not in self.__wideipPool:
							self.__wideipPool[tmp_nameStr] = [ ]
						# add pool name to the wideip dict value list
						self.__wideipPool[tmp_nameStr].append(lineStr)

						# create pool dict and append wideip to the contained list
						if lineStr not in self.__poolWideip:
							self.__poolWideip[lineStr] = [ ]
						self.__poolWideip[lineStr].append(tmp_nameStr)

						# save pool name to be used as a Dict key
						tmp_dictKeyStr = lineStr
					elif lineList[0] == "order":
						tmp_dictValuesList.insert(0, lineStr)
					else:
						# add random details to the List of pool values
						tmp_dictValuesList.append(lineStr)
			else:
				if isServer == 1:
					# build and store gtmServer object
					self.__server[tmp_nameStr] = gtmServer(tmp_nameStr, (', '.join(s_ipAddrList)), s_datacenter, \
						tmp_monitorList[:], s_product, s_vsDiscovery, **tmp_dict)

					# reset server variables
					isServer = 0
					s_ipAddrList.clear()
					s_datacenter = str()
					s_product = str()
					s_vsDiscovery = "disabled"
				elif isPool == 1:
					## build and store gtmPool object
					self.__pool[tmp_nameStr] = gtmPool(tmp_nameStr, p_alternateMode, p_dynamicRatio, p_fallbackIp, \
						p_fallbackMode, p_lbMode, p_verifyMemberAvailability, p_ttl, tmp_monitorList[:], **tmp_dict)

					# reset pool variables
					isPool = 0
					p_alternateMode = "none"
					p_dynamicRatio = "disabled"
					p_fallbackIp = str()
					p_fallbackMode = str()
					p_lbMode = str()
					p_verifyMemberAvailability = "enabled"
					p_ttl = 30
				elif isWideip == 1:
					## build and store gtmWideip object
					self.__wideip[tmp_nameStr] = gtmWideIp(tmp_nameStr, w_descriptionStr, w_lastResortPoolStr, \
						w_persistenceStr, w_poolLBmodeStr, w_ttlPersistenceStr, w_aliasesList[:], w_rulesList[:], **tmp_dict)

					# reset pool variables
					w_descriptionStr = str()
					w_lastResortPoolStr = str()
					w_persistenceStr = str()
					w_poolLBmodeStr = str()
					w_ttlPersistenceStr = str()
					w_aliasesList.clear()
					w_rulesList.clear()

				# reset shared variables
				tmp_nameStr = str()
				tmp_monitorList.clear()
				tmp_dict.clear()
				tmp_dictKeyStr = str()
				tmp_dictValuesList.clear()


	def searchIP(self, inputNodesListArg):
		"""
		Uses IP addresses to build/return a list of related objects (server, pools and wideip).
		input: 	inputNodesListArg, list of IP server addresses.
		output:	list of objects related to the input IP addresses.
		"""
		## Variables
		myOutputList = [ ]
		tmp_serverNameStr = str()
		vsList = [ ]
		memberList = [ ]
		poolList = [ ]
		wideipList = [ ]

		for addr in inputNodesListArg:
			# add IP to the output
			myOutputList.append("======== " + addr + " ========")

			## for each IP address
			# if the ip address is in use by some server
			if addr in self.__ipServer:
				# search __ipServer and store the server name
				tmp_serverNameStr = self.__ipServer[addr]
				# add the server object to the output list
				myOutputList.append(self.__server[tmp_serverNameStr])

				## for each server
				# get each vs of the current server and store them in a list
				############## try server with multiple vs
				vsList = self.__server[tmp_serverNameStr].getVsNameList()
				# create a list of members (server:virtual-server) based off of the vsList
				for vs in vsList:
					memberList.append(tmp_serverNameStr + ":" + vs)
				
				## for each member
				# search __memberPool and store a list of pool names
				for member in memberList:
					if member in self.__memberPool:
						# extract each name of the list contained in the memberPool dict
						for poolName in self.__memberPool[member]:
							# avoid adding same pool multiple times
							if poolName not in poolList:
								poolList.append(poolName)
					else:
						# add member(s) not in use to the output list
						myOutputList.append("\nmember not listed on any pool: " + member)
						
				## for each pool found
				for pool in poolList:
					# add pool object to the output list
					myOutputList.append(self.__pool[pool])

				## for each pool
				# search __poolWideip and store a list of wideip names
				for pool in poolList:
					# if pool is used by some wideip
					if pool in self.__poolWideip:
						# extract each wideip name from the list of wideips referenced by the current pool
						for wideipName in self.__poolWideip[pool]:
							# avoid adding same wideip multiple times
							if wideipName not in wideipList:
								wideipList.append(wideipName)
					else:
						# add pool(s) not in use to the output list
						myOutputList.append("\npool not used by any wideip: " + pool)
				for wideip in wideipList:
					# add wideip object to the output list
					myOutputList.append(self.__wideip[wideip])
			else:
				myOutputList.append("\n[error] IP address not found\n")

			myOutputList.append("\n================================\n")

			# only if addr is not the last iteration of this method
			if addr != inputNodesListArg[-1]:
				tmp_serverNameStr = str()
				vsList.clear()
				memberList.clear()
				poolList.clear()
				wideipList.clear()

		return myOutputList


	def printServer(self):
		"""
		[Debug] Function used to print contents of the server Dict. Values are gtmServer objects
		output: prints to stdOut the gtmServer object stored within each key.
		"""
		if len(self.__server) > 0:
			F5gtmServerList = self.__server.keys()
			print("\n======== F5 GTM Server ========")
			for name in F5gtmServerList:
				print(self.__server[name])
		else:
			print("no backend servers found")

	def printPool(self):
		"""
		[Debug] Function used to print contents of the pool Dict. Values are gtmPool objects
		output: prints to stdOut the gtmPool object stored within each key.
		"""
		if len(self.__pool) > 0:
			F5gtmPoolList = self.__pool.keys()
			print("\n======== F5 GTM Pool ========")
			for name in F5gtmPoolList:
				print(self.__pool[name])
		else:
			print("no pools found")

	def printWideip(self):
		"""
		[Debug] Function used to print contents of the wideip Dict. Values are gtmWideIp objects
		output: prints to stdOut the gtmWideIp object stored within each key.
		"""
		if len(self.__wideip) > 0:
			F5gtmWideipList = self.__wideip.keys()
			print("\n======== F5 GTM WideIP ========")
			for name in F5gtmWideipList:
				print(self.__wideip[name])
		else:
			print("no wideips found")

	def printSearchDicts(self):
		"""
		[Debug] Function used to print contents of the search Dicts.
		output: prints to stdOut the ip -> server, member -> pool, pool -> wideip, wideip -> pool relationship.
		"""
		print("\n======== Search Dicts ========")
		print("\n ** ipServer ")
		printStrDict(self.__ipServer)
		print("\n ** memberPool ")
		printListDict(self.__memberPool)
		print("\n ** poolWideip ")
		printListDict(self.__poolWideip)
		print("\n ** wideipPool ")
		printListDict(self.__wideipPool)


#####################
### Script Body
#####################
if readInput():
	# if inputNodeList is empty, load it with the contents of the user input csv
	if len(inputNodeList) == 0:
		inputNodeList = readCsv(ui_CsvStr)
	# put F5 source contents into a List
	f5SourceList = readF5Source(ui_f5SourceLocationStr)
	# create a GTM object
	myGTM = F5gtm()
	# Load the object with the F5 source file contents
	myGTM.load(f5SourceList)
	#myGTM.printServer()
	#myGTM.printPool()
	#myGTM.printWideip()
	#myGTM.printSearchDicts()
	# search each nodes in the inputNodeList and put the results in the scriptOutputObjList 
	scriptOutputObjList = myGTM.searchIP(inputNodeList)
	if getOutput(scriptOutputObjList, ui_outputPathStr):
		print ("\nScript completed successfully at " + localDateTime() + '\n')
