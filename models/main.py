from abc import ABC, abstractmethod
import json
import string
import random
import boto3
import io 


class Base(ABC):
	@abstractmethod
	def tasks(self):
		pass

	@abstractmethod
	def task(self):
		pass

	@abstractmethod
	def add_task(self):
		pass

	@abstractmethod
	def delete_task(self):
		pass


class Main(Base):
	def __init__(self, data):
		self.aws_bucket_name = data.get('aws_bucket_name')
		self.aws_dynamodb_table_name = data.get('aws_dynamodb_table_name')

		aws_access_key_id = data.get('aws_access_key_id')
		aws_secret_access_key = data.get('aws_secret_access_key')
		aws_region_name = data.get('aws_region_name')

		self.dynamodb_client = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region_name)
		self.s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region_name)

	def __generate_id(self):
		return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(25))

	def __upload_images(self, images):
		response_json = {'status': 'error', 'response': None, 'names': []}

		try:
			for image in images:
				filename = image.filename
				if filename.endswith(('png', 'jpg')):
					file = image.file 
					self.s3_client.upload_fileobj(file, Bucket=self.aws_bucket_name, Key=filename)

					response_json['names'].append(filename)

			if len(response_json['names']):
				response_json['response'] = 'The request was not completed because all the images did not fit the format. Acceptable formats: jpg, png.'

			response_json['status'] = 'success'

		except Exception as e:
			response_json['response'] = str(e)

		return response_json

	def __if_task_exists(self, tasks_id):
		response_json = {'status': 'error', 'err_description': None, 'task': {}}

		try:
			tasks = self.tasks()
			if tasks['status'] == 'error':
				response_json['err_description'] = tasks['err_description']
				return response_json

			task_list = tasks['tasks']

			task = [task for task in task_list if task['id'] == tasks_id]
			if len(task) == 0:
				response_json['err_description'] = 'Task not found!'
				return response_json

			response_json['status'] = 'success'
			response_json['task'] = task[0]

		except Exception as e:
			response_json['err_description'] = str(e)

		return response_json

	def tasks(self):
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

	def task(self, tasks_id):
		response_json = {'status': 'error', 'err_description': None, 'task': {}}

		try:
			if_task_exists = self.__if_task_exists(tasks_id)
			status = if_task_exists['status']
			err_description = if_task_exists['err_description']
			task = if_task_exists['task']

			if status == 'error':
				response_json['err_description'] = err_description
				return response_json

			response_json['status'] = 'success'
			response_json['task'] = task

		except Exception as e:
			response_json['err_description'] = str(e)

		return response_json

	def add_task(self, tasks_data, images):
		response_json = {'status': 'error', 'err_description': None, 'task': {}}

		try:
			date_time = tasks_data.get('date_time')
			caption = tasks_data.get('caption')

			if not all([caption, date_time]):
				response_json['err_description'] = 'One of the parameters is missing to execute the query.'
				return response_json				

			upload_images = self.__upload_images(images)
			upload_images_status = upload_images['status']
			upload_images_response = upload_images['response']
			upload_images_names = upload_images['names']

			if upload_images_status == 'error':
				response_json['err_description'] = upload_images_response
				return response_json

			tasks_id = self.__generate_id()
			put_item = self.dynamodb_client.put_item(TableName=self.aws_dynamodb_table_name, Item={
				'id': {
					'S': tasks_id
				},

				'date_time': {
					'S': date_time
				},

				'caption': {
					'S': caption
				},

				'images': {
					'S': json.dumps(upload_images_names)
				}
			})

			tasks_data['id'] = tasks_id
			tasks_data['images'] = upload_images_names

			response_json['status'] = 'success'
			response_json['task'] = tasks_data

		except Exception as e:
			response_json['err_description'] = str(e)

		return response_json

	def delete_task(self, tasks_id):
		response_json = {'status': 'error', 'err_description': None, 'task': {}}

		try:
			if_task_exists = self.__if_task_exists(tasks_id)
			status = if_task_exists['status']
			err_description = if_task_exists['err_description']
			task = if_task_exists['task']
			image_filenames = task['images']

			if status == 'error':
				response_json['err_description'] = err_description
				return response_json

			delete_item = self.dynamodb_client.delete_item(TableName=self.aws_dynamodb_table_name, Key={
				'id': {
					'S': tasks_id
				}
			})

			for image in image_filenames:
				self.s3_client.delete_object(Bucket=self.aws_bucket_name, Key=image)

			response_json['status'] = status

		except Exception as e:
			response_json['err_description'] = str(e)

		return response_json