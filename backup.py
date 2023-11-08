# Copyright (C) 2023 Marcus Huber (xenorio) <dev@xenorio.xyz>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import yaml
import requests
from time import sleep

config = yaml.safe_load(open('./config.yml'))

def create_backup(identifier):
	r = requests.post(config['endpoint'] + '/api/client/servers/' + identifier + '/backups', headers={
		'Authorization': 'Bearer ' + config['key']
	})
	if r.status_code == 429:
		retry_after = r.headers['Retry-After']
		print('Ratelimited - Retrying in ' + retry_after + ' seconds')
		sleep(int(retry_after))
		return create_backup(identifier)
	elif r.status_code - 200 < 100:
		return r.json()
	else:
		print('Received Error ' + str(r.status_code) + ' - Aborting')
		quit()

def list_servers():
	r = requests.get(config['endpoint'] + '/api/client', headers={
		'Authorization': 'Bearer ' + config['key']
	})
	if r.status_code == 429:
		retry_after = r.headers['Retry-After']
		print('Ratelimited - Retrying in ' + retry_after + ' seconds')
		sleep(int(retry_after))
		return list_servers()
	elif r.status_code - 200 < 100:
		return r.json()
	else:
		print('Received Error ' + str(r.status_code) + ' - Aborting')
		quit()

def list_backups(identifier):
	r = requests.get(config['endpoint'] + '/api/client/servers/' + identifier + '/backups', headers={
		'Authorization': 'Bearer ' + config['key']
	})
	if r.status_code == 429:
		retry_after = r.headers['Retry-After']
		print('Ratelimited - Retrying in ' + retry_after + ' seconds')
		sleep(int(retry_after))
		return list_backups(identifier)
	elif r.status_code - 200 < 100:
		return r.json()
	else:
		print('Received Error ' + str(r.status_code) + ' - Aborting')
		quit()

def delete_backup(identifier, uuid):
	r = requests.delete(config['endpoint'] + '/api/client/servers/' + identifier + '/backups/' + uuid, headers={
			'Authorization': 'Bearer ' + config['key']
		})
	if r.status_code == 429:
		retry_after = r.headers['Retry-After']
		print('Ratelimited - Retrying in ' + retry_after + ' seconds')
		sleep(int(retry_after))
		return delete_backup(identifier)
	elif r.status_code - 200 < 100:
		return r.json()
	else:
		print('Received Error ' + str(r.status_code) + ' - Aborting')
		quit()

servers = list_servers()['data']

for server in servers:
	attributes = server['attributes']
	identifier = attributes['identifier']
	backup_limit = attributes['feature_limits']['backups']
	
	if backup_limit <= 0:
		continue

	data = list_backups(identifier)
	backups = data['data']
	total_backups = data['meta']['backup_count']

	if total_backups >= backup_limit:
		latest_backup = backups[0]
		delete_backup(identifier, latest_backup['attributes']['uuid'])
		print('[' + attributes['name'] + '] Deleted ' + latest_backup['attributes']['name'])

	created_backup = create_backup(identifier)

	print('[' + attributes['name'] + '] Created ' + created_backup['attributes']['name'])
