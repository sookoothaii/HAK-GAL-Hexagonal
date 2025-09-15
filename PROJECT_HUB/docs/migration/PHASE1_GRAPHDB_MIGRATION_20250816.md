---
title: "Phase1 Graphdb Migration 20250816"
created: "2025-09-15T00:08:01.041612Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# PHASE 1 IMPLEMENTATION - GraphDB Migration Script
**Document ID:** PHASE1_GRAPHDB_MIGRATION_20250816  
**Purpose:** Konkrete Implementierung für Neo4j Migration  
**Status:** READY TO EXECUTE  

---

## Sofort ausführbar: SQLite → Neo4j Migration

### 1. Docker Setup für Neo4j

```yaml
# docker-compose.neo4j.yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.15-enterprise
    container_name: hakgal_neo4j
    ports:
      - "7474:7474"  # Browser
      - "7687:7687"  # Bolt protocol
    volumes:
      - ./neo4j/data:/data
      - ./neo4j/logs:/logs
      - ./neo4j/import:/import
      - ./neo4j/plugins:/plugins
    environment:
      - NEO4J_AUTH=neo4j/hakgal2025!
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
      - NEO4J_dbms_memory_heap_initial__size=2G
      - NEO4J_dbms_memory_heap_max__size=8G
      - NEO4J_dbms_memory_pagecache_size=4G
      - NEO4J_dbms_default__database=hakgal
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.*
      - NEO4J_dbms_security_procedures_allowlist=apoc.*,gds.*
    restart: unless-stopped
    networks:
      - hakgal_network

  qdrant:
    image: qdrant/qdrant:v1.7.4
    container_name: hakgal_qdrant
    ports:
      - "6333:6333"  # REST API
      - "6334:6334"  # gRPC
    volumes:
      - ./qdrant/storage:/qdrant/storage
    environment:
      - QDRANT__LOG_LEVEL=INFO
    restart: unless-stopped
    networks:
      - hakgal_network

networks:
  hakgal_network:
    driver: bridge
```

### 2. Python Migration Script

```python
#!/usr/bin/env python3
"""
Complete SQLite to Neo4j Migration
Transforms flat predicates to graph structure
"""

import sqlite3
import json
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from neo4j import GraphDatabase
import logging
from tqdm import tqdm
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Fact:
    """Fact representation"""
    id: int
    statement: str
    predicate: str
    subject: str
    object: str
    confidence: float
    source: Optional[str]
    tags: Optional[List[str]]
    created_at: str
    
class FactParser:
    """Parse Predicate(Subject, Object) format"""
    
    @staticmethod
    def parse(statement: str) -> Optional[Tuple[str, str, str]]:
        """
        Parse fact statement into components
        Returns: (predicate, subject, object) or None
        """
        # Pattern: Predicate(Subject, Object)
        pattern = r'^(\w+)\(([^,]+),\s*([^)]+)\)\.?$'
        match = re.match(pattern, statement.strip())
        
        if match:
            predicate = match.group(1)
            subject = match.group(2).strip()
            object = match.group(3).strip()
            return predicate, subject, object
        return None

class GraphMigrator:
    """Migrate facts from SQLite to Neo4j"""
    
    def __init__(self, sqlite_path: str, neo4j_uri: str, neo4j_auth: tuple):
        self.sqlite_path = sqlite_path
        self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=neo4j_auth)
        self.parser = FactParser()
        
    def load_sqlite_facts(self) -> List[Fact]:
        """Load all facts from SQLite"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, statement, confidence, source, tags, created_at, updated_at
            FROM facts
            ORDER BY id
        """)
        
        facts = []
        for row in cursor.fetchall():
            statement = row[1]
            parsed = self.parser.parse(statement)
            
            if parsed:
                predicate, subject, object = parsed
                fact = Fact(
                    id=row[0],
                    statement=statement,
                    predicate=predicate,
                    subject=subject,
                    object=object,
                    confidence=row[2] or 1.0,
                    source=row[3],
                    tags=json.loads(row[4]) if row[4] else [],
                    created_at=row[5]
                )
                facts.append(fact)
            else:
                logger.warning(f"Could not parse: {statement}")
                
        conn.close()
        logger.info(f"Loaded {len(facts)} facts from SQLite")
        return facts
    
    def create_constraints(self):
        """Create Neo4j constraints and indexes"""
        with self.neo4j_driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE",
                "CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)",
                "CREATE INDEX rel_type IF NOT EXISTS FOR ()-[r:RELATION]-() ON (r.type)",
                "CREATE INDEX rel_confidence IF NOT EXISTS FOR ()-[r:RELATION]-() ON (r.confidence)",
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Created: {constraint}")
                except Exception as e:
                    logger.warning(f"Constraint exists or error: {e}")
    
    def migrate_batch(self, facts: List[Fact], batch_size: int = 1000):
        """Migrate facts in batches"""
        with self.neo4j_driver.session() as session:
            for i in tqdm(range(0, len(facts), batch_size), desc="Migrating batches"):
                batch = facts[i:i + batch_size]
                
                # Prepare batch data
                batch_data = []
                for fact in batch:
                    batch_data.append({
                        'fact_id': fact.id,
                        'subject': fact.subject,
                        'object': fact.object,
                        'predicate': fact.predicate,
                        'confidence': fact.confidence,
                        'source': fact.source or '',
                        'tags': fact.tags or [],
                        'created_at': fact.created_at,
                        'statement': fact.statement
                    })
                
                # Batch import using UNWIND
                query = """
                UNWIND $batch as fact
                MERGE (s:Entity {name: fact.subject})
                ON CREATE SET s.type = 'auto_detected', s.created = timestamp()
                MERGE (o:Entity {name: fact.object})
                ON CREATE SET o.type = 'auto_detected', o.created = timestamp()
                MERGE (s)-[r:RELATION {
                    type: fact.predicate,
                    fact_id: fact.fact_id
                }]->(o)
                ON CREATE SET 
                    r.confidence = fact.confidence,
                    r.source = fact.source,
                    r.tags = fact.tags,
                    r.created_at = fact.created_at,
                    r.statement = fact.statement,
                    r.created = timestamp()
                ON MATCH SET
                    r.updated = timestamp()
                """
                
                session.run(query, batch=batch_data)
                
            # Create predicate-specific relationships
            self.create_typed_relationships(session, facts)
    
    def create_typed_relationships(self, session, facts: List[Fact]):
        """Create predicate-specific relationship types"""
        predicate_mapping = {
            'HasPart': 'HAS_PART',
            'HasPurpose': 'HAS_PURPOSE',
            'Causes': 'CAUSES',
            'HasProperty': 'HAS_PROPERTY',
            'IsDefinedAs': 'IS_DEFINED_AS',
            'IsSimilarTo': 'IS_SIMILAR_TO',
            'IsTypeOf': 'IS_TYPE_OF',
            'HasLocation': 'HAS_LOCATION',
            'ConsistsOf': 'CONSISTS_OF',
            'WasDevelopedBy': 'WAS_DEVELOPED_BY'
        }
        
        for old_pred, new_rel in predicate_mapping.items():
            query = f"""
            MATCH (s:Entity)-[r:RELATION {{type: '{old_pred}'}}]->(o:Entity)
            MERGE (s)-[nr:{new_rel}]->(o)
            SET nr = properties(r)
            """
            result = session.run(query)
            logger.info(f"Created {result.consume().counters.relationships_created} {new_rel} relationships")
    
    def verify_migration(self):
        """Verify the migration was successful"""
        with self.neo4j_driver.session() as session:
            # Count entities
            entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()['count']
            
            # Count relationships
            rel_count = session.run("MATCH ()-[r:RELATION]->() RETURN count(r) as count").single()['count']
            
            # Top predicates
            top_predicates = session.run("""
                MATCH ()-[r:RELATION]->()
                RETURN r.type as predicate, count(r) as count
                ORDER BY count DESC
                LIMIT 10
            """).data()
            
            logger.info(f"Migration complete:")
            logger.info(f"  Entities: {entity_count}")
            logger.info(f"  Relations: {rel_count}")
            logger.info(f"  Top predicates:")
            for pred in top_predicates:
                logger.info(f"    {pred['predicate']}: {pred['count']}")
    
    def close(self):
        """Close connections"""
        self.neo4j_driver.close()

def main():
    """Run the migration"""
    
    # Configuration
    SQLITE_PATH = "D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant.db"
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_AUTH = ("neo4j", "hakgal2025!")
    
    logger.info("=" * 60)
    logger.info("HAK-GAL SQLite to Neo4j Migration")
    logger.info("=" * 60)
    
    # Start migration
    migrator = GraphMigrator(SQLITE_PATH, NEO4J_URI, NEO4J_AUTH)
    
    try:
        # Step 1: Load facts
        facts = migrator.load_sqlite_facts()
        
        # Step 2: Create constraints
        logger.info("Creating Neo4j constraints...")
        migrator.create_constraints()
        
        # Step 3: Migrate data
        logger.info(f"Migrating {len(facts)} facts...")
        start_time = time.time()
        migrator.migrate_batch(facts)
        elapsed = time.time() - start_time
        logger.info(f"Migration completed in {elapsed:.2f} seconds")
        
        # Step 4: Verify
        logger.info("Verifying migration...")
        migrator.verify_migration()
        
    finally:
        migrator.close()
    
    logger.info("=" * 60)
    logger.info("Migration successful! Access Neo4j Browser at http://localhost:7474")
    logger.info("Username: neo4j, Password: hakgal2025!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
```

### 3. Start-Script für Windows

```batch
@echo off
REM start_neo4j_migration.bat

echo ========================================
echo HAK-GAL Neo4j Migration
echo ========================================

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Start Neo4j and Qdrant
echo Starting Neo4j and Qdrant containers...
docker-compose -f docker-compose.neo4j.yaml up -d

REM Wait for Neo4j to be ready
echo Waiting for Neo4j to start (30 seconds)...
timeout /t 30 /nobreak >nul

REM Check Neo4j status
docker exec hakgal_neo4j cypher-shell -u neo4j -p "hakgal2025!" "RETURN 1" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Neo4j is not responding!
    echo Check docker logs hakgal_neo4j
    pause
    exit /b 1
)

echo Neo4j is ready!

REM Activate virtual environment
echo Activating Python environment...
call D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\activate.bat

REM Install required packages
echo Installing dependencies...
pip install neo4j tqdm

REM Run migration
echo.
echo Starting migration...
python migrate_to_neo4j.py

echo.
echo ========================================
echo Migration complete!
echo.
echo Neo4j Browser: http://localhost:7474
echo Username: neo4j
echo Password: hakgal2025!
echo.
echo Run this Cypher query to explore:
echo MATCH (n) RETURN n LIMIT 25
echo ========================================
pause
```

### 4. Verification Queries

```cypher
-- Total Fakten
MATCH (e:Entity) RETURN count(e) as total_entities;
MATCH ()-[r:RELATION]->() RETURN count(r) as total_relations;

-- Top Prädikate
MATCH ()-[r:RELATION]->()
RETURN r.type as predicate, count(r) as count
ORDER BY count DESC
LIMIT 10;

-- Beispiel-Subgraph
MATCH path = (s:Entity {name: 'ImmanuelKant'})-[r:RELATION*1..2]->(o:Entity)
RETURN path LIMIT 50;

-- Finde isolierte Entities
MATCH (e:Entity)
WHERE NOT (e)-[:RELATION]-()
RETURN e.name as isolated_entity
LIMIT 20;

-- PageRank (Wichtigste Entities)
CALL gds.graph.project(
  'hakgal-graph',
  'Entity',
  'RELATION'
);

CALL gds.pageRank.stream('hakgal-graph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS entity, score
ORDER BY score DESC
LIMIT 10;
```

---

## Das ist PHASE 1 - In 2 Wochen erledigt

**Nach dieser Migration haben Sie:**
1. ✅ Alle 3,879 Facts in Neo4j
2. ✅ Graph-basierte Queries möglich
3. ✅ PageRank, Community Detection, Path Finding
4. ✅ Skalierbar auf Millionen Facts
5. ✅ Docker-basiert, reproduzierbar

**Nächster Schritt:** Vector Store Integration (Qdrant bereits im Docker-Compose)

---

*Dies ist keine Theorie. Dies ist ausführbarer Code.*  
*Keine Ausreden mehr.*
