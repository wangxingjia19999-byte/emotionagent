from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from app.database import Base, engine
from app.models import post as post_model  # noqa: F401
from app.models import user as user_model  # noqa: F401
from app.routers import auth, home, posts, user


app = FastAPI(title="心语陪伴 API", version="1.0.0")
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
POST_UPLOAD_DIR = STATIC_DIR / "posts"
POST_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    try:
        user_columns = {column["name"] for column in inspector.get_columns("users")}
    except Exception:
        user_columns = set()

    try:
        post_columns = {column["name"] for column in inspector.get_columns("posts")}
    except Exception:
        post_columns = set()

    post_column_statements = {
        "image_url": "ALTER TABLE posts ADD COLUMN image_url VARCHAR(255) NULL",
        "image_urls": "ALTER TABLE posts ADD COLUMN image_urls TEXT NULL",
    }

    user_column_statements = {
        "occupation": "ALTER TABLE users ADD COLUMN occupation VARCHAR(100) NULL",
        "age": "ALTER TABLE users ADD COLUMN age INT NULL",
        "gender": "ALTER TABLE users ADD COLUMN gender VARCHAR(20) NULL",
    }

    with engine.begin() as connection:
        for column_name, statement in post_column_statements.items():
            if column_name not in post_columns:
                connection.execute(text(statement))

        for column_name, statement in user_column_statements.items():
            if column_name not in user_columns:
                connection.execute(text(statement))


app.include_router(auth.router, prefix="/api")
app.include_router(home.router, prefix="/api/home", tags=["首页"])
app.include_router(posts.router, prefix="/api")
app.include_router(user.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "心语陪伴 API 服务已启动"}
