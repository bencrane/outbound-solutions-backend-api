from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tables

app = FastAPI(
    title="Outbound Solutions API",
    description="API for accessing database tables",
    version="1.0.0"
)

# CORS - allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/")
def root():
    return {"message": "Outbound Solutions API", "docs": "/docs"}


# Include routers
app.include_router(tables.router, prefix="/api", tags=["tables"])
