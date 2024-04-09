from fastapi import APIRouter, Request, Form, UploadFile
from fastapi.responses import JSONResponse
from config import Config	
from models.main import Main
from typing import List
import json


admin = APIRouter()


config = Config()
data = config.data()
api_key = data.get('api_key')


main_model = Main(data)


@admin.get('/tasks/show', name='Show tasks', description='Show all pending tasks.', status_code=201)
def show_tasks(request: Request):
	response_json = {'status': 'error', 'err_description': None, 'tasks': []}
	status_code = 500

	try:
		requests_api_key = request.headers.get('api_key')
		if requests_api_key != api_key:
			response_json['err_description'] = 'Forbidden!'
			status_code = 403

		else:
			show_tasks = main_model.tasks()
			status = show_tasks['status'] 
			err_description = show_tasks['err_description']
			tasks = show_tasks['tasks']

			response_json['status'] = status 
			response_json['err_description'] = err_description 
			response_json['tasks'] = tasks 

			status_code = 201

	except Exception as e:
		response_json['err_description'] = str(e)

	return JSONResponse(content=response_json, status_code=status_code)


@admin.get('/tasks/show/{tasks_id}', name='Show task', description='Show task for it\'s id.', status_code=201)
def show_task(request: Request, tasks_id: str):
	response_json = {'status': 'error', 'err_description': None, 'task': {}}
	status_code = 500

	try:
		requests_api_key = request.headers.get('api_key')
		if requests_api_key != api_key:
			response_json['err_description'] = 'Forbidden!'
			status_code = 403

		else:
			show_task = main_model.task(tasks_id)
			status = show_task['status'] 
			err_description = show_task['err_description']
			task = show_task['task']

			response_json['status'] = status 
			response_json['err_description'] = err_description 
			response_json['task'] = task 

			status_code = 201

	except Exception as e:
		response_json['err_description'] = str(e)

	return JSONResponse(content=response_json, status_code=status_code)


@admin.post('/tasks/add', name='Add new task', description='Create a new pending task.', status_code=201)
def add_rask(request: Request, payload: str = Form(...), images: List[UploadFile] = Form(...)):
	response_json = {'status': 'error', 'err_description': None, 'task': {}}
	status_code = 500

	try:
		requests_api_key = request.headers.get('api_key')
		if requests_api_key != api_key:
			response_json['err_description'] = 'Forbidden!'
			status_code = 403

		else:
			tasks_data = json.loads(payload)
			add_task = main_model.add_task(tasks_data, images)
			status = add_task['status'] 
			err_description = add_task['err_description']
			task = add_task['task']

			response_json['status'] = status 
			response_json['err_description'] = err_description 
			response_json['task'] = task 

			status_code = 201

	except Exception as e:
		response_json['err_description'] = str(e)

	return JSONResponse(content=response_json, status_code=status_code)


@admin.delete('/tasks/delete/{tasks_id}', name='Delete task', description='Delete task for it\'s id.', status_code=201)
def delete_task(request: Request, tasks_id: str):
	response_json = {'status': 'error', 'err_description': None, 'task': {}}
	status_code = 500

	try:
		requests_api_key = request.headers.get('api_key')
		if requests_api_key != api_key:
			response_json['err_description'] = 'Forbidden!'
			status_code = 403

		else:
			delete_task = main_model.delete_task(tasks_id)
			status = delete_task['status'] 
			err_description = delete_task['err_description']
			task = delete_task['task']

			response_json['status'] = status 
			response_json['err_description'] = err_description 
			response_json['task'] = task 

			status_code = 201

	except Exception as e:
		response_json['err_description'] = str(e)

	return JSONResponse(content=response_json, status_code=status_code)
