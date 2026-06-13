import os  # import os module to access environment variables
import json  # import json module to parse the AI response
from openai import OpenAI  # import the OpenAI client class from the openai library
from dotenv import load_dotenv  # import load_dotenv to read the .env file

load_dotenv()  # load all variables from the .env file into the environment

HF_TOKEN = os.getenv("HF_TOKEN")  # retrieve the Hugging Face token from environment variables

client = OpenAI(
    api_key=HF_TOKEN,
    base_url="https://router.huggingface.co/v1"
)

def analyze_resume(resume_text: str, job_description: str) -> dict:  # define function taking resume text and job description, returning a dict
    """Send resume and job description to Hugging Face model and return precise structured analysis."""  # docstring

    prompt = f"""You are a strict and precise ATS (Applicant Tracking System) resume analyst.

Your job is to compare the RESUME below against the JOB DESCRIPTION below and return a highly accurate analysis.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESUME:
{resume_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JOB DESCRIPTION:
{job_description}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STRICT RULES YOU MUST FOLLOW:

1. MATCHING SKILLS:
   - Only list skills that are EXPLICITLY present in BOTH the resume AND the job description.
   - Do NOT invent skills. Do NOT assume. Only include a skill if it appears clearly in both documents.
   - Match semantically: "JS" = "JavaScript", "ML" = "Machine Learning", "React" = "React.js" are the same.

2. MISSING SKILLS:
   - Only list skills that are EXPLICITLY required or mentioned in the job description but are ABSENT from the resume.
   - Do NOT list generic skills like "communication" or "teamwork" unless the JD specifically requires them.
   - Do NOT make up skills the JD never asked for.

3. MATCH PERCENTAGE:
   - Calculate honestly: (number of JD-required skills found in resume) / (total skills required in JD) * 100
   - Adjust slightly (+/- 5%) for relevant experience, projects, or domain alignment.
   - Do NOT inflate or deflate. Be accurate.

4. STRENGTHS:
   - Write 3-4 specific strengths based on what is actually written in the resume.
   - Reference real details: actual project names, real companies, real technologies from the resume.
   - Be specific. Do NOT write generic praise.

5. AREAS FOR IMPROVEMENT:
   - Write 2-3 specific, actionable improvement points directly tied to what the JD requires and the resume lacks.
   - Reference actual missing skills or experiences from the JD.
   - Do NOT give generic advice like "improve your resume formatting".

6. AI SUGGESTIONS:
   - Write 3-4 sentences of highly specific, personalized career advice.
   - Mention the candidate's actual projects, actual skills, and actual gaps from the JD.
   - Tell them exactly what to learn, build, or do next based on THEIR resume and THIS specific job.
   - Be direct, practical, and specific. No generic advice.

7. RECOMMENDATION:
   - "Strong Match" = 70% or above
   - "Moderate Match" = 40-69%
   - "Weak Match" = below 40%

Respond ONLY in this exact JSON format. No markdown, no code blocks, no extra text:
{{
    "match_percentage": <integer 0-100>,
    "matching_skills": ["only skills present in BOTH resume and JD"],
    "missing_skills": ["only skills the JD requires that are NOT in the resume"],
    "strengths": ["specific strength 1 with real resume details", "specific strength 2", "specific strength 3"],
    "improvements": ["specific improvement 1 tied to JD gap", "specific improvement 2", "specific improvement 3"],
    "ai_suggestions": "3-4 sentences of specific, personalized advice referencing actual resume content and JD requirements",
    "recommendation": "Strong Match | Moderate Match | Weak Match"
}}"""  # build the highly detailed and strict prompt

    try:  # begin try block to catch any API or parsing errors

        response = client.chat.completions.create(  # call the Hugging Face Inference Providers API
            model="meta-llama/Llama-3.1-8B-Instruct:cheapest",  # use Llama 3.1 8B via cheapest HF provider
            messages=[  # pass the conversation messages list
                {
                    "role": "system",  # system message sets strict behavior for the model
                    "content": (
                        "You are a strict ATS resume analyst. "
                        "You ONLY report skills that genuinely appear in both documents. "
                        "You NEVER invent, assume, or hallucinate skills. "
                        "You always respond with valid JSON only and nothing else."
                    )
                },
                {
                    "role": "user",  # user message contains the full analysis prompt
                    "content": prompt  # inject the detailed prompt with resume and JD
                }
            ],
            temperature=0.1,  # very low temperature for maximum accuracy and consistency
            max_tokens=1500  # allow enough tokens for detailed, specific responses
        )

        raw_text = response.choices[0].message.content  # extract the response text from the completion

        cleaned_text = raw_text.strip()  # strip leading and trailing whitespace

        if cleaned_text.startswith("```json"):  # check for markdown json code fence
            cleaned_text = cleaned_text[7:]  # remove the opening ```json marker

        if cleaned_text.startswith("```"):  # check for plain markdown code fence
            cleaned_text = cleaned_text[3:]  # remove the opening ``` marker

        if cleaned_text.endswith("```"):  # check for closing markdown code fence
            cleaned_text = cleaned_text[:-3]  # remove the closing ``` marker

        cleaned_text = cleaned_text.strip()  # strip any remaining whitespace after fence removal

        result = json.loads(cleaned_text)  # parse the cleaned JSON string into a Python dictionary

        return result  # return the parsed dictionary containing all analysis fields

    except json.JSONDecodeError as e:  # catch JSON parsing failures specifically
        return {"error": f"Failed to parse AI response as JSON: {str(e)}"}  # return error dict with message

    except Exception as e:  # catch any other unexpected exceptions
        return {"error": f"AI API error: {str(e)}"}  # return error dict with exception message
