from auth.oauth import get_current_active_user
from fastapi import FastAPI, Request, Depends
from auth.views import router as auth_router
from fastapi.staticfiles import StaticFiles
from auth.decorators import login_redirect
from fastapi.responses import HTMLResponse
from api.views import router as api_router
from templates.templates import templates
from auth.utils import get_user_contacts
from uvicorn import Config, Server
from core.utils import listener
from auth.schemes import User
import asyncio

app = FastAPI()
loop = asyncio.get_event_loop()

app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(auth_router)
app.include_router(api_router)


@app.on_event('startup')
async def startup():
    listener.start()


@app.on_event('shutdown')
async def shutdown():
    pass


@app.get('/', response_class=HTMLResponse)
@login_redirect
async def root(request: Request, user: User = Depends(get_current_active_user)):
    contacts = await get_user_contacts(user.id)
    return templates.TemplateResponse('index.html', {'request': request, 'user': user, 'contacts': contacts})


if __name__ == '__main__':
    config = Config(app=app, loop=loop)
    server = Server(config)
    loop.create_task(server.serve())
    loop.run_forever()
