#
#                    _)
#   __ `__ \    _` |  |  __ \      __ \   |   |
#   |   |   |  (   |  |  |   |     |   |  |   |
#  _|  _|  _| \__,_| _| _|  _| _)  .__/  \__, |
#                                 _|     ____/
#

from auth.oauth import get_current_active_user
from fastapi import FastAPI, Request, Depends
from auth.views import router as auth_router
from fastapi.staticfiles import StaticFiles
from auth.decorators import login_redirect
from fastapi.responses import HTMLResponse
from api.views import router as api_router
from templates.templates import templates
from chat.utils import get_user_chats
from chat.constants import ChatAction
from uvicorn import Config, Server
from chat.models import ChatType
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
    chats = await get_user_chats(user.id)
    chats_arr = [c.dict() for c in chats]
    return templates.TemplateResponse(
        'index.html',
        {'request': request,
         'user': user,
         'chats': chats_arr,
         'chat_type': ChatType,
         'chat_action': ChatAction}
    )


if __name__ == '__main__':
    config = Config(app=app, loop=loop)
    server = Server(config)
    loop.create_task(server.serve())
    loop.run_forever()
