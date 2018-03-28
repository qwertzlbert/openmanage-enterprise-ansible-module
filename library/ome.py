#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
ANSIBLE_METADATA = {'status': ['preview'],
					'supported_by': 'community',
					'metadata_version': '1.1'}

DOCUMENTATION = """
module: omenterprise
version_added: "2.3"
short_description: Manage Dell EMC hardware through OME REST API
options:
  category:
	required: true
	default: None
	description:
	  - Action category to execute on OME
  command:
	required: true
	default: None
	description:
	  - Command to execute on OME
  OMEip:
	required: true
	default: None
	description:
	  - OMEnterprise IP address
  omeuser:
	required: true
	default: None
	description:
	  - OMEnterprise user name used for authentication
  omepswd:
	required: true
	default: none
	description:
	  - OMEnterprise user password used for authentication
  dataFormat:
	required: false
	description:
	  - Format for files to download (e.g. csv)
  discStartAddress:
	required: false
	description:
	  - first ip address to start scan devices
  discEndAddress:
    required: false
    description:
	  - last ip address to scan for devices
  discDeviceType:
	required: false
	description: 
	  - Type of device to scan for (numerical)
  discJobName:
	required: false
	description:
	  - Name for Job
  discEmail:
	required: false
	description:
	  - email to notify
  discJobId
	required: false
	description:
	  - Id of job 
  discIpsFileLocation:
	required: false
	description:
	  - Location for file to import from
  reportName:
    required: false
    description:
      - Name for report
  reportId:
	required: false
	description:
	  - id of report
author: "simon.schnell@dell.com", github: qwertzlbert
"""

import os
import requests
import json
import re
import xml.etree.ElementTree as ET
from distutils.version import LooseVersion
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ome_utils import OmeUtils


def main():
	result = {}
	module = AnsibleModule(
		argument_spec = dict(
			category   = dict(required=True, type='str', default=None),
			command    = dict(required=True, type='str', default=None),
			omeip    = dict(required=True, type='str', default=None),
			omeuser  = dict(required=True, type='str', default=None),
			omepswd  = dict(required=True, type='str', default=None, no_log=True),
			dataFormat = dict(required=False, type='str', default=None),
			discStartAddress = dict(required=False, type='str', default=None),
			discEndAddress = dict(required=False, type='str', default=None),
			discDeviceType = dict(required=False, type='str', default=None),
			discJobName = dict(required=False, type='str', default=None),
			discEmail = dict(required=False, type='str', default=None),
			discJobId = dict(required=False, type='str', default=None),
			discIpsFileLocation = dict(required=False, type='str', default=None),
			reportName = dict(required=False, type='str', default=None),
			reportId = dict(required=False, type='str', default=None),
		),
		supports_check_mode=False
	)

	params = module.params
	category   = module.params['category']
	command    = module.params['command']
	#hostname   = params['hostname']

	# Disable insecure-certificate-warning message
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

	# admin credentials used for authentication
	creds = { 'user': module.params['omeuser'],
			  'pswd': module.params['omepswd']
			}

	# Attributes for disovery job
	discovery_attributes = { 'startIp': module.params['discStartAddress'],
				  'endIp' : module.params['discEndAddress'],
				  'deviceType': module.params['discDeviceType'],
				  'jobName': module.params['discJobName'],
				  'email': module.params['discEmail'],
				}

	# Build initial URI
	root_uri = "https://" + params['omeip'] + "/api"
	ome_utils = OmeUtils(creds, root_uri)
	# Execute based on what we want. Notice that some rf_uri values have an
	# ending slash ('/') and other don't. It's all by design and depends on
	# how the URI is used in each function.

	if category == "Discovery":
		if command == "ShowJobs":
			result = ome_utils.get_discovery_jobs("/DiscoveryConfigService/Jobs")
		elif command == "NewJob":
			result = ome_utils.create_new_discovery_job("/DiscoveryConfigService/DiscoveryConfigGroups", discovery_attributes) # not working issue with input --> error 400 missing attribute
		elif command == "RemoveJob":
			result = ome_utils.remove_discovery_job("/DiscoveryConfigService/Actions/DiscoveryConfigService.RemoveDiscoveryGroup", module.params['discJobId'])		
		elif command == "ImportJob":
			result = ome_utils.import_discovery_job_ips("/DiscoveryConfigService/Actions/DiscoveryConfigService.Parse", module.params['discIpsFileLocation']) # not working --> java null pointer exception in java backend
		else:
			result = { 'ret': False, 'msg': 'Invalid Command'}
	
	elif category == "Warranty":
		if command == "GetWarranties":
			result = ome_utils.get_warranties("/WarrantyService/Warranties")
		elif command == "WarrantyCount":
			result = ome_utils.get_warranty_count('/WarrantyService/Actions/WarrantyService.WarrantyCount')
		else: 
			result = { 'ret': False, 'msg': 'Invalid Command'}
			
	elif category == "Report":
		if command == "GetReports":
			result = ome_utils.get_reports("/ReportService/ReportDefs")
		elif command == "CreateReport":
			# no URI; missing in documentation...
			result = ome_utils.create_report("/ReportService/Actions/ReportService.????", module.params['reportName'])			
		elif command == "UpdateReport":
			# no URI; missing in documentation...
			result = ome_utils.update_report("/ReportService/Actions/ReportService.UpdateReport", module.params['reportId'])	
		elif command == "RunReport":
			result = ome_utils.run_report("/ReportService/Actions/ReportService.RunReport",module.params['reportId'])	
		elif command == "DeleteReport":
			result = ome_utils.delete_report("/ReportService/Actions/ReportService.DeleteReports", module.params['reportId'])
		elif command == "DownloadReport":
			result = ome_utils.download_report("/ReportService/Actions/ReportService.DownloadReport", module.params['reportId'], module.params['dataFormat'])
		else:
			result = { 'ret': False, 'msg': 'Invalid Command'}
	
	elif category == "Group":
		if command == "GetGroups":
			result = ome_utils.get_groups("/GroupService/Groups")
		elif command == "GetGroupAudits":
			result = ome_utils.get_group_audit("/GroupService/GroupAudits")
		elif command == "CreateGroup":
			result = ome_utils.create_group("/GroupService/Actions/GroupService.CreateGroup")
		else:
			result = { 'ret': False, 'msg': 'Invalid Command'}		
	
	else:
		result = { 'ret': False, 'msg': 'Invalid Category'}

	# Return data back or fail with proper message
	if result['ret'] == True:
		del result['ret']		# Don't want to pass this back
		module.exit_json(result=result)
	else:
		module.fail_json(msg=result['msg'])


if __name__ == '__main__':
	main()


