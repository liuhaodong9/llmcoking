"""
Question type classifier for routing to appropriate processing pipeline.
"""
from ..llm_client import chat_json

# Question types and their descriptions
QUESTION_TYPES = {
    "factual": "asking for a specific fact, definition, or value",
    "comparison": "comparing two or more things (methods, materials, properties)",
    "causal": "asking why something happens, cause-effect relationships",
    "process": "asking how something works step-by-step",
    "recommendation": "asking for advice, best practices, or optimal parameters",
    "general_chat": "greeting, off-topic, meta-questions, or simple conversation",
}

# Types that require ESCARGOT reasoning (complex)
COMPLEX_TYPES = {"comparison", "causal", "recommendation"}
# Types that use simple RAG
SIMPLE_RAG_TYPES = {"factual", "process"}

_CLASSIFY_PROMPT = """You are a question classifier for a coal coking domain Q&A system.

Classify the user's question into EXACTLY ONE of these types:
- factual: asking for a specific fact, definition, or value
- comparison: comparing two or more things (methods, materials, properties)
- causal: asking why something happens, cause-effect relationships
- process: asking how something works step-by-step
- recommendation: asking for advice, best practices, or optimal parameters
- general_chat: greeting, off-topic, meta-questions, or simple conversation

Return ONLY the type name, nothing else."""


def classify_question(question: str) -> str:
    """
    Classify a question into one of the predefined types.

    Returns one of: factual, comparison, causal, process, recommendation, general_chat
    """
    try:
        result = chat_json(
            [{"role": "system", "content": _CLASSIFY_PROMPT},
             {"role": "user", "content": question}],
            temperature=0.0,
            max_tokens=20,
        )
        q_type = result.strip().lower().replace('"', "").replace("'", "")
        if q_type in QUESTION_TYPES:
            return q_type
        # Fuzzy match
        for key in QUESTION_TYPES:
            if key in q_type:
                return key
        return "factual"  # default
    except Exception:
        return "factual"


def is_complex(question_type: str) -> bool:
    """Whether this question type should use ESCARGOT reasoning."""
    return question_type in COMPLEX_TYPES


def needs_rag(question_type: str) -> bool:
    """Whether this question type needs RAG retrieval."""
    return question_type != "general_chat"
