import os
import re
import asyncio
from typing import List, Dict, Any, Optional
import pypdf
from app.core.config import settings
from app.services.llm_service import llm_service

class LegalMetrologyRAGService:
    """
    Retrieval-Augmented Generation (RAG) Service for Legal Metrology.
    Indexes the official Book on Packaged Commodities Rules 2011 (with all amendments)
    and official FAQs, and connects to local Ollama LLM for expert statutory answers.
    """

    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.is_indexed = False
        self._index_rulebooks()

    def _index_rulebooks(self):
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        pdf_files = [
            (os.path.join(root_dir, "Book_on_Legal_Metrology_Packaged_Commodities_Rules,2011_with_all_amendments_whatsnews.pdf"), "PCR_2011_Book"),
            (os.path.join(root_dir, "FAQs_on_Packaged_Commodities,_Rules_2011_whatsnews (1).pdf"), "PCR_2011_FAQs")
        ]

        for pdf_path, doc_label in pdf_files:
            if os.path.exists(pdf_path):
                try:
                    reader = pypdf.PdfReader(pdf_path)
                    for page_idx, page in enumerate(reader.pages):
                        text = page.extract_text() or ""
                        if text.strip():
                            # Split into logical chunks of ~500 characters with overlap
                            paragraphs = text.split("\n\n")
                            for p_idx, para in enumerate(paragraphs):
                                cleaned = " ".join(para.split())
                                if len(cleaned) > 50:
                                    self.documents.append({
                                        "source": doc_label,
                                        "page": page_idx + 1,
                                        "chunk_id": f"{doc_label}_p{page_idx+1}_c{p_idx}",
                                        "text": cleaned
                                    })
                except Exception as e:
                    print(f"Error indexing {pdf_path}: {e}")

        # Fallback statutory handbook chunks if PDFs not present
        if not self.documents:
            self.documents = [
                {"source": "PCR_2011_Core", "page": 1, "text": "Rule 6(1)(a): Name and complete address of the manufacturer or packer or importer must be declared on every retail package."},
                {"source": "PCR_2011_Core", "page": 2, "text": "Rule 6(1)(b): Net quantity in terms of standard unit of weight or measure or number must be declared."},
                {"source": "PCR_2011_Core", "page": 3, "text": "Rule 6(1)(d): Month and year in which commodity is manufactured or pre-packed or imported."},
                {"source": "PCR_2011_Core", "page": 4, "text": "Rule 6(1)(e): Maximum Retail Price (MRP) inclusive of all taxes in Indian Rupees (₹ or Rs.)."},
                {"source": "PCR_2011_Core", "page": 5, "text": "Rule 6(1)(ab): Country of origin must be declared for all imported commodities."},
                {"source": "PCR_2011_Core", "page": 6, "text": "Rule 6(11): Unit Sale Price (USP) in Rupees per gram/ml/piece for commodities packed in standard quantities."},
                {"source": "PCR_2011_Core", "page": 7, "text": "Rule 6(1)(n): Consumer care contact details including telephone number and email address."},
                {"source": "PCR_2011_Core", "page": 8, "text": "Rule 3: Non-applicability - retail packages containing more than 25kg or 25L, or packaged commodities meant for industrial or institutional consumers."},
            ]

        self.is_indexed = True

    async def query_async(self, question: str, top_k: int = 4) -> Dict[str, Any]:
        """
        Retrieves relevant statutory sections and generates answer via local Ollama LLM.
        """
        if not self.documents:
            return {
                "query": question,
                "answer": "Legal Metrology rulebook index is loading.",
                "citations": []
            }

        q_terms = set(re.findall(r"\w+", question.lower()))
        scored_docs = []

        for doc in self.documents:
            doc_terms = set(re.findall(r"\w+", doc["text"].lower()))
            overlap = len(q_terms.intersection(doc_terms))
            
            boost = 0
            if any(term in doc["text"].lower() for term in ["rule 6", "mrp", "net quantity", "schedule", "exemption", "amendment"]):
                boost += 2
            
            score = overlap + boost
            if score > 0:
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_matches = [d for _, d in scored_docs[:top_k]]

        if not top_matches:
            top_matches = self.documents[:top_k]

        citations = [
            {"source": d["source"], "page": d.get("page", 1), "text_snippet": d["text"][:180] + "..."}
            for d in top_matches
        ]

        # Context for Ollama
        context_text = "\n\n".join([f"Source: {d['source']} (Page {d.get('page', 1)}):\n{d['text']}" for d in top_matches[:3]])
        
        prompt = (
            f"You are the Legal Metrology AI Statutory Assistant for the Government of India. "
            f"Answer the user question using ONLY the provided official rulebook excerpts. "
            f"Always cite the exact rule numbers and source references.\n\n"
            f"Official Legal Metrology Excerpts:\n{context_text}\n\n"
            f"Question: {question}\n\n"
            f"Statutory Answer:"
        )

        ollama_answer = await llm_service.generate_response(prompt)
        if ollama_answer:
            return {
                "query": question,
                "answer": ollama_answer,
                "citations": citations,
                "generator": f"Ollama ({llm_service.model})"
            }

        # Fallback structured synthesis
        synthesis = (
            f"According to the Legal Metrology (Packaged Commodities) Rules, 2011:\n\n"
            + "\n\n".join([f"• [{d['source']} p.{d.get('page', 1)}]: {d['text']}" for d in top_matches[:3]])
        )

        return {
            "query": question,
            "answer": synthesis,
            "citations": citations,
            "generator": "Handbook Index (Ollama Standby)"
        }

    def query(self, question: str, top_k: int = 4) -> Dict[str, Any]:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Run query_async synchronously if inside running event loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, self.query_async(question, top_k)).result()
            else:
                return asyncio.run(self.query_async(question, top_k))
        except Exception:
            # Simple fallback
            return asyncio.run(self.query_async(question, top_k))

rag_service = LegalMetrologyRAGService()
