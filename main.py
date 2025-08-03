# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.query_router import router as query_router
from utils.error_handlers import add_exception_handlers
import uvicorn

app = FastAPI(
    title="Advanced Database Querying System",
    description="An AI-powered system for querying databases, generating reports, and more.",
    version="1.0.0"
)

# CORS Middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add global exception handling
add_exception_handlers(app)

# Include API routers
app.include_router(query_router, prefix="/api", tags=["Query"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Advanced Database Querying API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)