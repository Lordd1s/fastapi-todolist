# uvicorn main:app --reload --host=0.0.0.0 --port=8000
# http://127.0.0.1:8000/
import uvicorn as uvicorn

from utils import Db
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse, Response

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
template = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    raw_todos = Db.select("SELECT id, title, completed FROM todos")
    todo = [
        {
            "id": x[0],
            "title": x[1],
            "completed": x[2]
        } for x in raw_todos
    ]
    return template.TemplateResponse("home.html", context={"request": request, "todos": todo})


@app.post("/add", response_class=RedirectResponse)
async def add_todo(request: Request):
    form = await  request.form()
    todo = form.get("todo").strip()
    if len(todo) <= 3:
        return template.TemplateResponse("404.html", context={"request": request})
    Db.insert_to_db("INSERT INTO todos (title) VALUES (?)", (todo, ))
    return RedirectResponse("/", status_code=303)


@app.post("/complete", response_class=RedirectResponse)
async def complete_todo(request: Request):
    form = await  request.form()
    todo_id = form.get("id")

    completed = Db.select_one("SELECT completed FROM todos WHERE id = ?", one_val=(todo_id,))
    print(completed)
    if completed[0] == 1:
        Db.update("UPDATE todos SET completed = 0 WHERE id = ?", (todo_id, ))
    else:
        Db.update("UPDATE todos SET completed = 1 WHERE id = ?", (todo_id, ))
    return RedirectResponse("/", status_code=303)


@app.post("/delete/{pk}", response_class=RedirectResponse)
async def delete(request: Request, pk):
    Db.delete_from_db("DELETE FROM todos WHERE id = ?", pk)
    return RedirectResponse("/", status_code=303)


@app.post("/update/{pk}", response_class=RedirectResponse)
async def update(request: Request, pk):
    form = await request.form()
    todo = form.get("todo").strip()

    Db.update("UPDATE todos SET title = ? WHERE id = ?", (todo, pk))
    return RedirectResponse("/", status_code=303)
