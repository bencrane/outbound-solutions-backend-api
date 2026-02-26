from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import carriers

app = FastAPI(
    title="Outbound Solutions API",
    description="FMCSA Carrier Data API",
    version="1.0.0"
)

# CORS - allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://outboundsolutions.com",
        "https://www.outboundsolutions.com",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:3006",
        "http://localhost:3007",
        "http://localhost:3008",
        "http://localhost:3009",
        "http://localhost:3010",
    ],
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


# Global exception handler - return actual error details
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Error: {str(exc)}"}
    )


# Include routers
app.include_router(carriers.router, prefix="/api", tags=["carriers"])
