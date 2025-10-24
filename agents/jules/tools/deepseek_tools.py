from langchain_core.tools import Tool
from agents.jules.clients import deepseek_client
from agents.jules.provenance import record_execution

def _summarize_and_record(text: str, max_tokens: int, model: str = "r1") -> dict:
    result = deepseek_client.summarize(text, max_tokens, model)
    record_execution(
        target="deepseek_summarize",
        actor="jules-deepseek-agent",
        inputs={"text": text, "max_tokens": max_tokens, "model": model},
        outputs=result,
        metadata={}
    )
    return result

def _ocr_and_record(filepath: str) -> dict:
    result = deepseek_client.ocr(filepath)
    record_execution(
        target="deepseek_ocr",
        actor="jules-deepseek-agent",
        inputs={"filepath": filepath},
        outputs=result,
        metadata={}
    )
    return result

def _reason_and_record(prompt: str, model: str = "v3") -> dict:
    result = deepseek_client.reason(prompt, model)
    record_execution(
        target="deepseek_reason",
        actor="jules-deepseek-agent",
        inputs={"prompt": prompt, "model": model},
        outputs=result,
        metadata={}
    )
    return result

DeepSeekSummarizeTool = Tool(
    name="deepseek_summarize",
    func=_summarize_and_record,
    description="Summarizes text using the DeepSeek API.",
)

DeepSeekOCRTool = Tool(
    name="deepseek_ocr",
    func=_ocr_and_record,
    description="Performs OCR using the DeepSeek API.",
)

DeepSeekAuditTool = Tool(
    name="deepseek_audit",
    func=_reason_and_record,
    description="Performs claim extraction and contradiction checking using the DeepSeek API.",
)
