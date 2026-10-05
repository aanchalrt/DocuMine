"""
Gemini AI service for DocuMine.
Uses the google-genai >= 2.3.0 SDK with the interactions API.
Model: gemini-2.0-flash  (gemini-3.8-flash not yet public; using latest flash)
"""
from __future__ import annotations

import json
import re
import unicodedata
from typing import Optional

from google import genai  # type: ignore

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODELS_TO_TRY = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.1-flash-lite"]
MODEL_ID = "gemini-3.5-flash-lite"

SYSTEM_INSTRUCTION = (
    "You are DocuMine AI, a document analysis assistant for coal mining regulatory "
    "documents for the Government of India / PSU sector. "
    "Always wrap extracted data in <field> tags with confidence attribute (0.0–1.0). "
    'Add flag="needs_review" to any field where confidence < 0.6. '
    "Always cite sources using <citation> tags. "
    "Never state a fact without a citation. "
    "Answer only using the provided document context. "
    "Never hallucinate data not present in documents. "
    "Output valid XML-tagged structured data as instructed."
)

# Gemini client — reads GEMINI_API_KEY from environment automatically
_client: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


def _call_gemini(prompt: str, system: str = SYSTEM_INSTRUCTION) -> str:
    """
    Execute a single-turn Gemini call. Automatically falls back to lighter models
    if rate limit or quota errors occur.
    """
    client = _get_client()
    last_exc = None
    for model_name in MODELS_TO_TRY:
        try:
            interaction = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "system_instruction": system,
                },
            )
            text = interaction.text or ""
            if text:
                return text
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            print(f"[gemini_service] Model {model_name} error: {exc}")
            continue

    print(f"[gemini_service] All models failed. Last error: {last_exc}")
    return ""


# ---------------------------------------------------------------------------
# Field extraction
# ---------------------------------------------------------------------------

_FIELD_PATTERN = re.compile(
    r'<field\s+'
    r'name="([^"]+)"\s+'
    r'value="([^"]*)"\s*'
    r'(?:unit="([^"]*)"\s*)?'
    r'confidence="([0-9.]+)"\s*'
    r'(?:flag="([^"]*)"\s*)?'
    r'/?>'
)

_ALL_FIELDS = [
    "mine_name",
    "coal_reserve_mt",
    "coal_grade",
    "annual_production_mt",
    "estimation_method",
    "fiscal_year",
    "report_date",
    "mine_type",
    "seam_depth_m",
    "water_discharge_mld",
    "dust_concentration",
    "air_quality_index",
    "plantation_area_ha",
    "sender_office",
    "recipient_office",
    "subject",
    "status",
    "monthly_production_jan",
    "monthly_production_feb",
    "monthly_production_mar",
    "monthly_production_apr",
    "monthly_production_may",
    "monthly_production_jun",
    "monthly_production_jul",
    "monthly_production_aug",
    "monthly_production_sep",
    "monthly_production_oct",
    "monthly_production_nov",
    "monthly_production_dec",
]

_FIELD_DESCRIPTIONS = "\n".join(
    [
        "- mine_name (text)",
        "- coal_reserve_mt (million_tonnes)",
        "- coal_grade (text)",
        "- annual_production_mt (million_tonnes)",
        "- estimation_method (text)",
        "- fiscal_year (text)",
        "- report_date (text)",
        "- mine_type (text)",
        "- seam_depth_m (metres)",
        "- water_discharge_mld (MLD)",
        "- dust_concentration (mg/m3)",
        "- air_quality_index (text)",
        "- plantation_area_ha (hectares)",
        "- sender_office (text, for correspondence)",
        "- recipient_office (text, for correspondence)",
        "- subject (text, for correspondence)",
        "- status (pending/resolved/escalated, for correspondence)",
        "- monthly_production_jan through monthly_production_dec (million_tonnes, from XLSX)",
    ]
)


def _build_table_summary(tables: list) -> str:
    """Render tables as compact text for the prompt."""
    if not tables:
        return ""
    parts: list[str] = ["<tables>"]
    for tbl in tables[:5]:  # Cap at 5 tables to stay within token budget
        if isinstance(tbl, dict):
            # XLSX format: {sheet, headers, rows}
            parts.append(f'<sheet name="{tbl.get("sheet", "")}">')
            headers = tbl.get("headers", [])
            parts.append(" | ".join(str(h) for h in headers))
            for row in tbl.get("rows", [])[:30]:
                parts.append(" | ".join(str(v) for v in row.values()))
            parts.append("</sheet>")
        elif isinstance(tbl, list):
            # PDF / DOCX format: list of lists
            for row in tbl[:20]:
                parts.append(" | ".join(str(cell) for cell in row))
    parts.append("</tables>")
    return "\n".join(parts)


def extract_fields(
    doc_id: str,
    doc_name: str,
    doc_type: str,
    text: str,
    tables: list,
) -> list[dict]:
    """
    Ask Gemini to extract structured fields from a document.

    Returns a list of dicts with keys: name, value, unit, confidence, flag.
    """
    table_summary = _build_table_summary(tables)

    prompt = f"""<document id="{doc_id}" name="{doc_name}" type="{doc_type}">
{text[:8000]}
{table_summary}
</document>

Extract ALL of these fields if present. Return ONLY valid XML <field> tags, one per line, nothing else:
{_FIELD_DESCRIPTIONS}

For each field use format: <field name="..." value="..." unit="..." confidence="0.0-1.0"/>
If confidence < 0.6, add flag="needs_review"
If a field is not found, skip it.
"""

    raw_output = _call_gemini(prompt)
    return _parse_field_tags(raw_output)


def _parse_field_tags(raw: str) -> list[dict]:
    """Parse <field .../> XML tags from Gemini output using regex."""
    results: list[dict] = []
    for match in _FIELD_PATTERN.finditer(raw):
        name = match.group(1)
        value = match.group(2)
        unit = match.group(3) or ""
        try:
            confidence = float(match.group(4))
        except (TypeError, ValueError):
            confidence = 0.5
        flag = match.group(5) or (
            "needs_review" if confidence < 0.6 else None
        )
        results.append(
            {
                "name": name,
                "value": value,
                "unit": unit,
                "confidence": confidence,
                "flag": flag,
            }
        )
    return results


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

_REPORT_TEMPLATE = """
Generate a professional Mine Status Summary Report in HTML format.
Fill in ALL sections using ONLY data from the documents provided.
After EVERY factual statement include a <citation doc_id="..." field="..."/> tag.

Required sections (use proper HTML h2/h3 headings, p tags, ul/li for lists):

<h1>Mine Status Summary Report</h1>

<h2>1. Executive Summary</h2>
<!-- Brief overview of findings -->

<h2>2. Mine Details</h2>
<!-- Mine name, type, location, fiscal year -->

<h2>3. Coal Reserves & Resources</h2>
<!-- Reserve estimates, coal grade, estimation method -->

<h2>4. Production Performance</h2>
<!-- Annual production, monthly breakdown if available -->

<h2>5. Environmental Compliance</h2>
<!-- Water discharge, dust, AQI, plantation area -->

<h2>6. Key Observations</h2>
<!-- Notable conflicts, data gaps, or concerns -->

<h2>7. Disclaimer</h2>
<p>This report has been auto-generated by DocuMine AI from the provided document corpus.
All figures should be independently verified before official use.</p>
"""


def generate_report(doc_data: list[dict], report_type: str = "mine_status_summary") -> str:
    """
    Generate an HTML mine status report from extracted document data.
    Returns an HTML string.
    """
    doc_blocks = "\n".join(
        f'<document id="{d.get("id", "")}" name="{d.get("filename", "")}" '
        f'type="{d.get("doc_type", "")}">\n'
        f'{str(d.get("raw_text", ""))[:3000]}\n'
        f'<fields>\n'
        + "\n".join(
            f'<field name="{f.get("name")}" value="{f.get("value")}" '
            f'unit="{f.get("unit", "")}" confidence="{f.get("confidence", 0)}"/>'
            for f in (d.get("fields") or [])
        )
        + "\n</fields>\n</document>"
        for d in doc_data
    )

    prompt = f"""You are generating a {report_type} for a coal mine regulatory dossier.

Documents:
{doc_blocks}

{_REPORT_TEMPLATE}

IMPORTANT:
- Use ONLY data from the documents above.
- Add a <citation doc_id="..." field="..."/> tag after every factual claim.
- Return complete valid HTML (no markdown fences).
- If data is unavailable for a section, write "Data not available in provided documents."
"""

    html = _call_gemini(prompt)

    # If Gemini wraps in markdown fences, strip them
    html = re.sub(r"^```html?\s*", "", html, flags=re.IGNORECASE)
    html = re.sub(r"```$", "", html.strip())

    return html or "<p>Report generation failed. Please retry.</p>"


# ---------------------------------------------------------------------------
# Word cloud data
# ---------------------------------------------------------------------------

def get_word_cloud_data(texts: list[str]) -> list[dict]:
    """
    Ask Gemini for the top 20 mining/geological keywords with weights 1–100.
    Returns list of {word: str, weight: int}.
    """
    combined = " ".join(texts)[:6000]

    prompt = f"""Analyse the following text from coal mining documents and identify the top 20 most important domain-specific keywords related to mining, geology, production, and regulation.

Text:
{combined}

Return ONLY a valid JSON array with no additional commentary, markdown, or explanation.
Format: [{{"word": "coal", "weight": 95}}, ...]
Weights must be integers between 1 and 100, proportional to keyword importance and frequency.
"""

    raw = _call_gemini(prompt)

    # Strip markdown fences if present
    raw = re.sub(r"^```json?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```$", "", raw.strip())

    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [
                {"word": str(item.get("word", "")), "weight": int(item.get("weight", 1))}
                for item in data
                if item.get("word")
            ]
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"[gemini_service] Word cloud JSON parse error: {exc}\nRaw: {raw[:200]}")

    # Graceful fallback
    return [{"word": "coal", "weight": 90}, {"word": "mine", "weight": 80}]


# ---------------------------------------------------------------------------
# Chat query
# ---------------------------------------------------------------------------

_DEVANAGARI_RANGE = re.compile(r"[\u0900-\u097F]")
_CITATION_PATTERN = re.compile(
    r'<citation\s+doc_id="([^"]+)"\s+field="([^"]+)"\s*/>'
)


def chat_query(
    question: str,
    documents: list[dict],
    previous_interaction_id: Optional[str] = None,
) -> dict:
    """
    Answer a user query grounded in the provided documents.

    Returns:
        {
            "answer": str,
            "language": "en" | "hi",
            "citations": list[dict],  # [{doc_id, field}]
        }
    """
    lang = "hi" if _DEVANAGARI_RANGE.search(question) else "en"

    doc_blocks = "\n".join(
        f'<document id="{d.get("id", "")}" name="{d.get("filename", "")}" '
        f'type="{d.get("doc_type", "")}">\n'
        f'{str(d.get("raw_text", ""))[:3000]}\n'
        "</document>"
        for d in documents
    )

    hindi_instruction = (
        "Respond in Hindi (Devanagari script)." if lang == "hi" else "Respond in English."
    )

    prompt = f"""<query lang="{lang}">{question}</query>

{doc_blocks}

Instructions:
1. Answer the query directly, politely, and in natural, human conversational language.
2. {hindi_instruction}
3. Base your answer strictly on the provided documents.
4. After every factual statement, add a citation tag: <citation doc_id="..." field="..."/> citing the source document.
5. Do NOT output raw XML or JSON tags in your conversational response (other than <citation> tags).
6. If the question cannot be answered from the documents, explain that politely in clear language.
"""

    raw_answer = _call_gemini(prompt)

    # Extract citation tags
    citations: list[dict] = [
        {"doc_id": m.group(1), "field": m.group(2)}
        for m in _CITATION_PATTERN.finditer(raw_answer)
    ]

    # Clean citation tags from displayed answer
    clean_answer = _CITATION_PATTERN.sub("", raw_answer).strip()

    return {
        "answer": clean_answer,
        "language": lang,
        "citations": citations,
    }
