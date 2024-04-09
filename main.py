from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from middlewares.error404 import error404
from routers.admin import admin
from routers.schedule_task import schedule_task
import uvicorn


app = FastAPI(docs_url=None, redoc_url=None)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['*'], allow_methods=['*'])
app.add_middleware(error404)
app.include_router(admin)
app.include_router(schedule_task)


@app.get('/error404', name='Page not found', description='End point, if a new route is not found.', status_code=201)
async def error404():
	content = '''
		<div style="width: 100%; text-align: center;">
			<h1>Page not found!</h1>
		</div>
	'''

	return HTMLResponse(content=content, status_code=201)


@app.get('/', name='Root page', description='The root of the application that redirects to the documentation page.', status_code=301)
def root():
	return RedirectResponse('/docs', status_code=301)


if __name__ == '__main__':
	uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)