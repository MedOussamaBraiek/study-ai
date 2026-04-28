from fastapi import APIRouter, UploadFile, File, HTTPException
import pdfplumber
import io

from app.services.embedding_service import embed_texts
from app.services.vector_store import create_index

router = APIRouter()

def chunk_text_by_topic(full_text: str) -> list[dict]:
    lines = full_text.split("\n")
    chunks = []
    current_topic = "Introduction"
    current_text = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # A line is probably a heading if:
        # - it's short (less than 60 chars)
        # - doesn't end with a period (not a sentence)
        # - has real content (not just a page number)
        is_heading = (
            len(line) < 60
            and not line.endswith(".")
            and not line.isdigit()
            and len(line.split()) >= 2   # at least 2 words
        )

        if is_heading and current_text.strip():
            # Save the previous chunk before starting a new one
            chunks.append({
                "topic": current_topic,
                "text": current_text.strip()
            })
            current_topic = line
            current_text = ""
        else:
            current_text += " " + line

    # Don't forget the last chunk
    if current_text.strip():
        chunks.append({
            "topic": current_topic,
            "text": current_text.strip()
        })

    return chunks

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)): 
    # File means params required and ... means no default must be provided
    # Validate it's actually a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")
    
    # Read the file bytes
    contents = await file.read()
    
    # with is Python's way of safely opening resources
    with pdfplumber.open(io.BytesIO(contents)) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:                        
                full_text += text + "\n"

    if not full_text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from this PDF")

    # Parse into topic chunks
    chunks = chunk_text_by_topic(full_text)

    embeddings = embed_texts([c["text"] for c in chunks])
    create_index(embeddings, chunks)

    return {
        "filename": file.filename,
        "total_chunks": len(chunks),
        "chunks": chunks 
    }