# Openmanage Enterprise - manage Dell Openmanage Enterprise Tech. using REST API

## Synopsis

* Central management of Dell systems

## Requirements

* python >= 2.6
* ansible >= 2.3
* *requests* python library

## Options


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

## Examples

```
```
