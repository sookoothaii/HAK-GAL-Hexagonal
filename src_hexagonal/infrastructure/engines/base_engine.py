#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HEXAGONAL Base Engine - Abstract base for all learning engines
================================================================
Nach HAK/GAL Verfassung: Artikel 1 (Komplementäre Intelligenz)
"""

import logging
import requests
import time
from abc import ABC, abstractmethod
from typing import List, Set, Dict, Any
import os

class BaseHexagonalEngine(ABC):
    """
    Abstract base class for all HEXAGONAL learning engines
    Provides common functionality and API integration
    """
    
    def __init__(self, name: str = "BaseEngine", port: int = None):
        """
        Initialize base engine
        
        Args:
            name: Engine name for logging
            port: Engine's own port (defaults to 5002, but API always connects to 5002)
        """
        self.name = name
        # Always connect to backend on port 5002, ignore engine port parameter
        self.api_port = 5002  # Backend always runs on 5002
        self.engine_port = port if port is not None else 5002  # Engine's own port
        self.base_url = f"http://localhost:{self.api_port}"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format=f'%(asctime)s - [{self.name.upper()}] - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)
        
        # Log what we're doing
        self.logger.info(f"Initialized {self.name} for HEXAGONAL - API: {self.api_port}, Engine: {self.engine_port}")
        
        # API Endpoints
        self.COMMAND_URL = f"{self.base_url}/api/command"
        self.FACTS_URL = f"{self.base_url}/api/facts"
        self.SEARCH_URL = f"{self.base_url}/api/search"
        self.REASON_URL = f"{self.base_url}/api/reason"
        self.LLM_URL = f"{self.base_url}/api/llm/get-explanation"
        
        # Knowledge base cache
        self.existing_facts: Set[str] = set()
        self.last_kb_update = 0
        self.kb_update_interval = 60  # seconds

        # Throughput tuning (env-controlled)
        try:
            add_delay_ms = float(os.environ.get('AETHELRED_ADD_DELAY_MS', '100'))
        except Exception:
            add_delay_ms = 20.0
        self.add_delay_seconds = max(0.0, add_delay_ms / 1000.0)
        try:
            self.add_workers = int(os.environ.get('AETHELRED_ADD_WORKERS', '2'))
        except Exception:
            self.add_workers = 8
        
        self.logger.info(f"Initialized {self.name} for HEXAGONAL on port {self.api_port}")
    
    def get_existing_facts(self, force_refresh: bool = False) -> Set[str]:
        """
        Get existing facts from knowledge base with caching
        
        Args:
            force_refresh: Force refresh even if cache is fresh
            
        Returns:
            Set of existing fact statements
        """
        current_time = time.time()
        
        # Use cache if fresh
        if not force_refresh and (current_time - self.last_kb_update) < self.kb_update_interval:
            return self.existing_facts
        
        try:
            # Try HEXAGONAL endpoint first
            # Kleinere Limit und längeres Timeout für langsame API
            response = requests.get(f"{self.base_url}/api/facts", params={'limit': 1000}, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                facts = data.get('facts', [])
                
                self.existing_facts = set()
                for fact in facts:
                    if isinstance(fact, dict) and 'statement' in fact:
                        self.existing_facts.add(fact['statement'])
                    elif isinstance(fact, str):
                        self.existing_facts.add(fact)
                
                self.last_kb_update = current_time
                self.logger.info(f"Loaded {len(self.existing_facts)} facts from knowledge base")
                return self.existing_facts
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error loading facts: {e}")
        
        return self.existing_facts
    
    def add_fact(self, fact: str) -> bool:
        """
        Add a single fact to the knowledge base
        
        Args:
            fact: Fact statement in format Predicate(Entity1, Entity2).
            
        Returns:
            True if fact was added successfully
        """
        if not fact.endswith('.'):
            fact = fact + '.'
        
        try:
            # Try HEXAGONAL native endpoint
            response = requests.post(
                self.FACTS_URL,
                json={'statement': fact, 'context': {'source': self.name}},
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                self.logger.info(f"✅ Added: {fact}")
                self.existing_facts.add(fact)
                return True
            elif response.status_code == 409:
                self.logger.debug(f"Duplicate: {fact}")
                return False
            else:
                # Fallback to command endpoint
                response = requests.post(
                    self.COMMAND_URL,
                    json={'command': 'add_fact', 'query': fact},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        self.logger.info(f"✅ Added via command: {fact}")
                        self.existing_facts.add(fact)
                        return True
                        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error adding fact '{fact}': {e}")
        
        return False
    
    def add_facts_batch(self, facts: List[str]) -> int:
        """
        Add multiple facts in batch
        
        Args:
            facts: List of fact statements
            
        Returns:
            Number of facts successfully added
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        added_count = 0

        def _add_one(f: str) -> bool:
            ok = self.add_fact(f)
            if self.add_delay_seconds > 0:
                time.sleep(self.add_delay_seconds)
            return ok

        # Concurrent add with bounded workers
        with ThreadPoolExecutor(max_workers=max(1, self.add_workers)) as pool:
            futures = [pool.submit(_add_one, f) for f in facts]
            for fut in as_completed(futures):
                try:
                    if fut.result():
                        added_count += 1
                except Exception as e:
                    self.logger.debug(f"Add error: {e}")
        return added_count

    def get_confidence(self, statement: str, timeout: int = 10) -> float:
        """Query HEXAGONAL /api/reason for a confidence score of a statement.

        Returns 0.0 on error.
        """
        try:
            resp = requests.post(
                self.REASON_URL,
                json={'query': statement},
                timeout=timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                return float(data.get('confidence', 0.0))
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Confidence error: {e}")
        return 0.0
    
    def get_llm_explanation(self, topic: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Get LLM explanation for a topic with retry logic
        
        Args:
            topic: Topic to explain
            timeout: Request timeout in seconds (reduziert auf 30s)
            
        Returns:
            Dictionary with explanation and suggested facts
        """
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.LLM_URL,
                    json={'topic': topic},
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.warning(f"LLM request failed with status {response.status_code}")
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"LLM request timeout (attempt {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Kurze Pause vor Retry
                    continue
            except requests.exceptions.RequestException as e:
                self.logger.error(f"LLM request error: {e}")
                break
        
        return {'explanation': '', 'suggested_facts': []}
    
    def search_facts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for facts in the knowledge base
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching facts
        """
        try:
            response = requests.post(
                self.SEARCH_URL,
                json={'query': query, 'limit': limit},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Search error: {e}")
        
        return []
    
    @abstractmethod
    def run(self, duration_minutes: float = 15):
        """
        Main engine run method - must be implemented by subclasses
        
        Args:
            duration_minutes: How long to run the engine
        """
        pass
    
    @abstractmethod
    def generate_facts(self) -> List[str]:
        """
        Generate new facts - must be implemented by subclasses
        
        Returns:
            List of new fact statements
        """
        pass
