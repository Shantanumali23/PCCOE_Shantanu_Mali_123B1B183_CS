"""
CodeSecure AI — RAG Subsystem Unit Tests
Tests document ingestion, chunking, metadata extraction, retrieval, and citation mapping.
"""

import unittest
from pathlib import Path
from app.services.rag_service import rag_service, DocumentChunk


class TestRAGSubsystem(unittest.TestCase):
    def setUp(self):
        # Ensure knowledge base is ingested
        self.stats = rag_service.get_stats()

    def test_knowledge_base_chunks_loaded(self):
        self.assertGreater(self.stats["total_chunks"], 0)
        self.assertIn("KB-MEM-001", self.stats["citations_available"])
        self.assertIn("KB-SEC-001", self.stats["citations_available"])

    def test_semantic_retrieval(self):
        results = rag_service.search("null pointer dereference sensor", top_k=3)
        self.assertGreater(len(results), 0)
        # Verify citation code is attached
        citation_codes = [r["citation_code"] for r in results]
        self.assertTrue(any("KB-MEM" in c or "KB-HIST" in c for c in citation_codes))

    def test_category_filtering(self):
        sec_results = rag_service.search("buffer overflow", category="Security", top_k=3)
        self.assertGreater(len(sec_results), 0)
        for r in sec_results:
            self.assertEqual(r["category"].lower(), "security")

    def test_formatted_context_structure(self):
        context = rag_service.get_formatted_context("memory leak free pointer", top_k=2)
        self.assertIsInstance(context, str)
        self.assertIn("[CITATION:", context)
        self.assertIn("KB-", context)


if __name__ == "__main__":
    unittest.main()
