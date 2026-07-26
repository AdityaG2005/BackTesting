import os
import ast
from google import genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

STRATEGY_TEMPLATE_PROMPT = """You are generating a Python trading strategy class for a backtesting engine.

The class MUST:
- Be named GeneratedStrategy
- Inherit from Strategy (already imported, do not import it yourself)
- Implement: def on_bar(self, bar, history) -> Signal
- Only use `bar` and `history` for decisions — never any external data, never look ahead
- Return Signal(signal_type=SignalType.BUY / SELL / HOLD, timestamp=bar.timestamp, ticker=bar.ticker, reason="...")
- history is a list of past Bar objects (each has .close, .open, .high, .low, .volume, .timestamp), NOT including the current bar
- Only use Python's standard library if needed (e.g. math) — no external packages

Return ONLY the Python code for the class. No explanation, no markdown fences, no extra text.

User's strategy description:
{description}
"""


def _clean_code(code: str) -> str:
    code = code.strip()
    if code.startswith("```"):
        code = code.split("```")[1]
        if code.startswith("python"):
            code = code[len("python"):]
    return code.strip()


def generate_strategy_code(description: str) -> str:
    prompt = STRATEGY_TEMPLATE_PROMPT.format(description=description)

    try:
        response = gemini_client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
        )
        return _clean_code(response.text)
    except Exception as e:
        print(f"Gemini failed ({e}), falling back to Groq...")
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return _clean_code(response.choices[0].message.content)


def validate_syntax(code: str) -> tuple[bool, str]:
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, str(e)


def compile_strategy_class(code: str):
    from app.core.strategy import Strategy, Signal, SignalType

    namespace = {
        "Strategy": Strategy,
        "Signal": Signal,
        "SignalType": SignalType,
    }

    exec(code, namespace)

    if "GeneratedStrategy" not in namespace:
        raise ValueError("Generated code did not define a class named GeneratedStrategy")

    return namespace["GeneratedStrategy"]

