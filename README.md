# Data Center Decommissioning Automation Tool (DCAT)

## Introduction

The **Data Center Decommissioning Automation Tool (DCAT)** is a comprehensive automation solution designed to streamline and standardize the decommissioning process for IT infrastructure components in data centers. This tool automates the end-to-end decommissioning workflow for various server types while ensuring data integrity, security compliance, and proper resource cleanup.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ServiceNow    │───▶│      DCAT        │───▶│   AWX/Ansible   │
│   (Trigger)     │    │   Automation     │    │   Tower         |
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                      |
                                                      │
                                ┌─────────────────────┼─────────────────────┐
                                │                     │                     │
                                ▼                     ▼                     ▼
                        ┌─────────────┐    ┌─────────────────┐    ┌────────────────┐
                        │   Virtual   │    │     Physical    │    │ ESXi Servers   │
                        │   Machines  │    │     Servers     │    │ ( Rack/Blades/ │
                        │   (VMware)  │    │                 │    │  Enclosures )  │
                        └─────────────┘    └─────────────────┘    └────────────────┘
                                │                     │                     │
                                └─────────────────────┼─────────────────────┘
                                                      │
                                                      ▼
                                            ┌──────────────────────┐
                                            │ Integrated           │
                                            │ Systems:             │
                                            │ • DNS/IP cleanup     │
                                            │ • CMDB               │
                                            │ • Backup             │
                                            │ • Storage (NAS/SAN)  │
                                            │ • Network            |
                                            | • Server Deletion    │
                                            └──────────────────────┘
```


## Disclaimer
This project serves as a blueprint and reference implementation for Data Center Decommissioning Automation Tool (DCAT). Users are expected to configure their own environment, set up connectivity, integrate with internal systems (CMDB, ServiceNow, IPAM, Storage, Network, etc.), and implement any additional operational or security requirements specific to their organization.


## Supported Infrastructure Flavors

### 1. Virtual Machine (VM) Decommissioning
- **VMware vSphere** virtual machines
- **Two-phase approach** with configurable grace period (currently 3 days)
- **Complete lifecycle management** from information gathering to resource cleanup to power-off to deletion

**Key Features:**
- Pre-decommission health checks
- NAS/Storage cleanup
- DNS/IP cleanup integration
- CMDB server status updates
- Data backup policy management

### 2. Physical Server Decommissioning
- **Two-phase approach** with configurable grace period (currently 3 days)
- **Hardware inventory** management
- **ILO/BMC** integration for remote management
- **Storage controller** configuration cleanup
- **Network controller** configuration cleanup (HP, Dell & Arista vendors)

**Supported Hardware:**
- HP/HPE servers with ILO
- Data backup policy management
- SAN Storage cleanup along with NVME & local disk
- DNS/IP cleanup integration
- CMDB server status updates


### 3. ESXi Server Decommissioning
- **Blade servers**, **Enclosure servers** and **Rack servers**
- **Cluster management** integration
- **Storage and network** cleanup

**ESXi Features:**
- Host evacuation procedures
- Data backup policy management
- SAN Storage cleanup along with NVME & local disk
- DNS/IP cleanup integration
- CMDB servers status updates
- Oneview/Xclarity, Vcenter cleanup
- Network configuration removal (HP, Dell & Arista vendors)

## Prerequisites and Execution Environment

### Required Software Versions
```yaml
Ansible: >= 2.9
Python: >= 3.8
AWX/Ansible Tower: >= 17.0
VMware vSphere: >= 6.5
```

### Python Dependencies
```bash
# Core automation libraries
pyvmomi==7.0.3              # VMware vSphere SDK
infoblox-client==0.5.0      # DNS/IP cleanup management
requests>=2.25.1            # HTTP client library
paramiko>=2.7.2             # SSH client
cryptography==37.0.4        # Encryption support
pandas>=1.3.0               # Data manipulation
pywinrm>=0.4.2             # Windows remote management

# Storage and networking
netapp-lib>=2021.6.25       # NetApp storage management
dnspython>=2.1.0            # DNS operations
urllib3>=1.26.0             # HTTP library

# Data processing and parsing
xmltodict>=0.12.0           # XML parsing
lxml>=4.6.0                 # XML/HTML processing
six>=1.16.0                 # Python 2/3 compatibility

# Data storage and analysis
pyarrow>=5.0.0              # Parquet file support
azure-data-tables>=12.0.0   # Azure Table Storage
```

### Ansible Collections
```yaml
collections:
  - community.general       # General utilities
  - netapp.ontap            # NetApp storage
  - infoblox.nios_modules   # Infoblox DNS/IP cleanup
  - community.vmware        # VMware operations
  - ansible.windows         # Windows management
```

## How to Run the Automation

### 1. Standard VM Decommissioning Workflow

#### Phase 1: Pre-Decommission Validation (Grace Period Start)
```bash
# Launch first trigger with grace period flag set to False
ansible-playbook playbooks/launch_prod_deco.yml -e '{
  "associated_cis": [
    {"hosts": "server001"},
    {"hosts": "server002"},
    {"hosts": "server003"}
  ],
  "cr": "CR2024001234",                # change_record_number
  "graceperiod_flag": false,
  "retention_days": "30",
  "requester_name": "John Doe",
  "requester_group": "Infrastructure Team",
  "ritm_number": "RITM001234"         # RITM number from ServiceNow
}'
```

#### Phase 2: Final Decommission (After Grace Period)
```bash
# Launch second trigger with grace period flag set to True
ansible-playbook playbooks/launch_prod_deco.yml -e '{
  "associated_cis": [
    {"hosts": "server001"},
    {"hosts": "server002"},
    {"hosts": "server003"}
  ],  
  "cr": "CR2024001234",                 # change_record_number
  "graceperiod_flag": true,
  "retention_days": "30",
  "requester_name": "John Doe",
  "requester_group": "Infrastructure Team",
  "ritm_number": "RITM001234"           # RITM number from ServiceNow
}'
```

### 2. Physical Server Decommissioning

#### Phase 1: Pre-Decommission Validation (Grace Period Start)
```bash
# Physical server decommission workflow
ansible-playbook playbooks/launch_prod_phydeco.yml -e '{
  "associated_cis": [
    {"hosts": "physerver001"},
    {"hosts": "physerver002"}
  ],
  "cr": "CR2024001235",               # change_record_number
  "graceperiod_flag": false,
  "retention_days": "30",
  "requester_name": "John Doe",
  "requester_group": "Infrastructure Team",
  "ritm_number": "RITM001234"         # RITM number from ServiceNow
}'
```

#### Phase 2: Final Decommission (After Grace Period)
```bash
# Launch second trigger with grace period flag set to True
ansible-playbook playbooks/launch_prod_phydeco.yml -e '{
  "associated_cis": [
    {"hosts": "physerver001"},
    {"hosts": "physerver002"}
  ],
  "cr": "CR2024001234",               # change_record_number
  "graceperiod_flag": true,
  "retention_days": "30",
  "requester_name": "John Doe",
  "requester_group": "Infrastructure Team",
  "ritm_number": "RITM001234"         # RITM number from ServiceNow
}'
```

### 3. ESXi Host Decommissioning

```bash
# ESXi host decommission workflow
ansible-playbook playbooks/launch_dev_esxi_enclosure.yml -e '{
  "associated_cis": [
    {"hosts": "esxihost001"},
    {"hosts": "esxihost002"}
  ],
  "cr": "CR2024001236",               # change_record_number
  "requester_name": "John Doe",
  "requester_group": "Infrastructure Team",
  "ritm_number": "RITM001234",        # RITM number from ServiceNow
  "graceperiod_flag": false,
}'
```

# External App Dependencies

## CMDB Integration

### Overview
The DCAT tool integrates with **BMC Remedy CMDB** (Configuration Management Database) to fetch server information and update asset status during the decommissioning process. This integration ensures accurate tracking of infrastructure components and maintains data consistency across systems.

### CMDB API Endpoints
The tool uses BMC Remedy REST API v1 to interact with the CMDB:

```
Base URL: https://{cmdb_server}/api/arsys/v1/
Authentication: AR-JWT Token
Primary Form: BMC.CORE:BMC_ComputerSystem
Dataset: BMC.ASSET
```

### Authentication Flow

```python
# JWT Token Authentication Process
1. Login Request → CMDB Server
2. Receive JWT Token
3. API Operations with Token
4. Logout Request → Token Cleanup
```

### Sample CMDB Query Structure

```python
# Query Format for Server Information
query = 'DatasetId="BMC.ASSET" and (MarkAsDeleted=null or MarkAsDeleted=0) and Name="{server_name}"'
url = '{cmdb_server}/api/arsys/v1/entry/BMC.CORE:BMC_ComputerSystem?q={encoded_query}'
```

### Sample API Response Structure

```json
{
  "Category": "Hardware",
  "Type": "Processing Unit",
  "Item": "Server",
  "Department": null,
  "SiteGroup": "ADP",
  "Region": null,
  "PartNumber": null,
  "Name": "vmdecovt003",
  "Model": "VMWare Virtual Machine",
  "ManufacturerName": "VMware",
  "ManufacturerID": null
}
```

## Swagger API Integration (Referenced as Synergon)

### Overview
The DCAT tool integrates with **Swagger API** to fetch vCenter and infrastructure details for virtual machines during the decommissioning process. The in-built swagger API provides a centralized inventory system that maintains up-to-date information about VM locations, cluster assignments, and datacenter mappings.

### Swagger API Endpoints
The tool uses Swagger REST API v1 to query VM information:

```
Base URL: https://{swagger_api}/v1/
Query Parameters: expand, offset, limit, name
```

### Sample API Query Structure

```python
# Query Format for VM Information
url = "https://{swagger_api}/v1/vms/?expand=host&offset=0&limit=10&name={vmname}"
headers = {"Accept": "application/json"}
```

### Sample API Response Structure

```json
{
    "data": [
        {
            "self": {
                "name": "vmdecovt003",
                "link": "https://{swagger_api}/v1/vms/45aa1e7b-8042-4ae2-ace4-28c743b5729b/"
            },
            "uuid": "<uuid_value>",
            "vcenter": "<vcenter_name>",
            "datacenter": "<datacenter_name>",
            "cluster": "<cluster_name>"
        }
    ]
}
```

## IPAM/Infoblox Integration

### Overview
The DCAT tool integrates with **Infoblox IPAM** (IP Address Management) system to manage IP address lifecycle during server decommissioning. This integration ensures proper cleanup of IP reservations and DNS records, preventing IP conflicts and maintaining network hygiene.

### Infoblox WAPI Endpoints
The tool uses Infoblox Web API (WAPI) v2.1 for IP management operations:

```
Base URL: https://{ipam_server}/wapi/v2.1/
Primary Endpoint: /ipv4address
Authentication: Basic Auth Plain Text(Username/Password)
SSL Verification: Disabled for internal networks
```

### Sample API Query Structure

```python
# Query Format for IP Information
url = "https://{ipam_server}/wapi/v2.1/ipv4address?ip_address={ip}&network_view={view}"
auth = (username, password)
```

### Sample API Response Structure

```json
[
    {
        "_ref": "ipv4address/Li5pcHY0X2FkZHJlc3MkMTcyLjE3LjE4MC43Ny8w:<server_ip_address>",
        "ip_address": "<server_ip_address>",
        "is_conflict": false,
        "mac_address": "",
        "names": [],
        "network": "<server_network>",
        "network_view": "default",
        "objects": [],
        "status": "UNUSED",
        "types": [],
        "usage": []
    }
]
```

### IP Release Logic and Validation

```python
# IP Release Decision Flow
1. Query IP Status → Check if UNUSED
2. If USED → Validate hostname match
3. If Valid → Release IP (DELETE operation)
4. Return Status → Success/Error message
```


# Azure Tables Integration

## Introduction

The **Azure Table Storage** database serves as the **central state management layer** for DCAT. It acts as one of the **key components** enabling idempotent, traceable, and consistent execution across decommissioning workflows.  
Azure Tables store server- and ticket-level information for both virtual and physical infrastructures, ensuring that each automation step is executed exactly once.

---

## Database Structure

DCAT uses **six tables** within Azure Table Storage, each handling a distinct operational aspect:

| Table Name | Description |
|-------------|-------------|
| **CRdetails** | Stores the *Change Record (CR)* number and its mapping to all related servers. Acts as a parent table for host and ticket data. |
| **metadataDetails** | Holds metadata about each ticket (CR/RITM), including requester details, timestamps, and context information. |
| **hostDetails** | Tracks **VM-level** task progress with `T/F` flags. Each flag represents whether a module (e.g., DNS cleanup, CMDB update) has completed successfully. Defaults are `F`, updated to `T` upon success — forming the foundation of **idempotency**. |
| **PhysicalServerDetails** | Similar to `hostDetails` but for **physical servers**, storing per-module task completion flags. |
| **PhysicalServerStorageDetails** | Maintains **infrastructure details** such as IPs, FQDNs, SAN switch mappings, and enclosure or rack data. |
| **TRdetails** | Logs all **approval (TR)** and **problem tasks** for each server, linking them to their corresponding ServiceNow records. |

---

## How-to

### Provisioning Azure Tables

1. **Create a Storage Account** in Azure → enable **Table Storage**.  

2. Create six tables:  
  - CRdetails
  - metadataDetails
  - hostDetails
  - PhysicalServerDetails
  - PhysicalServerStorageDetails
  - TRdetails

3. Configure access keys or Managed Identity for secure automation access.

4. Use the azure-data-tables Python SDK to read/write data programmatically.

```python
from azure.data.tables import TableServiceClient

service = TableServiceClient.from_connection_string(conn_str)
table = service.get_table_client("hostDetails")

entity = {
    "PartitionKey": "CR2024001234",
    "RowKey": "server001",
    "dns_cleanup": "T",
    "cmdb_update": "F"
}
table.upsert_entity(entity)
```

## Role in Automation

1. Before executing a module, Ansible checks Azure Tables for existing T/F flags.

2. If a task is already marked as T, it is skipped.

3. If marked F, the module executes and updates to T after successful completion.

4. This ensures safe re-runs and eliminates duplicate executions.

## Why-to

1. **Backtracking** - Azure Tables provide complete visibility into every automation stage, enabling easy traceability of failures or skipped steps for any CR or host.

2. **Idempotency** - The T/F model ensures safe re-execution — only incomplete modules run on retries, maintaining data consistency and preventing destructive re-runs.

3. **Mapping and Correlation** - Ticket data, task progress, and server metadata are all cross-linked in one unified store, simplifying reporting, auditing, and integration with CMDB and ServiceNow.


