import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base, run_lightweight_migrations
from app.api import auth, inspections, reviews, reports, dashboard, demo, rag, llm, tools, defects

# Create database tables
Base.metadata.create_all(bind=engine)
run_lightweight_migrations()

app = FastAPI(
    title="Legal Metrology AI Compliance Platform",
    description="AI-Powered Legal Metrology Compliance & Inspection Platform (SIH26034) with a separate AI & Computer-Vision Product Defect Inspection mode",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static storage files (uploaded images and generated PDF reports)
storage_dir = settings.STORAGE_DIR
os.makedirs(storage_dir, exist_ok=True)
app.mount("/storage", StaticFiles(directory=storage_dir), name="storage")

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(inspections.router, prefix=settings.API_V1_STR)
app.include_router(reviews.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(demo.router, prefix=settings.API_V1_STR)
app.include_router(rag.router, prefix=settings.API_V1_STR)
app.include_router(llm.router, prefix=settings.API_V1_STR)
app.include_router(tools.router, prefix=settings.API_V1_STR)
app.include_router(defects.router, prefix=settings.API_V1_STR)

@app.get("/api/health")
def health_check():
    detector = defects.defect_detector.status()
    return {
        "status": "healthy",
        "service": "Legal Metrology AI Compliance Platform",
        "version": settings.VERSION,
        "rule_engine": "ACTIVE (40+ Statutory Rules)",
        "defect_detector": f"ACTIVE ({detector['backend']}, model {'loaded' if detector['model_loaded'] else 'not loaded'})",
        "storage": "ONLINE"
    }

@app.on_event("startup")
def startup_event():
    # Automatically seed initial demo data for immediate verification
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        demo.seed_demo_data(db)
    except Exception as e:
        print(f"Demo seeding error on startup: {e}")
    try:
        defects.seed_defect_demo_data(db)
    except Exception as e:
        print(f"Defect demo seeding error on startup: {e}")
    finally:
        db.close()
