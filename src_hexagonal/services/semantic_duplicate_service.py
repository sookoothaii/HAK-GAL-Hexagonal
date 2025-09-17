#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Semantic Duplicate Detection Service
====================================
Detects semantically similar facts using sentence embeddings and FAISS indexing.
Ready for integration with real embedding models when Opus 4.1 design is complete.
"""

import time
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class DuplicateResult:
    """Result of duplicate detection"""
    fact: str
    is_duplicate: bool
    similarity_score: float
    similar_fact: Optional[str] = None
    similar_fact_id: Optional[int] = None
    detection_time_ms: int = 0
    metadata: Dict[str, Any] = None

class SemanticDuplicateDetector:
    """
    Semantic Duplicate Detection using sentence embeddings
    Currently implements mock embeddings, ready for real model integration
    """
    
    def __init__(self, db_path: str = "hexagonal_kb.db", threshold: float = 0.85):
        self.db_path = db_path
        self.threshold = threshold
        self.embedding_dim = 384  # Standard for all-MiniLM-L6-v2
        self.facts_cache = {}
        self.embeddings_cache = {}
        self.detection_count = 0
        self.total_detection_time = 0.0
        
        # Mock embedding model for development
        self.model_ready = False
        self._initialize_mock_model()
        
        logger.info(f"Semantic Duplicate Detector initialized (threshold: {threshold})")
    
    def _initialize_mock_model(self):
        """Initialize mock embedding model for development"""
        try:
            # Try to import real model first
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.model_ready = True
            logger.info("Real SentenceTransformer model loaded successfully")
        except ImportError:
            # Fallback to mock model
            self.model = None
            self.model_ready = False
            logger.warning("SentenceTransformer not available - using mock embeddings")
    
    def _get_mock_embedding(self, text: str) -> np.ndarray:
        """Generate mock embedding for testing"""
        # Simple hash-based mock embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to numpy array of correct dimension
        embedding = np.zeros(self.embedding_dim)
        for i in range(min(len(hash_bytes), self.embedding_dim)):
            embedding[i] = (hash_bytes[i] - 128) / 128.0  # Normalize to [-1, 1]
        
        # Add some noise for realism
        noise = np.random.normal(0, 0.1, self.embedding_dim)
        embedding += noise
        
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text (real or mock)"""
        if self.model_ready and self.model:
            return self.model.encode([text])[0]
        else:
            return self._get_mock_embedding(text)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def load_facts_from_db(self, limit: int = 1000) -> List[Tuple[str, str]]:
        """Load facts from database for indexing"""
        facts = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT statement, statement FROM facts 
                    ORDER BY rowid DESC 
                    LIMIT ?
                """, (limit,))
                
                facts = cursor.fetchall()
                logger.info(f"Loaded {len(facts)} facts from database")
                
        except Exception as e:
            logger.error(f"Failed to load facts from database: {e}")
        
        return facts
    
    def build_index(self, facts: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Build FAISS index for fast similarity search"""
        if not facts:
            return {"success": False, "error": "No facts provided"}
        
        try:
            # Try to import FAISS
            import faiss
            faiss_available = True
        except ImportError:
            faiss_available = False
            logger.warning("FAISS not available - using simple similarity search")
        
        embeddings = []
        fact_ids = []
        
        logger.info(f"Building index for {len(facts)} facts...")
        
        for fact_id, fact_text in facts:
            embedding = self._get_embedding(fact_text)
            embeddings.append(embedding)
            fact_ids.append(fact_id)
            
            # Cache for later use
            self.facts_cache[fact_id] = fact_text
            self.embeddings_cache[fact_id] = embedding
        
        embeddings_array = np.array(embeddings).astype('float32')
        
        if faiss_available:
            # Build FAISS index
            index = faiss.IndexFlatL2(self.embedding_dim)
            index.add(embeddings_array)
            
            return {
                "success": True,
                "index": index,
                "fact_ids": fact_ids,
                "embeddings": embeddings_array,
                "faiss_available": True
            }
        else:
            # Simple numpy-based search
            return {
                "success": True,
                "index": None,
                "fact_ids": fact_ids,
                "embeddings": embeddings_array,
                "faiss_available": False
            }
    
    def check_duplicate(self, fact: str, index_data: Dict[str, Any]) -> DuplicateResult:
        """
        Check if a fact is a duplicate using semantic similarity
        
        Args:
            fact: The fact to check
            index_data: Pre-built index data
            
        Returns:
            DuplicateResult with similarity information
        """
        start_time = time.time()
        
        if not index_data.get("success"):
            return DuplicateResult(
                fact=fact,
                is_duplicate=False,
                similarity_score=0.0,
                detection_time_ms=0,
                metadata={"error": "Index not available"}
            )
        
        # Get embedding for the input fact
        fact_embedding = self._get_embedding(fact)
        
        if index_data.get("faiss_available"):
            # Use FAISS for fast search
            distances, indices = index_data["index"].search(
                fact_embedding.reshape(1, -1).astype('float32'), 
                k=5
            )
            
            # Convert L2 distance to cosine similarity
            # For normalized vectors: cosine_sim = 1 - (L2_distance^2 / 2)
            similarities = 1 - (distances[0] ** 2 / 2)
            similarities = np.clip(similarities, 0, 1)  # Ensure valid range
            
        else:
            # Use simple numpy search
            embeddings = index_data["embeddings"]
            similarities = []
            indices = []
            
            for i, stored_embedding in enumerate(embeddings):
                sim = self._cosine_similarity(fact_embedding, stored_embedding)
                similarities.append(sim)
                indices.append(i)
            
            # Sort by similarity
            sorted_pairs = sorted(zip(similarities, indices), reverse=True)
            similarities = [pair[0] for pair in sorted_pairs[:5]]
            indices = [pair[1] for pair in sorted_pairs[:5]]
        
        # Check if highest similarity exceeds threshold
        max_similarity = similarities[0] if similarities else 0.0
        is_duplicate = max_similarity >= self.threshold
        
        # Get the most similar fact
        similar_fact = None
        similar_fact_id = None
        if is_duplicate and indices:
            similar_fact_id = index_data["fact_ids"][indices[0]]
            similar_fact = self.facts_cache.get(similar_fact_id, "Unknown")
        
        detection_time_ms = int((time.time() - start_time) * 1000)
        
        # Update statistics
        self.detection_count += 1
        self.total_detection_time += detection_time_ms
        
        result = DuplicateResult(
            fact=fact,
            is_duplicate=is_duplicate,
            similarity_score=max_similarity,
            similar_fact=similar_fact,
            similar_fact_id=similar_fact_id,
            detection_time_ms=detection_time_ms,
            metadata={
                "top_similarities": similarities[:3],
                "model_ready": self.model_ready,
                "faiss_available": index_data.get("faiss_available", False)
            }
        )
        
        logger.info(f"Duplicate check: {fact[:50]}... Similarity: {max_similarity:.3f}, Duplicate: {is_duplicate}")
        
        return result
    
    def batch_check_duplicates(self, facts: List[str], index_data: Dict[str, Any]) -> List[DuplicateResult]:
        """Check multiple facts for duplicates"""
        results = []
        
        for fact in facts:
            result = self.check_duplicate(fact, index_data)
            results.append(result)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detection statistics"""
        avg_time = self.total_detection_time / max(self.detection_count, 1)
        
        return {
            "detection_count": self.detection_count,
            "total_detection_time_ms": self.total_detection_time,
            "average_detection_time_ms": avg_time,
            "model_ready": self.model_ready,
            "facts_cached": len(self.facts_cache),
            "embeddings_cached": len(self.embeddings_cache),
            "threshold": self.threshold
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for the duplicate detector"""
        return {
            "status": "healthy",
            "model_ready": self.model_ready,
            "facts_cached": len(self.facts_cache),
            "ready_for_integration": True
        }

# Test function for development
def test_semantic_duplicate_detector():
    """Test the Semantic Duplicate Detector"""
    print("🧪 Testing Semantic Duplicate Detector...")
    
    # Initialize detector
    detector = SemanticDuplicateDetector(threshold=0.8)
    
    # Load facts from database
    facts = detector.load_facts_from_db(limit=100)
    print(f"📊 Loaded {len(facts)} facts from database")
    
    if not facts:
        print("❌ No facts found in database - skipping test")
        return
    
    # Build index
    print("🔨 Building semantic index...")
    index_data = detector.build_index(facts)
    
    if not index_data["success"]:
        print(f"❌ Failed to build index: {index_data.get('error')}")
        return
    
    print(f"✅ Index built successfully (FAISS: {index_data['faiss_available']})")
    
    # Test duplicate detection
    test_facts = [
        "Water boils at 100 degrees Celsius at sea level.",
        "Water boils at 100°C at standard atmospheric pressure.",  # Similar
        "The Earth is flat.",  # Different
        "The Earth orbits around the Sun.",  # Different
        "Water reaches its boiling point at 100 degrees Celsius under normal conditions."  # Similar
    ]
    
    print(f"\n🔍 Testing {len(test_facts)} facts for duplicates...")
    
    for i, fact in enumerate(test_facts, 1):
        print(f"\n{i}. Fact: {fact}")
        result = detector.check_duplicate(fact, index_data)
        print(f"   Duplicate: {result.is_duplicate}")
        print(f"   Similarity: {result.similarity_score:.3f}")
        if result.similar_fact:
            print(f"   Similar to: {result.similar_fact[:60]}...")
        print(f"   Time: {result.detection_time_ms}ms")
    
    # Show statistics
    stats = detector.get_statistics()
    print(f"\n📈 Statistics:")
    print(f"   Detections: {stats['detection_count']}")
    print(f"   Avg Time: {stats['average_detection_time_ms']:.1f}ms")
    print(f"   Model Ready: {stats['model_ready']}")
    print(f"   Facts Cached: {stats['facts_cached']}")
    
    # Health check
    health = detector.health_check()
    print(f"\n🏥 Health Check: {health['status']}")
    
    print("\n✅ Semantic Duplicate Detector test completed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_semantic_duplicate_detector()
    else:
        print("Semantic Duplicate Detector - Mock Implementation")
        print("Usage: python semantic_duplicate_service.py --test")
        print("Ready for integration with Opus 4.1 design!")