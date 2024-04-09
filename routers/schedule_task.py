from fastapi import APIRouter
from fastapi.responses import JSONResponse
from config import Config	
from models.addition import Addition


schedule_task = APIRouter()


config = Config()
data = config.data()


addition_model = Addition(data)


@schedule_task.get('/tasks/execution', name='Execution of a task', description='If some task coincides with the current time, then the task is published on Instagram.', status_code=201)
async def execution():
	response_json = {'status': 'error', 'err_description': None}
	status_code = 500

	try:
		execution = await addition_model.execution()
		status = execution['status'] 
		err_description = execution['err_description']

		response_json['status'] = status 
		response_json['err_description'] = err_description 

		status_code = 201

	except Exception as e:
		response_json['err_description'] = str(e)

	return JSONResponse(content=response_json, status_code=status_code)
