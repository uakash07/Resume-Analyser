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
    """Analyze resume against job description with semantic matching and weighted scoring."""

    prompt = f"""You are a senior technical recruiter and ATS expert with 15+ years of experience.

Analyze this resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

RULES:

1. SEMANTIC MATCHING:
   - "MongoDB" IS a "NoSQL database" — match it.
   - "Scikit-learn" IS "Machine Learning" — match it.
   - "FastAPI" IS "API Development" — match it.
   - "Telemetry analysis" IS "Data Mining" — match it.
   - "House Captain" IS "Leadership" — match it.
   - Do NOT do blind keyword matching. Understand what each skill actually means.
   - Be lenient and intelligent about synonyms and related concepts.

2. PARTIAL MATCHES:
   - If the resume covers a concept but not the exact tool/level → "Partial Match"
   - Example: resume has "MongoDB" and JD asks for "NoSQL databases" → Partial Match
   - Example: resume has "FastF1/Plotly" and JD asks for "Data Visualization Tools" → Partial Match
   - Example: resume has "basic SQL" and JD asks for "complex querying" → Partial Match

3. MATCH PERCENTAGE:
   Weight the score across these categories:
   - Technical Skills (40%)
   - Projects & Experience (20%)
   - Experience Level (20%)
   - Leadership & Soft Skills (10%)
   - Domain Alignment (10%)

   A fresher with exact technical skills should NOT score the same as a 6-year experienced professional. Penalize experience gaps.

4. STRENGTHS: 2-4 specific points referencing actual resume content.

5. IMPROVEMENTS: 2-3 points tied directly to JD gaps.

6. AI SUGGESTIONS: 3-4 sentences of personalized advice.

7. RECOMMENDATION:
   - "Strong Match" = 75%+ with relevant experience
   - "Moderate Match" = 50-74%
   - "Weak Match" = below 50%

Respond ONLY with this exact JSON:
{{
    "match_percentage": <integer 0-100>,
    "matching_skills": ["skills fully present in both"],
    "partial_matching_skills": ["skills partially covered"],
    "missing_skills": ["skills in JD absent from resume"],
    "strengths": ["specific point 1", "specific point 2"],
    "improvements": ["specific point 1", "specific point 2"],
    "ai_suggestions": "personalized advice here",
    "recommendation": "Strong Match | Moderate Match | Weak Match"
}}"""

    try:

        response = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise ATS resume analyzer. "
                        "You use semantic understanding, not keyword matching. "
                        "Respond with valid JSON only."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=1500
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
