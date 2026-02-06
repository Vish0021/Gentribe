from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import io

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/parse_resume")
async def parse_resume(resume: UploadFile = File(...)):
    file = resume # Alias for backward compatibility in logic
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is allowed.")

    try:
        content = await file.read()
        text = ""
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # Simple Keyword Extraction (Mock AI)
        # In a real app, you'd use an LLM or NLP library here.
        # We will look for common tech skills.
        common_skills = [
            "Python", "Java", "JavaScript", "React", "Node.js", "HTML", "CSS", 
            "SQL", "NoSQL", "AWS", "Azure", "Docker", "Kubernetes", "Git",
            "Figma", "Machine Learning", "AI", "C++", "C#", "Go", "Rust",
            "TypeScript", "Angular", "Vue", "Next.js", "Tailwind"
        ]
        
        found_skills = []
        lower_text = text.lower()
        for skill in common_skills:
             # simple check, might have false positives but good for MVP
             # Adding spaces to avoid substring matches like "Go" in "Google"
            if f" {skill.lower()} " in f" {lower_text} " or \
               f" {skill.lower()}," in f" {lower_text} " or \
               f" {skill.lower()}." in f" {lower_text} " or \
               f"\n{skill.lower()}" in f" {lower_text} ":
                found_skills.append(skill)

        return {
            "text": text[:500] + "...", # Preview
            "skills": ", ".join(found_skills)
        }

    except Exception as e:
        print(f"Error parsing resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "GenTribe Resume Parser API is running"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
