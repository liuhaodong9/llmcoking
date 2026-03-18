"""
Main pipeline orchestrator for DeepCoke.
Routes questions through classification → retrieval → reasoning → generation → follow-up.
"""
import logging
import asyncio
from typing import AsyncGenerator

from .classifier.question_classifier import classify_question, is_complex, needs_rag
from .classifier.query_translator import translate_query
from .vectorstore.retriever import retrieve, RetrievedChunk
from .knowledge_graph.neo4j_client import query_kg_with_llm, find_related_papers
from .generation.answer_generator import generate_answer_stream, build_evidence_context
from .followup.followup_generator import generate_followup_questions, format_followup_block
from .reasoning.escargot_runner import run_escargot_reasoning

logger = logging.getLogger("deepcoke.pipeline")


async def process_question(question: str) -> AsyncGenerator[str, None]:
    """
    Main pipeline: process a user question and yield streaming response chunks.

    This is an async generator that yields text pieces for streaming to the frontend,
    preserving the same streaming contract as the original /chat/ endpoint.

    Pipeline:
    1. Classify question type
    2. Translate to English queries (if domain question)
    3. Retrieve from vector DB + knowledge graph
    4. Route to simple RAG or ESCARGOT reasoning
    5. Generate evidence-driven answer with citations
    6. Append follow-up questions
    """
    # ── Step 1: Classify ─────────────────────────────────────────
    question_type = classify_question(question)
    logger.info(f"Question type: {question_type}")

    if not needs_rag(question_type):
        # General chat — pass through to simple LLM response
        async for chunk in _simple_chat(question):
            yield chunk
        return

    # ── Step 2: Translate query ──────────────────────────────────
    translated = translate_query(question)
    english_queries = translated["english_queries"]
    key_concepts = translated["key_concepts"]
    logger.info(f"English queries: {english_queries}")

    # ── Step 3: Retrieve evidence ────────────────────────────────
    all_chunks: list[RetrievedChunk] = []
    for eq in english_queries:
        chunks = retrieve(eq, top_k=5)
        all_chunks.extend(chunks)

    # Deduplicate by (paper_id, chunk_index) keeping highest score
    seen = {}
    for c in all_chunks:
        key = (c.paper_id, c.chunk_index)
        if key not in seen or c.score > seen[key].score:
            seen[key] = c
    all_chunks = sorted(seen.values(), key=lambda x: x.score, reverse=True)[:10]
    logger.info(f"Retrieved {len(all_chunks)} unique chunks")

    # ── Step 3b: Knowledge graph context ─────────────────────────
    kg_context = ""
    try:
        kg_results = []
        for concept in key_concepts[:3]:
            papers = find_related_papers(concept, limit=3)
            if papers:
                kg_results.extend(papers)
        if kg_results:
            kg_lines = []
            for r in kg_results[:5]:
                kg_lines.append(f"- {r.get('title', 'Unknown')} ({r.get('year', '?')}): studies {r.get('concept', '')}")
            kg_context = "\n".join(kg_lines)
    except Exception as e:
        logger.warning(f"KG retrieval failed (non-fatal): {e}")

    # ── Step 4: Reasoning (for complex questions) ────────────────
    reasoning_trace = ""
    if is_complex(question_type) and all_chunks:
        logger.info("Running ESCARGOT reasoning...")
        try:
            reasoning_trace = await asyncio.to_thread(
                run_escargot_reasoning,
                question,
                answer_type="natural",
                num_strategies=2,
                timeout=60,
            )
            if reasoning_trace and "超时" not in reasoning_trace:
                logger.info(f"ESCARGOT reasoning complete ({len(reasoning_trace)} chars)")
            else:
                reasoning_trace = ""
        except Exception as e:
            logger.warning(f"ESCARGOT reasoning failed (falling back to RAG): {e}")
            reasoning_trace = ""

    # ── Step 5: Generate answer with citations (streaming) ───────
    full_response_parts = []
    for piece in generate_answer_stream(
        question=question,
        chunks=all_chunks,
        kg_context=kg_context,
        reasoning_trace=reasoning_trace,
    ):
        full_response_parts.append(piece)
        yield piece
        await asyncio.sleep(0)

    # ── Step 6: Generate follow-up questions ─────────────────────
    full_response = "".join(full_response_parts)
    try:
        followups = generate_followup_questions(question, full_response[:500])
        followup_text = format_followup_block(followups)
        if followup_text:
            yield followup_text
    except Exception as e:
        logger.warning(f"Follow-up generation failed (non-fatal): {e}")


async def _simple_chat(question: str) -> AsyncGenerator[str, None]:
    """Simple pass-through chat for general/non-domain questions."""
    from .llm_client import chat

    system_prompt = (
        "你是焦化大语言智能问答与分析系统DeepCoke，由苏州龙泰氢一能源科技有限公司研发。"
        "以下是对你输出的强制格式要求："
        "1. 任何数学公式一定要使用 $$ 公式 $$ 包裹\n"
        "2. 多行代码一定使用三重反引号 ``` 语言 来包裹\n"
        "3. 务必使用标准 Markdown 语法。\n"
        "4. 不要提供mermaid图"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    stream = chat(messages, stream=True)
    for chunk in stream:
        if not getattr(chunk, "choices", None):
            continue
        delta = chunk.choices[0].delta
        piece = getattr(delta, "content", None)
        if not piece:
            continue
        yield piece
        await asyncio.sleep(0)


def get_pipeline_metadata(question_type: str, chunks: list, reasoning_used: bool) -> dict:
    """Build metadata dict for storing in the messages table."""
    return {
        "question_type": question_type,
        "num_chunks_retrieved": len(chunks),
        "reasoning_used": "escargot" if reasoning_used else "simple_rag",
    }
