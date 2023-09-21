from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.demo_routes import router as demo_router
from routes.todo_routes import router as todo_router
from starlette.responses import RedirectResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.on_event("startup")
async def startup_event():
    global consumer_process


@app.get("/")
def main():
    return RedirectResponse(url="/docs/")


app.include_router(demo_router)
app.include_router(todo_router)
