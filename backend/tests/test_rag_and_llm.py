import pytest
from app.services.rag_service import LegalMetrologyRAGService
from app.services.llm_service import LLMService

@pytest.fixture
def anyio_backend():
    return 'asyncio'

def test_rag_query_mrp_rule():
    rag = LegalMetrologyRAGService()
    result = rag.query("What is the mandatory rule for Maximum Retail Price MRP?")
    
    assert "query" in result
    assert "answer" in result
    assert len(result["citations"]) > 0
    assert "Rule 6" in result["answer"] or "MRP" in result["answer"] or "Maximum Retail Price" in result["answer"]

def test_rag_query_net_quantity():
    rag = LegalMetrologyRAGService()
    result = rag.query("How should net quantity be declared on packages?")
    
    assert len(result["citations"]) > 0
    assert "quantity" in result["answer"].lower()

@pytest.mark.anyio
async def test_llm_explanation_fallback():
    llm = LLMService()
    explanation = await llm.explain_rule_finding(
        rule_id="PC-DEC-007",
        field="mrp",
        detected_val="₹ 60.00",
        outcome="PASS",
        legal_reference="Rule 6(1)(e)"
    )
    assert "mrp" in explanation.lower() or "complies" in explanation.lower()
