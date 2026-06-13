from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.db.database import engine
from app.db import models
from app.api.routes import router as api_router

# Tell SQLAlchemy to create all tables in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Transaction Processing Pipeline",
    description="Asynchronously processes, cleans, and analyzes financial transactions.",
    version="1.0.0"
)

# Connect our API routes to the main app
app.include_router(api_router)

# Serve our new Frontend Dashboard on the root URL
@app.get("/", include_in_schema=False)
def serve_dashboard():
    return FileResponse("app/static/index.html")