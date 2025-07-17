import ollama
from config import LLM_MODEL
import json

ACCURACY_PROMPT = """
Your task is to label an answer to a question as ’CORRECT’ or ’WRONG’. You will be given the following data:
    (1) a question (posed by one user to another user), 
    (2) a ’gold’ (ground truth) answer, 
    (3) a generated answer
which you will score as CORRECT/WRONG.

The point of the question is to ask about something one user should know about the other user based on their prior conversations.
The gold answer will usually be a concise and short answer that includes the referenced topic, for example:
Question: Do you remember what I got the last time I went to Hawaii?
Gold answer: A shell necklace
The generated answer might be much longer, but you should be generous with your grading - as long as it touches on the same topic as the gold answer, it should be counted as CORRECT. 

For time related questions, the gold answer will be a specific date, month, year, etc. The generated answer might be much longer or use relative time references (like "last Tuesday" or "next month"), but you should be generous with your grading - as long as it refers to the same date or time period as the gold answer, it should be counted as CORRECT. Even if the format differs (e.g., "May 7th" vs "7 May"), consider it CORRECT if it's the same date.

Now it's time for the real question:
Question: {question}
Gold answer: {gold_answer}
Generated answer: {generated_answer}

First, provide a short (one sentence) explanation of your reasoning, then finish with CORRECT or WRONG. 
Do NOT include both CORRECT and WRONG in your response, or it will break the evaluation script.

Just return the label CORRECT or WRONG in a json format with the key as "label".
"""

def llm_judge_similarity(a: str, b: str, question: str = None) -> float:
    """
    Use a local LLM (Ollama, llama3.2) to judge if b is a correct answer to a.
    Returns 1.0 for 'CORRECT', 0.0 for 'WRONG'.
    """
    prompt = ACCURACY_PROMPT.format(
        question=question or '',
        gold_answer=a,
        generated_answer=b
    )
    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )
    content = response['message']['content'].strip()
    # Try to parse JSON label
    try:
        label_json = json.loads(content)
        label = label_json.get('label', '').strip().upper()
    except Exception:
        # Fallback: look for CORRECT/WRONG in the text
        label = 'CORRECT' if 'CORRECT' in content.upper() else 'WRONG'
    return 1.0 if label == 'CORRECT' else 0.0 