import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
client = OpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

def analyze_resume(resume_text: str, job_description: str) -> dict:
    prompt = f"""You are an Enterprise ATS Engine, Technical Recruiter, HR Specialist, and Domain Expert.

Your job is to rank resumes against job descriptions with maximum accuracy.

IMPORTANT:
Never perform generic keyword matching.
Never reward irrelevant skills.
Never assume a skill exists unless evidence appears in the resume.
Never inflate scores.

STEP 1 - DETECT JOB DOMAIN

Determine the primary domain of the job:
- Software Engineering
- Data Science
- Data Engineering
- AI/ML
- Cybersecurity
- Cloud Engineering
- DevOps
- Electronics
- Embedded Systems
- Mechanical Engineering
- Electrical Engineering
- Networking
- Product Management
- Business Analysis
- Other

Store this as job_domain.

STEP 2 - EXTRACT REQUIREMENTS

Extract and categorize requirements into:
A. Mandatory Skills
B. Preferred Skills
C. Nice-to-Have Skills
D. Education Requirements
E. Experience Requirements
F. Domain Requirements
G. Soft Skills

STEP 3 - EXTRACT RESUME EVIDENCE

Extract evidence only from:
- Experience
- Projects
- Skills
- Education
- Certifications
- Achievements

Do not infer unsupported skills.

STEP 4 - DOMAIN RELEVANCE CHECK

If job domain is Electronics:
Reward: PCB, Circuit Design, Control Panels, Wire Harness, Testing, Maintenance, Electronics Systems, Instrumentation, Electrical Components, Quality Assurance
Do NOT significantly reward: Python, Java, React, Node.js, MongoDB, Machine Learning, Data Science, Web Development (unless explicitly required).

Apply equivalent logic for every domain.

STEP 5 - SEMANTIC MATCHING

Allow equivalent technologies.
Examples: MongoDB = NoSQL, MySQL = SQL, Pandas = Data Analysis, Plotly = Data Visualization, FastAPI = Backend API, AWS = Cloud Platform

Only apply when domain relevant.

STEP 6 - TRANSFERABLE SKILLS

Transferable skills receive partial credit.
Examples: Telemetry Analysis -> Data Analytics, Research Project -> Technical Project, Team Lead -> Leadership

Partial credit only.

STEP 7 - EXPERIENCE VALIDATION

Differentiate:
Full-Time Work = 100%
Internship = 60%
Academic Project = 40%
Personal Project = 30%

Never treat projects as equivalent to industry experience.

STEP 8 - SCORING

Technical Skills = 40%
Domain Experience = 25%
Projects = 15%
Education = 10%
Certifications = 5%
Soft Skills = 5%

Calculate each category separately.

STEP 9 - PENALTIES

Missing mandatory skill: -15 to -25
Missing preferred skill: -5 to -10
Missing nice-to-have: 0
Missing core domain requirement: major penalty

STEP 10 - REALITY CHECK

Before final score, ask: "Would a real recruiter shortlist this candidate?"
If answer is no: Score must not exceed 50.
If candidate lacks multiple core requirements: Score must not exceed 40.
If candidate lacks the primary domain entirely: Score must not exceed 30.

STEP 11 - CLASSIFICATION

90-100 = Excellent Match
75-89 = Strong Match
60-74 = Potential Match
40-59 = Partial Match
0-39 = Weak Match

STEP 12 - OUTPUT JSON ONLY

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Respond ONLY with this exact JSON, no other text:
{{
    "job_domain": "",
    "score": 0,
    "classification": "",
    "matching_skills": [],
    "transferable_skills": [],
    "missing_critical_skills": [],
    "recruiter_summary": "",
    "improvements": [],
    "scoring_breakdown": {{
        "technical_skills": 0,
        "domain_experience": 0,
        "projects": 0,
        "education": 0,
        "certifications": 0,
        "soft_skills": 0
    }}
}}

Validation Rules:
- Score must be integer.
- Never output percentages.
- Never output text outside JSON.
- Never reward irrelevant domain skills.
- Prioritize recruiter realism over generosity.
- Be conservative rather than optimistic."""

    try:
        response = client.chat.completions.create(
            model="meta/llama-3.1-70b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are an Enterprise ATS Engine. Respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=3000
        )

        raw_text = response.choices[0].message.content

        cleaned_text = raw_text.strip()

        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]

        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]

        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]

        cleaned_text = cleaned_text.strip()

        json_start = cleaned_text.find("{")
        json_end = cleaned_text.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            cleaned_text = cleaned_text[json_start:json_end]

        result = json.loads(cleaned_text)

        return result

    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse AI response as JSON: {str(e)}"}

    except Exception as e:
        return {"error": f"API error: {str(e)}"}
