from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import user as user_model  # noqa: F401
from app.routers import auth, user


app = FastAPI(title="心语陪伴 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "心语陪伴 API 服务已启动"}
