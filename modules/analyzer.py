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
    """Send resume and job description to OpenAI GPT and return structured analysis."""  # docstring

    prompt = f"""You are an expert ATS resume analyzer.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Respond ONLY in this exact JSON format with no extra text, no markdown, no code blocks:
{{
    "match_percentage": <integer 0-100>,
    "matching_skills": ["skill1", "skill2"],
    "missing_skills": ["skill1", "skill2"],
    "strengths": ["point1", "point2"],
    "improvements": ["point1", "point2"],
    "ai_suggestions": "2-3 sentence personalized advice",
    "recommendation": "Strong Match | Moderate Match | Weak Match"
}}"""  # build the structured prompt with resume text and job description injected

    try:  # begin try block to catch any API or parsing errors

        response = client.chat.completions.create(  # call the OpenAI Chat Completions API
            model="meta-llama/Llama-3.1-8B-Instruct:cheapest",  # use Llama 3.1 8B via cheapest HF provider
            messages=[  # pass the conversation messages list
                {
                    "role": "system",  # system message sets the assistant's behaviour
                    "content": "You are an expert ATS resume analyzer. Always respond with valid JSON only."  # instruct the model to return JSON only
                },
                {
                    "role": "user",  # user message contains the actual resume and JD
                    "content": prompt  # inject the full prompt with resume and job description
                }
            ],
            temperature=0.3,  # low temperature for consistent, deterministic JSON output
            max_tokens=1000  # cap the response length to avoid runaway token usage
        )

        raw_text = response.choices[0].message.content  # extract the response text from the first completion choice

        cleaned_text = raw_text.strip()  # strip leading and trailing whitespace from the response

        if cleaned_text.startswith("```json"):  # check if response starts with markdown json code fence
            cleaned_text = cleaned_text[7:]  # remove the opening ```json marker (7 characters)

        if cleaned_text.startswith("```"):  # check if response starts with plain markdown code fence
            cleaned_text = cleaned_text[3:]  # remove the opening ``` marker (3 characters)

        if cleaned_text.endswith("```"):  # check if response ends with closing markdown code fence
            cleaned_text = cleaned_text[:-3]  # remove the closing ``` marker (3 characters from end)

        cleaned_text = cleaned_text.strip()  # strip any remaining whitespace after fence removal

        result = json.loads(cleaned_text)  # parse the cleaned JSON string into a Python dictionary

        return result  # return the parsed dictionary containing all analysis fields

    except json.JSONDecodeError as e:  # catch JSON parsing failures specifically
        return {"error": f"Failed to parse OpenAI response as JSON: {str(e)}"}  # return error dict with parse message

    except Exception as e:  # catch any other unexpected exceptions (network errors, auth errors, etc.)
        return {"error": f"OpenAI API error: {str(e)}"}  # return error dict with the exception message
