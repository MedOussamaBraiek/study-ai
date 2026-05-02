from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.routers import pdf, qa, learn

# app = FastAPI(title = "StudyAI API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://quizzy-ai-frontend.vercel.app"],  
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(pdf.router, prefix="/pdf")
# app.include_router(qa.router)
# app.include_router(learn.router)

# @app.get("/")
# def root():
#     return {"status": "StudyAI backend is running"}

app = FastAPI()

@app.get("/")
def root():
    return {"ok": True}