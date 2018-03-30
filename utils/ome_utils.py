#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This file is part of Ansible.
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


import os
import requests
import json
import re
import xml.etree.ElementTree as ET
from distutils.version import LooseVersion
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning


HEADERS = {'content-type': 'application/json'}

class OmeUtils(object):

	def __init__(self, creds, root_uri):
		self.root_uri = root_uri
		self.creds = creds
		self._init_session()

	def send_get_request(self, uri):
		'''helper function for get requests'''


		headers = {}
		if 'token' in self.creds:
			headers = {"X-Auth-Token": self.creds['token']}
		try:
			response = requests.get(uri, headers, verify=False, auth=(self.creds['user'], self.creds['pswd']))
		except:
			raise
		return response

	def send_post_request(self, uri, pyld, hdrs, fileName=None):
		headers = {}
		#import epdb; epdb.serve()
		if 'token' in self.creds:
			headers = {"X-Auth-Token": self.creds['token']}
		try:
			data = json.dumps(pyld)
			response = requests.post(uri, data, headers=hdrs, files=fileName, verify=False, auth=(self.creds['user'], self.creds['pswd']))
		except:
			raise
		return response

	def send_patch_request(self, uri, pyld, hdrs):
		headers = {}
		if 'token' in self.creds:
			headers = {"X-Auth-Token": self.creds['token']}
		try:
			response = requests.patch(uri, data=json.dumps(pyld), headers=hdrs,
							   verify=False, auth=(self.creds['user'], self.creds['pswd']))
		except:
			raise
		return response

	def send_delete_request(self, uri, pyld, hdrs):
		headers = {}
		if 'token' in self.creds:
			headers = {"X-Auth-Token": self.creds['token']}
		try:
			response = requests.delete(uri, verify=False, auth=(self.creds['user'], self.creds['pswd']))
		except:
			raise
		return response

	def _init_session(self):
		pass

	def get_discovery_jobs(self, uri):
		'''get detailed information of existing discovery jobs'''

		# works

		uri = self.root_uri + uri
		result = {}
		allJobs = []

		response = self.send_get_request(uri)

		if response.status_code == 200: # success
			result['ret'] = True
			data = response.json()

			for task in data[u'value']: # flatten result tree
				job = {}
				job['DiscoveredDevices'] = task[u'DiscoveredDevicesByType']
				job['DiscoveredDevicesCount'] = task[u'DiscoveryConfigDiscoveredDeviceCount']
				job['MailRecipient'] = task[u'DiscoveryConfigEmailRecipient']
				job['ExpectedDeviceCount'] = task[u'DiscoveryConfigExpectedDeviceCount']
				job['GroupId'] = task[u'DiscoveryConfigGroupId']
				job['Description'] = task[u'JobDescription']
				job['EndTime'] = task[u'JobEndTime']
				job['Id'] = task[u'JobId']
				job['Name'] = task[u'JobName']
				job['NextRun'] = task[u'JobNextRun']
				job['Progress'] = task[u'JobProgress']
				job['Schedule'] = task[u'JobSchedule']
				job['StartTime'] = task[u'JobStartTime']
				job['StatusId'] = task[u'JobStatusId']
				job['LastUpdateTime'] = task[u'LastUpdateTime']
				job['UpdatedBy'] = task[u'UpdatedBy']
				allJobs.append(job) #append job details

			result['entries'] = allJobs

		elif response.status_code == 400:
			result = { 'ret': False, 'msg': 'Not Supported'}
		else:

			result = { 'ret': False, 'msg': "Error code %s, url %s" % (response.status_code, url) }

		return result

	def create_new_discovery_job(self, uri, attributes):
		'''create new discovery job for given range'''

	## Not working returns error 400 (try with changed payload, direct to json.dumps)

		uri = self.root_uri + uri
		result = {}



	#	discovery_attributes = "{\"DiscoveryConfigGroupName\":\"" + attributes['jobName'] + "\"," \
	#						"{\"DiscoveryStatusEmailRecipient\":\"" + attributes['email'] + "\"," \
	#						"{\"DiscoveryConfigModels\":[{\"DiscoveryConfigTargets\":[{\"NetworkAddressDetail\":\"" + attributes['startIp'] \
	#						+ "-" + attributes['endIp'] + "\"}]," \
	#						"{\"DeviceType\":[" + attributes['deviceType'] + "]}]," \
	#						"{\"Schedule\":{\"RunNow\":true,}}"


		payload = {"Attributes": json.loads(discovery_attributes) }
		response = self.send_post_request(uri, payload, HEADERS)
		result = { 'ret': False, 'msg': "Error code %s, url %s, response: %s" % (response.status_code, uri, response.json()) }
		return result

	def remove_discovery_job(self, uri, jobId):
		'''Remove discovery job'''

		# works! add support for ID lists


		uri = self.root_uri + uri
		result = {}

		job_attributes = [int(jobId)]

		# maybe put this payload to ome.py?
		payload = {"DiscoveryGroupIds": job_attributes }

		response = self.send_post_request(uri, payload, HEADERS)

		if response.status_code == 204:
			result['ret'] = True
		else:
			result = { 'ret': False, 'msg': "Error code %s" % (response.status_code) }

		return result

	def import_discovery_job_ips(self, uri, location):
		'''Import discovery job'''

		# [ERROR] 2018-03-17 22:45:06.810 [ajp-bio-8009-exec-2] MCSIActionProcessor - null
		# java.lang.NullPointerException


		uri = self.root_uri + uri
		result = {}
		#import epdb; epdb.serve()
		payload = location

		response = self.send_post_request(uri, payload, HEADERS)
		if response.status_code == 201:
			result['ret'] = True
			result['entries'] = response.json()
		else:
			result = { 'ret': False, 'msg': "Error code %s, response: %s" % (response.status_code, response.json()) }
		return result

	def get_warranties(self, uri):
		'''returns all warranty information discovered by OME'''

		# filtering is done via uri like this: .../Warranties?top&orderby=name

		uri = self.root_uri + uri
		result = {}
		allEntries = []

		response = self.send_get_request(uri)

		if response.status_code == 200:
			result['ret'] = True
			data = response.json()

			for warranty in data[u'value']: # clean up output
				entry = {}
				entry['WarrantyId'] = warranty[u'Id']
				entry['DeviceId'] = warranty[u'DeviceId']
				entry['DeviceModel'] = warranty[u'DeviceModel']
				entry['DeviceServiceTag'] = warranty[u'DeviceIdentifier']
				entry['DeviceType'] = warranty[u'DeviceType']
				entry['CountryLookupCode'] = warranty[u'CountryLookupCode']
				entry['CustomerNumber'] = warranty[u'CustomerNumber']
				entry['LocalCannel'] = warranty[u'LocalChannel']
				entry['OrderNumber'] = warranty[u'OrderNumber']
				entry['SystemShipDate'] = warranty[u'SystemShipDate']
				entry['State'] = warranty[u'State']
				entry['ItemNumber'] = warranty[u'ItemNumber']
				entry['ServiceLevelCode'] = warranty[u'ServiceLevelCode']
				entry['ServiceLevelDescription'] = warranty[u'ServiceLevelDescription']
				entry['ServiceLevelGroup'] = warranty[u'ServiceLevelGroup']
				entry['ServiceProvider'] = warranty[u'ServiceProvider']
				entry['StartDate'] = warranty[u'StartDate']
				entry['EndDate'] = warranty[u'EndDate']
				entry['DaysRemaining'] = warranty[u'DaysRemaining']
				entry['Timestamp'] = warranty[u'Timestamp']
				allEntries.append(entry)

			result['entries'] = allEntries
		else:
			result = { 'ret': False, 'msg': "Error code %s, response: %s" % (response.status_code, response.json()) }

		return result

	def get_warranty_count(self, uri):
		'''returns warranty counts based on webui scoreboard settings'''


		uri = self.root_uri + uri
		result = {}

		# payload doesn't change output, but it needs to be a valid property; empty payload is not allowed
		payload = {
					"ScoreBoard": 'false'
					}

		response = self.send_post_request(uri, payload, HEADERS)

		if response.status_code == 200:
			result['ret'] = True
			result['entries'] = response.json()
		else:
			result = { 'ret': False, 'msg': "Error code %s, response: %s" % (response.status_code, response.json()) }

		return result

	def get_reports(self, uri):
		'''returns report collection'''


		# works --> TODO: cleanup output

		uri = self.root_uri + uri
		result = {}

		response = self.send_get_request(uri)

		if response.status_code == 200:
			result['ret'] = True
			data = response.json()

			result['entries'] = data
		else:
			result = { 'ret': False, 'msg': "Error code %s" % (response.status_code) }

		return result

	def create_report(self, uri, name):
		'''creates a new report'''

		uri = self.root_uri + uri
		result = {}

		### should be like this

		payload = {
					"Name": name,
					"Description": "",
					"ColumnNames": [
					{
							  "Width":20,
							  "Sequence":0,
							  "Name":"Device Name"
							  },
							  {
							  "Width":20,
							  "Sequence":1,
							  "Name":"Device Model"
							  },
							  {
							  "Width":20,
							  "Sequence":2,
							  "Name":"Device Service Tag"
							  }
							  ],
							  "FilterGroupId":64,
							  "QueryDefRequest":{
							  "ContextId":5,
							  "ResultFields":[
							  {
							  "FieldId":421
							  },
							  {
							  "FieldId":423
							  },
							  {
							  "FieldId":424
							  }
							  ],
							  "SortFields":[
							  {
							  "FieldId":421,
							  "SortDir":0
							  }
							]
						}
					}
				

		response = self.send_post_request(uri, payload, HEADERS)
		if response.status_code == 201:
			result['ret'] = True
			data = response.json()

			result['entries'] = data
		else:
			result = { 'ret': False, 'msg': "Error code %s, response: %s" % (response.status_code, response.json()) }

		return result
		
	def update_report(self, uri, reportId, updateInfo):
		'''update a report'''

		uri = self.root_uri + uri
		result = {}

		### should be something like this

		payload = {  
                              "Id":12164,
                              "Name":"Report test-Edit",
                              "Description":"",
                              "ColumnNames":[  
                              {  
                              "Width":20,
                              "Sequence":0,
                              "Name":"Alert Message"
                              },
                              {  
                              "Width":20,
                              "Sequence":1,
                              "Name":"Alert Message ID"
                              },
                              {  
                              "Width":20,
                              "Sequence":2,
                              "Name":"Alert Severity"
                              }
                              ],
                              "FilterGroupId":64,
                              "QueryDefRequest":{  
                              "ContextId":5,
                              "ResultFields":[  
                              {  
                              "FieldId":689
                              },
                              {  
                              "FieldId":692
                              },
                              {  
                              "FieldId":691
                              }
                              ],
                              "SortFields":[  
                              
                              ]
                              }
                              }
				

		response = self.send_post_request(uri, payload, HEADERS)
		if response.status_code == 201:
			result['ret'] = True
			data = response.json()

			result['entries'] = data
		else:
			result = { 'ret': False, 'msg': "Error code %s, response: %s" % (response.status_code, response.json()) }

		return result


	def run_report(self, uri, reportId):
		'''run report'''

		uri = self.root_uri + uri
		result = {}
		
		payload = {
			"ReportDefId":reportId,
			"FilterGroupId":0
		}
		
		
		response = self.send_post_request(uri, payload, HEADERS)
		if response.status_code == 200:
			result['ret'] = True
			data = response.json()

			result['entries'] = data
		else:
			result = { 'ret': False, 'msg': "Error code %s, response: %s" % (response.status_code, response.json()) }

		return result

	def delete_report(self, uri, reportId):
		'''delete report'''

		uri = self.root_uri + uri
		result = {}
		
		payload = [int(reportId)]
		
		response = self.send_post_request(uri, payload, HEADERS)
		if response.status_code == 200:
			result['ret'] = True
			data = response.json()

			result['entries'] = data
		else:
			result = { 'ret': False, 'msg': "Error code %s, response: %s" % (response.status_code, response.json()) }

		return result

	def download_report(self, uri, reportId, dataFormat):
		'''delete report'''

		uri = self.root_uri + uri
		result = {}
		
		payload =  {"ReportDefId":reportId,"Format":dataFormat}
		
		response = self.send_post_request(uri, payload, HEADERS)
		if response.status_code == 200:
			result['ret'] = True
			data = response.json()

			result['entries'] = data
		else:
			result = { 'ret': False, 'msg': "Error code %s, response: %s" % (response.status_code, response.json()) }

		return result
		
	def get_groups(self, uri):
		'''returns groups'''


		# works --> TODO: cleanup output

		uri = self.root_uri + uri
		result = {}

		response = self.send_get_request(uri)

		if response.status_code == 200:
			result['ret'] = True
			data = response.json()

			result['entries'] = data
		else:
			result = { 'ret': False, 'msg': "Error code %s" % (response.status_code) }

		return result
		
	def get_group_audit(self, uri):
		'''returns groups and audit hierachy changes'''


		# works --> TODO: cleanup output

		uri = self.root_uri + uri
		result = {}

		response = self.send_get_request(uri)

		if response.status_code == 200:
			result['ret'] = True
			data = response.json()

			result['entries'] = data
		else:
			result = { 'ret': False, 'msg': "Error code %s" % (response.status_code) }

		return result


	def create_group(self, uri, attributes):
		'''create a new group'''

		uri = self.root_uri + uri
		result = {}
		
		# for static group
		payload = {	'GroupModel': 
						{ 	'Name': attributes['name'],
							'MembershipTypeId': attributes['membershipId'],
							'ParentId': attributes['parentId'],
						}
					}
		
		response = self.send_post_request(uri, payload, HEADERS)
		if response.status_code == 200:
			result['ret'] = True
			data = response.json()

			result['entries'] = data
		else:
			result = { 'ret': False, 'msg': "Error code %s, response: %s" % (response.status_code, response.json()) }

		return result
