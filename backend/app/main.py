from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import pdf, qa

app = FastAPI(title = "StudyAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf.router, prefix="/pdf")
app.include_router(qa.router)

@app.get("/")
def root():
    return {"status": "StudyAI backend is running"}