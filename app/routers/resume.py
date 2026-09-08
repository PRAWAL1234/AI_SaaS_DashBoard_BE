from sqlmodel import Session, select
from app.database import get_session
import os
from fastapi import APIRouter, Form, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.routers.models.resumeModel import Resume
from dotenv import load_dotenv

load_dotenv()

Google_API_Key = os.getenv("Google_api_key")
if not Google_API_Key:
    raise RuntimeError("Google_API_Key environment variable is not set")
    
router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)

class ResumeAnalysisResponse(BaseModel):
    overall_score: int = Field(description="Resume score out of 100")
    summary: str = Field(description="Brief AI summary of the resume strength")
    keyword_gaps: List[str] = Field(description="Missing important keywords found from general tech industry or job profile")
    formatting_suggestions: List[str] = Field(description="Suggestions to improve visual layout, spacing, or styling")
    actionable_steps: List[str] = Field(description="Bullet points on what the user should fix next")

parser = JsonOutputParser(pydantic_object=ResumeAnalysisResponse)
llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash', api_key=Google_API_Key)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert ATS (Applicant Tracking System) optimizer and HR manager. "
               "Analyze the provided resume text. You must return your response strictly matching the requested JSON schema.\n{format_instructions}"),
    ("user", "Here is the resume content:\n{resume_text}")
])


analysis_chain = prompt | llm | parser

@router.post("/uploadResume", response_model=ResumeAnalysisResponse)
async def analyze_resume(resume_text: str = Form(...), fileName: str = Form(...), user_id: int = 1, db: Session = Depends(get_session)):
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text content cannot be empty.")

    try:
        response = analysis_chain.invoke({
            "resume_text": resume_text,
            "format_instructions": parser.get_format_instructions()
        })
          # Create database object
        resume = Resume(
            user_id=user_id,
            fileName=fileName,
            resume_text=resume_text,
            overall_score=response["overall_score"],
            summary=response["summary"],
            keyword_gaps=response["keyword_gaps"],
            formatting_suggestions=response["formatting_suggestions"],
            actionable_steps=response["actionable_steps"],
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)

        return resume

    except Exception as e:
        error_msg = str(e).lower()
        print(f"Gemini API Error: {str(e)}")

        if "api_key" in error_msg or "invalid" in error_msg or "unauthenticated" in error_msg:
            raise HTTPException(
                status_code=500, 
                detail="SaaS Service is temporarily down due to configuration issues. Please try again later."
            )

        elif "quota" in error_msg or "rate limit" in error_msg or "429" in error_msg:
            raise HTTPException(
                status_code=429, 
                detail="AI server is busy. We are facing heavy traffic. Please wait a minute and try again!"
            )

        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to parse resume template. Please format your text and try again."
            )


@router.get('/getResumeByUserId', response_model=List[Resume])
async def getResume(user_id: int, db: Session = Depends(get_session)):
        try:
            resumes = db.exec(select(Resume).where(Resume.user_id == user_id)).all()
            return resumes
            
        except Exception as e:
            error_msg = str(e).lower()
            print(f"Gemini API Error: {str(e)}")

            if "api_key" in error_msg or "invalid" in error_msg or "unauthenticated" in error_msg:
                raise HTTPException(
                    status_code=500, 
                    detail="SaaS Service is temporarily down due to configuration issues. Please try again later."
                )

            elif "quota" in error_msg or "rate limit" in error_msg or "429" in error_msg:
                raise HTTPException(
                    status_code=429, 
                    detail="AI server is busy. We are facing heavy traffic. Please wait a minute and try again!"
                )

            else:
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to parse resume template. Please format your text and try again."
                )