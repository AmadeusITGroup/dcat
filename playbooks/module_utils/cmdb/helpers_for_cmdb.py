import random
import time
from datetime import datetime
from os import lockf
from time import sleep

from azure.data.tables import TableClient, UpdateMode
import requests

cmdb_accounts_table_name = "CMDBAccounts"


def lru_user_account(conn_str):  # accounts=None):
	try:
		accounts = []
		counter = 0
		MAX_TRIES = 10
		while not accounts and counter < MAX_TRIES:
			random_sleep_time = random.randint(5, 20)
			print(f"Please wait for {random_sleep_time} seconds before fetching CMDB users from Azure Storage...")
			time.sleep(random_sleep_time)
			accounts = fetch_cmdb_users_from_azure_storage(conn_str=conn_str)
			counter += 1
		
		if counter == MAX_TRIES:
			raise Exception("Failed to fetch CMDB users after multiple attempts.")
		for i, a in enumerate(accounts):
			if isinstance(a["LastLogoutTime"], str):
				accounts[i]["LastLogoutTime"] = datetime.fromisoformat(a["LastLogoutTime"]).replace(tzinfo=None)
			if isinstance(a["LastLoginTime"], str):
				accounts[i]["LastLoginTime"] = datetime.fromisoformat(a["LastLoginTime"]).replace(tzinfo=None)
		
		accounts.sort(key=lambda x: x["LastLogoutTime"])
		# accounts.sort(key=lambda x: x["LastLoginTime"])
		cmdb_user_object = accounts[0]
		return cmdb_user_object
	except Exception as e:
		raise Exception(f"Error fetching or processing CMDB users: {e}")


def update_cmdb_user_azure(cmdb_object, conn_str):
	service = TableClient.from_connection_string(conn_str=conn_str, table_name=cmdb_accounts_table_name)
	cmdb_object.pop("password", None)
	# account_entity = service.get_entity(partition_key=cmdb_object["PartitionKey"], row_key=cmdb_object["RowKey"])
	temp = service.upsert_entity(mode=UpdateMode.MERGE, entity=cmdb_object)
	return cmdb_object


def create_table_cmdb_user(conn_str):
	# pass
	accounts = [
		{
			"PartitionKey": "1",
			"RowKey": "svc-deco-cmdb",  # username
			"Status": "Inactive",
			"LastLoginTime": f'{datetime.strptime("10-06-2025 08:32:14", "%d-%m-%Y %H:%M:%S")}',
			"LastLogoutTime": f'{datetime.strptime("10-06-2025 17:45:59", "%d-%m-%Y %H:%M:%S")}'
		},
		{
			"PartitionKey": "2",
			"RowKey": "svc-deco-cmdb1",
			"Status": "Inactive",
			"LastLoginTime": f'{datetime.strptime("13-06-2025 09:10:22", "%d-%m-%Y %H:%M:%S")}',
			"LastLogoutTime": f'{datetime.strptime("13-06-2025 18:22:41", "%d-%m-%Y %H:%M:%S")}'
		},
		{
			"PartitionKey": "3",
			"RowKey": "svc-deco-cmdb2",
			"Status": "Inactive",
			"LastLoginTime": f'{datetime.strptime("11-06-2025 07:55:07", "%d-%m-%Y %H:%M:%S")}',
			"LastLogoutTime": f'{datetime.strptime("12-06-2025 16:35:33", "%d-%m-%Y %H:%M:%S")}'
		},
		{
			"PartitionKey": "4",
			"RowKey": "svc-deco-cmdb3",
			"Status": "Inactive",
			"LastLoginTime": f'{datetime.strptime("11-07-2025 07:55:07", "%d-%m-%Y %H:%M:%S")}',
			"LastLogoutTime": f'{datetime.strptime("11-07-2025 16:35:33", "%d-%m-%Y %H:%M:%S")}'
		},
		{
			"PartitionKey": "5",
			"RowKey": "svc-deco-cmdb4",
			"Status": "Inactive",
			"LastLoginTime": f'{datetime.strptime("11-08-2025 07:55:07", "%d-%m-%Y %H:%M:%S")}',
			"LastLogoutTime": f'{datetime.strptime("11-08-2025 16:35:33", "%d-%m-%Y %H:%M:%S")}'
		},
		{
			"PartitionKey": "6",
			"RowKey": "svc-deco-cmdb5",
			"Status": "Inactive",
			"LastLoginTime": f'{datetime.strptime("11-05-2025 07:55:07", "%d-%m-%Y %H:%M:%S")}',
			"LastLogoutTime": f'{datetime.strptime("11-05-2025 16:35:33", "%d-%m-%Y %H:%M:%S")}'
		}
	]
	
	add_new = False
	
	from azure.data.tables import TableServiceClient
	
	table_service_client = TableServiceClient.from_connection_string(conn_str=conn_str)
	tables = [t.name for t in table_service_client.list_tables()]
	table_name = cmdb_accounts_table_name
	
	if cmdb_accounts_table_name in tables:
		table_client = TableClient.from_connection_string(conn_str=conn_str, table_name=table_name)
		entities = table_client.list_entities()
		entities = list(entities)
		if len(accounts) == len(entities):
			for entity in entities:
				entity["Status"] = "Inactive"
				entity["LastLoginTime"] = "{}".format(
					datetime.fromisoformat(entity["LastLoginTime"]).replace(tzinfo=None) if isinstance(
						entity["LastLoginTime"], str) else
					entity["LastLoginTime"])
				entity["LastLogoutTime"] = "{}".format(
					datetime.fromisoformat(entity["LastLogoutTime"]).replace(tzinfo=None) if isinstance(
						entity["LastLogoutTime"], str) else
					entity["LastLogoutTime"])
				table_client.upsert_entity(entity=entity, mode=UpdateMode.MERGE)
			
			table_client = TableClient.from_connection_string(conn_str=conn_str, table_name=cmdb_accounts_table_name)
			entities = table_client.list_entities()
			return entities
		else:
			created_entities = []
			for acc in accounts:
				try:
					entity = table_client.create_entity(entity=acc)
					created_entities.append(entity)
				except Exception as e:
					print("Already exists")
			
			return created_entities
	else:
		table_service_client = TableServiceClient.from_connection_string(conn_str=conn_str)
		table_client = table_service_client.create_table(table_name=table_name)
		# table_client = table_service_client.get_table_client(table_name=table_name)
		created_entities = []
		for acc in accounts:
			entity = table_client.create_entity(entity=acc)
			created_entities.append(entity)
		
		return created_entities


def fetch_cmdb_users_from_azure_storage(conn_str):
	ens = []
	table_client = TableClient.from_connection_string(conn_str=conn_str, table_name=cmdb_accounts_table_name)
	# entities = table_client.list_entities()
	entities = table_client.query_entities(query_filter="Status eq 'Inactive'")
	if not entities:
		print("No inactive CMDB users found in Azure Storage.")
		return ens
	
	for entity in entities:
		entity["LastLoginTime"] = "{}".format(
			datetime.fromisoformat(entity["LastLoginTime"]).replace(tzinfo=None) if isinstance(entity["LastLoginTime"],
			                                                                                   str) else entity[
				"LastLoginTime"])
		entity["LastLogoutTime"] = "{}".format(
			datetime.fromisoformat(entity["LastLogoutTime"]).replace(tzinfo=None) if isinstance(
				entity["LastLogoutTime"], str) else entity["LastLogoutTime"])
		ens.append(entity)
	# for key in entity.keys():
	#     print(f"Key: {key}, Value: {entity[key]}")
	
	return ens


def login_cmdb(conn_str, cmdb_server, password):
	try:
		cntr = 0
		cmdb_object, auth_token = None, None
		while cntr < 3:
			cmdb_object = lru_user_account(conn_str=conn_str)
			print("USER in use: ", cmdb_object["RowKey"])
			user_name = cmdb_object["RowKey"]
			login_url = cmdb_server + "/api/jwt/login"
			headers = {'Content-Type': 'application/x-www-form-urlencoded'}
			body = {'username': user_name, 'password': password}
			response = requests.post(url=login_url, data=body, headers=headers)
			result = str(response.status_code) + ' ' + response.reason
			auth_token = response.text
			
			if response.status_code not in [200, 201, 202]:
				cntr += 1
				continue
			break
			
		if cntr == 3:
			raise Exception("Failed to login to CMDB THREE attempts.")
		cmdb_object["LastLoginTime"] = "{}".format(
			datetime.strptime(datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "%d-%m-%Y %H:%M:%S").replace(tzinfo=None))
		cmdb_object["Status"] = "Active"
		update_cmdb_user_azure(cmdb_object=cmdb_object, conn_str=conn_str)
		return auth_token, cmdb_object
	except Exception as e:
		auth_token = "NO TOKEN NO LOGIN - {}".format(e).upper()
		return auth_token, None


def logout_cmdb(cmdb_server, auth_token, cmdb_object, conn_str):
	logout_url = cmdb_server + "/api/jwt/logout"
	headers = {
		'Content-Type': 'application/json',
		'Authorization': 'AR-JWT ' + auth_token
	}
	try:
		response = requests.post(url=logout_url, headers=headers)
		result = str(response.status_code)
		cmdb_object["LastLogoutTime"] = "{}".format(
			datetime.strptime(datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "%d-%m-%Y %H:%M:%S").replace(tzinfo=None))
		cmdb_object["Status"] = "Inactive"
		update_cmdb_user_azure(cmdb_object=cmdb_object, conn_str=conn_str)
	except Exception as e:
		raise Exception(f"Error during logout: {e}")
	# result = None
	return result