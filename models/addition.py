from abc import ABC, abstractmethod
from loguru import logger
from datetime import datetime, timedelta
from instagrapi import Client 
import json
import boto3
import requests
import io 
import os


class Base(ABC):
	@abstractmethod
	def execution(self):
		pass


class Addition(Base):
	def __init__(self, data):
		self.inst_username = data.get('inst_username')
		self.inst_password = data.get('inst_password')
		self.aws_bucket_name = data.get('aws_bucket_name')
		self.aws_dynamodb_table_name = data.get('aws_dynamodb_table_name')

		aws_access_key_id = data.get('aws_access_key_id')
		aws_secret_access_key = data.get('aws_secret_access_key')
		aws_region_name = data.get('aws_region_name')

		self.dynamodb_client = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region_name)
		self.s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region_name)

	async def __delete_task(self, tasks_id, image_filenames):
		response_json = {'status': 'error', 'err_description': None}

		try:
			delete_item = self.dynamodb_client.delete_item(TableName=self.aws_dynamodb_table_name, Key={
				'id': {
					'S': tasks_id
				}
			})

			for image in image_filenames:
				self.s3_client.delete_object(Bucket=self.aws_bucket_name, Key=image)

			response_json['status'] = 'success'

		except Exception as e:
			response_json['err_description'] = str(e)

		logger.debug(response_json)
		return response_json

	async def __public_posts(self, to_implementation):
		response_json = {'status': 'error', 'err_description': None}

		try:
			inst_client = Client()

			try:
				inst_client.load_settings('session.json')

			except FileNotFoundError:
				inst_client.login(self.inst_username, self.inst_password)

			inst_client.dump_settings('session.json')

			for task in to_implementation:
				tasks_id = task['id']
				caption = task['caption']
				image_filenames = task['images']

				image_paths = []

				for image_filename in image_filenames:
					image = self.s3_client.get_object(Bucket=self.aws_bucket_name, Key=image_filename)
					image_bytes = image['Body'].read()

					with open(image_filename, 'wb') as file:
						file.write(image_bytes)

					path = os.getcwd() + '/{}'.format(image_filename)
					image_paths.append(path)

				if len(image_paths) > 1:
					album_upload = inst_client.album_upload(paths=image_paths, caption=caption)
				else:
					photo_upload = inst_client.photo_upload(paths=image_paths[0], caption=caption)
				
				delete_images = [os.remove(path) for path in image_paths]
				delete_task = await self.__delete_task(tasks_id, image_filenames)

			response_json['status'] = 'success'

		except Exception as e:
			response_json['err_description'] = str(e)

		return response_json

	async def __tasks(self):
		response_json = {'status': 'error', 'err_description': None, 'tasks': []}

		try:
			scan = self.dynamodb_client.scan(TableName=self.aws_dynamodb_table_name)
			items = scan.get('Items')
			if items is None or len(items) == 0:
				response_json['err_description'] = 'Tasks not found!'

			tasks = []
			for index, item in enumerate(items):
				keys = item.keys()
				json_info = {}
				for key in keys:
					json_info[key] = item[key]['S'] if key != 'images' else json.loads(item[key]['S'])

				tasks.append(json_info)

			response_json['status'] = 'success'
			response_json['tasks'] = tasks

		except Exception as e:
			response_json['err_description'] = str(e)

		return response_json

	async def execution(self):
		response_json = {'status': 'error', 'err_description': None}

		try:
			now = datetime.now() + timedelta(hours=3)
			current_time = now.strftime("%d.%m.%Y, %H:%M")
			logger.info(current_time)

			minute_ago = (datetime.strptime(current_time, "%d.%m.%Y, %H:%M") - timedelta(minutes=1)).strftime("%d.%m.%Y, %H:%M")
			all_tasks = await self.__tasks()
			if all_tasks['status'] == 'error':
				response_json['err_description'] = all_tasks['err_description']
				return response_json

			tasks = all_tasks['tasks']
			to_implementation = [task for task in tasks if task['date_time'] == current_time or task['date_time'] == minute_ago]
			if len(to_implementation) == 0:
				response_json['err_description'] = 'There are no suitable tasks at this time.'
				return response_json

			public_posts = await self.__public_posts(to_implementation)
			if public_posts['status'] == 'error':
				response_json['err_description'] = public_posts['err_description']
				return response_json

			response_json['status'] = 'success'

		except Exception as e:
			response_json['err_description'] = str(e)

		return response_json
