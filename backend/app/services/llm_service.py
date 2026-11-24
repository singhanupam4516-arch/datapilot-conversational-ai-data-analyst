"""Phase 4 — Open-Source LLM Prompting.

Two narrowly-scoped prompts: the first outputs only executable Pandas code;
the second turns the computed result into a short natural-language reply.
"""
import logging
import re

from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint

from app.config import get_settings

logger = logging.getLogger(__name__)

_llm: HuggingFaceEndpoint | None = None

CODE_GENERATION_PROMPT = PromptTemplate.from_template(
    """You are a senior data analyst. You write ONLY Python Pandas code. Never write \
explanations, markdown fences, or comments.

Dataset context:
{context}

Rules:
- A cleaned DataFrame is already available as `df`. Never re-read or re-create it.
- Do not import anything; pandas, numpy, matplotlib.pyplot, and seaborn are already \
available as pd, np, plt, sns.
- Assign your final answer to a variable named `result`.
- If a chart would help answer the question, build it with seaborn/matplotlib; do not \
call plt.show().
- Do not define functions, classes, loops, or try/except blocks — direct statements only.
- Output raw code only. No ```python fences. No prose before or after.

Question: {question}

Code:"""
)

ANSWER_PHRASING_PROMPT = PromptTemplate.from_template(
    """You are a concise data analyst chatbot. In 1-3 plain sentences, answer the user's \
question using the computed result below. Do not restate the raw code. Do not invent any \
number that isn't given to you.

Question: {question}
Computed result: {result}

Answer:"""
)

_CODE_FENCE_PATTERN = re.compile(r"^```(?:python)?\s*|\s*```$", re.MULTILINE)


def get_llm() -> HuggingFaceEndpoint:
    """Lazily construct a single shared LLM client for the process."""
    global _llm
    if _llm is None:
        settings = get_settings()
        _llm = HuggingFaceEndpoint(
            repo_id=settings.llm_model_name,
            huggingfacehub_api_token=settings.huggingfacehub_api_token,
            max_new_tokens=400,
            temperature=0.1,
            task="text-generation",
        )
    return _llm


def _strip_code_fences(raw_code: str) -> str:
    return _CODE_FENCE_PATTERN.sub("", raw_code).strip()


async def generate_pandas_code(question: str, context: str) -> str:
    """Phase 4, step 1: retrieved context + question -> executable Pandas code."""
    llm = get_llm()
    prompt = CODE_GENERATION_PROMPT.format(context=context, question=question)
    raw_output = await llm.ainvoke(prompt)
    return _strip_code_fences(raw_output)


async def phrase_answer(question: str, result: object) -> str:
    """Phase 4, step 3: turn the executed result back into a natural-language reply."""
    llm = get_llm()
    prompt = ANSWER_PHRASING_PROMPT.format(question=question, result=str(result)[:2000])
    raw_output = await llm.ainvoke(prompt)
    return raw_output.strip()
