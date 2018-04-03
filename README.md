# Ansible module for Dell EMC OpenManage Enterprise Tech Release using REST API

Ansible module and playbooks that use the REST API to manage PowerEdge servers via central OpenManage Enterprise. For more details, see these [slides](http://www.dell.com/en-us/work/learn/enterprise-systems-management).

## Why Ansible

Ansible is an open source automation engine that automates complex IT tasks such as cloud provisioning, application deployment and a wide variety of IT tasks. It is a one-to-many agentless mechanism where complicated deployment tasks can be controlled and monitored from a central control machine.

To learn more about Ansible, click [here](http://docs.ansible.com/).

## Why REST

## Ansible and REST together

## How it works

## Categories

For more details on what commands are available in each category, refer to this [README](playbooks).

## Requirements

- Openmanage Enterprise Tech Release

## Installation

Clone this repository:
```
$
```
Install Ansible + required Python libraries:
```
$ pip install -r requirements.txt
```
Copy module to default system location:
```
$ python install.py
```

## Examples

The file */etc/ansible/hosts* should look like this:

```
[myhosts]
# hostname     OOB controller IP/NAME
webserver1     baseuri=192.168.0.101
webserver2     baseuri=192.168.0.102
dbserver1      baseuri=192.168.0.103
...
```

The OOB controller IP is necessary as this is how we communicate with the host. We are not connecting to the host OS via ssh, but to the OOB controller via https, so be sure this information is correct. Please note that *baseuri* can also be a DNS-resolvable name.

The playbook names are self-explanatory, and they are the best source to learn how to use them. Every Redfish API supported by the Ansible module is included in the playbooks. If it's not in a playbook, a Redfish API has not been coded into the module yet.

```bash

$ cd playbooks
$ ansible-playbook get_system_inventory.yml
  ...
PLAY [Get System Inventory] ****************************************************

TASK [Define timestamp] ********************************************************
ok: [webserver1]
ok: [webserver2]
ok: [dbserver1]
  --- snip ---
```

Playbooks that collect system information will place it in files in JSON format in a directory defined by the *rootdir* variable in file *group_vars/all*. The playbook creates a directory for each server and places files there. For example:

```bash
$ cd <rootdir>/webserver1
$ ls

```

These files are in the format *<host>_<timestamp>_<datatype>* and each contains valuable server inventory.

```

```

## Parsing through JSON files

All data collected from servers is returned in JSON format. Any JSON parser can then be used to extract the specific data you are looking for, which can come in handy since in some cases the amount of data collected can be more than you need.

The [jq](https://stedolan.github.io/jq/) parser to be easy to install and use, here are some examples using the output files above:

```bash

```

It should be straight-forward to extract the same data from hundreds of files using shell scripts and organize it accordingly. In the near future scripts will be made available to facilitate data orgnization. For additional help with jq, refer to this [manual](https://shapeshed.com/jq-json/).

## Support

Please note this code is provided as-is and not supported by Dell EMC.

## Report problems or provide feedback

If you run into any problems or would like to provide feedback, please open an issue.
