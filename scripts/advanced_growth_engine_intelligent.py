#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HAK-GAL INTELLIGENT Adaptive Growth Engine
==========================================
Version: 2.0 - Mit echter Gap-Detection und Duplikat-Vermeidung
Features:
- Failed attempts cache
- Semantic similarity check
- Echte Knowledge Gap Analyse
- Priorisierte Topic-Generierung
- Lernendes System
"""

import requests
import json
import time
import re
import random
import os
import sqlite3
import hashlib
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime

# --- CONFIGURATION ---
API_BASE_URL = "http://localhost:5002/api"
DB_PATH = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db")
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
CACHE_FILE = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\failed_attempts_cache.json")

# --- QUALITY GATE CONFIG ---
# Sinnvolle Prädikate zulassen
PREDICATE_WHITELIST = {
    "Uses", "UsedFor", "UsedIn", "Requires", "PartOf", "Algorithm", "Causes", "MayCause",
    "Process", "Mechanism", "Architecture", "LocatedIn", "DevelopedBy",
    "Supports", "Provides", "Enables"
}

# Platzhalter-Tokens blockieren
PLACEHOLDER_TOKENS = {
    "Context", "Intermediate", "Relationship", "Component1", "Component2", "Component3",
    "Input", "Output", "Layer1", "Layer2", "Layer3", "Layer4", "Node1", "Node2", "Node3",
    "Phase1", "Phase2", "Phase3", "Significant", "Applications", "Init", "Validate", "Edge"
}

def _get_env_flag(name: str, default: bool) -> bool:
    v = str(os.environ.get(name, str(int(default)))).lower()
    return v in ("1", "true", "yes", "on")

class QualityGate:
    """Mehrstufiges Qualitäts-Gate für Kandidatenfakten.
    - Whitelist für Prädikate
    - Platzhalter-Blocker
    - KB-Support (beide Entitäten belegt, mind. 1 gemeinsamer Nachbar)
    - LLM-Rationale-Gate (Erklärung enthält beide Entitäten und Prädikat)
    - Confidence-Gate über /api/reason
    Per ENV deaktivier-/parametrierbar.
    """

    def __init__(self, api_base: str, api_key: str):
        self.api_base = api_base
        self.headers = {"Content-Type": "application/json", "X-API-Key": api_key}
        try:
            self.min_conf = float(os.environ.get("AETHELRED_MIN_CONFIDENCE", "0.65"))
        except Exception:
            self.min_conf = 0.65
        self.enable_kb_support = _get_env_flag("AETHELRED_ENABLE_KB_SUPPORT_GATE", True)
        self.enable_llm_gate = _get_env_flag("AETHELRED_ENABLE_LLM_GATE", True)
        self.enable_conf_gate = _get_env_flag("AETHELRED_ENABLE_CONF_GATE", True)

    def _predicate(self, fact: str) -> str:
        m = re.match(r'^([A-Za-z0-9_]+)\(', fact.strip().rstrip('.'))
        return m.group(1) if m else ""

    def _entities(self, fact: str) -> Optional[Tuple[str, str]]:
        m = re.match(r'^[A-Za-z0-9_]+\(([^,]+),\s*([^)]+)', fact.strip().rstrip('.'))
        if not m:
            return None
        return m.group(1).strip(), m.group(2).strip()

    def is_whitelisted(self, fact: str) -> bool:
        return self._predicate(fact) in PREDICATE_WHITELIST

    def has_placeholders(self, fact: str) -> bool:
        return any(tok in fact for tok in PLACEHOLDER_TOKENS)

    def kb_support(self, e1: str, e2: str) -> bool:
        if not self.enable_kb_support:
            return True
        try:
            s1 = requests.post(f"{self.api_base}/search", headers=self.headers, json={"query": e1, "limit": 20}, timeout=15)
            s2 = requests.post(f"{self.api_base}/search", headers=self.headers, json={"query": e2, "limit": 20}, timeout=15)
            if s1.status_code != 200 or s2.status_code != 200:
                return False
            r1 = s1.json().get("results", [])
            r2 = s2.json().get("results", [])
            # Locker: je Entität mindestens 1 Vorkommen
            if len(r1) < 1 or len(r2) < 1:
                return False
            n1 = [x.get("statement", "") for x in r1 if isinstance(x, dict)]
            n2 = [x.get("statement", "") for x in r2 if isinstance(x, dict)]
            set1, set2 = set(n1), set(n2)
            if len(set1 & set2) >= 1:
                return True
            # Alternativ: irgendein Statement erwähnt beide Entitäten (Substring-Check)
            el1, el2 = e1.lower(), e2.lower()
            for stmt in (n1 + n2):
                stl = stmt.lower()
                if el1 in stl and el2 in stl:
                    return True
            return False
        except Exception:
            return False

    def llm_rationale_ok(self, e1: str, e2: str, pred: str) -> bool:
        if not self.enable_llm_gate:
            return True
        try:
            r = requests.post(
                f"{self.api_base}/llm/get-explanation",
                headers=self.headers,
                json={"topic": f"{e1} {pred} {e2}"},
                timeout=20
            )
            if r.status_code != 200:
                return False
            data = r.json()
            txt = (data.get("explanation") or "")[:2000].lower()
            if (e1.lower() in txt) and (e2.lower() in txt) and (pred.lower() in txt):
                return True
            # Zusätzliche Akzeptanz, wenn LLM strukturierte Fakten liefert, die passen
            suggested = []
            for key in ("facts", "suggested_facts"):
                v = data.get(key)
                if isinstance(v, list):
                    suggested.extend([str(x) for x in v])
            target1 = f"{pred}({e1}, {e2})".lower()
            target2 = f"{pred}({e2}, {e1})".lower()
            for f in suggested:
                fs = f.strip().rstrip('.')
                if fs.lower() in (target1, target2):
                    return True
            return False
        except Exception:
            return False

    def confidence_ok(self, fact: str) -> bool:
        if not self.enable_conf_gate:
            return True
        try:
            r = requests.post(f"{self.api_base}/reason", headers=self.headers, json={"query": fact}, timeout=15)
            if r.status_code != 200:
                return False
            conf = float(r.json().get("confidence", 0.0))
            return conf >= self.min_conf
        except Exception:
            return False

    def passes(self, fact: str) -> bool:
        if not self.is_whitelisted(fact):
            return False
        if self.has_placeholders(fact):
            return False
        ents = self._entities(fact)
        if not ents:
            return False
        e1, e2 = ents
        pred = self._predicate(fact)
        if not self.kb_support(e1, e2):
            return False
        if not self.llm_rationale_ok(e1, e2, pred):
            return False
        if not self.confidence_ok(fact):
            return False
        return True

# --- INTELLIGENT CACHE MANAGER ---
class IntelligentCache:
    """Verwaltet Failed Attempts und bereits existierende Fakten"""
    
    def __init__(self, cache_file: Path):
        self.cache_file = cache_file
        self.failed_attempts = set()
        self.existing_facts = set()
        self.similar_facts = {}  # Hash -> [similar facts]
        self.load_cache()
        
    def load_cache(self):
        """Lade Cache von Disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.failed_attempts = set(data.get('failed', []))
                    self.existing_facts = set(data.get('existing', []))
                    print(f"📁 Cache geladen: {len(self.failed_attempts)} failed, {len(self.existing_facts)} existing")
            except:
                pass
    
    def save_cache(self):
        """Speichere Cache auf Disk"""
        data = {
            'failed': list(self.failed_attempts)[:5000],  # Limit size
            'existing': list(self.existing_facts)[:5000],
            'timestamp': datetime.now().isoformat()
        }
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    
    def normalize_fact(self, fact: str) -> str:
        """Normalisiere Fakt für Vergleich"""
        # Entferne Whitespace und lowercase
        normalized = re.sub(r'\s+', '', fact.lower())
        # Entferne Punkt am Ende wenn vorhanden
        if normalized.endswith('.'):
            normalized = normalized[:-1]
        return normalized
    
    def fact_hash(self, fact: str) -> str:
        """Erstelle Hash für schnellen Lookup"""
        normalized = self.normalize_fact(fact)
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def is_duplicate(self, fact: str) -> bool:
        """Prüfe ob Fakt bereits existiert oder fehlgeschlagen ist"""
        fact_hash = self.fact_hash(fact)
        normalized = self.normalize_fact(fact)
        
        # Check exact matches
        if fact in self.failed_attempts or fact in self.existing_facts:
            return True
        
        # Check normalized version
        if normalized in {self.normalize_fact(f) for f in self.failed_attempts}:
            return True
        if normalized in {self.normalize_fact(f) for f in self.existing_facts}:
            return True
            
        return False
    
    def add_failed(self, fact: str):
        """Füge zu Failed Attempts hinzu"""
        self.failed_attempts.add(fact)
        self.existing_facts.add(fact)  # Auch als existierend markieren
        
    def add_existing(self, fact: str):
        """Markiere als bereits existierend"""
        self.existing_facts.add(fact)

# --- KNOWLEDGE GAP ANALYZER ---
class KnowledgeGapAnalyzer:
    """Analysiert echte Wissenslücken in der KB"""
    
    def __init__(self, db_path: Path, api_base: str):
        self.db_path = db_path
        self.api_base = api_base
        
    def get_entity_statistics(self) -> Dict[str, int]:
        """Hole Entity-Statistiken aus der KB"""
        # Skip API and go directly to DB - API returns wrong format
        return self._get_entity_stats_from_db()
    
    def _get_entity_stats_from_db(self) -> Dict[str, int]:
        """Hole Entity-Stats direkt aus DB"""
        stats = Counter()
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT statement FROM facts")
            
            for row in cursor.fetchall():
                fact = row[0]
                # Extract entities - handle multi-argument facts
                match = re.match(r'^([A-Za-z0-9_]+)\(([^)]+)\)', fact)
                if match:
                    args_str = match.group(2)
                    # Split carefully to handle complex arguments
                    args = re.split(r',\s*', args_str)
                    for arg in args:
                        # Clean and extract entity names
                        clean_arg = arg.strip()
                        # Remove special chars but keep entity names
                        entity = re.sub(r'[^A-Za-z0-9_]', '', clean_arg)
                        # Filter out dates, numbers, and generic terms
                        if (entity and len(entity) > 2 and 
                            not entity.isdigit() and 
                            not re.match(r'^\d{4}_\d{2}_\d{2}', entity) and
                            not re.match(r'^\d+User', entity) and
                            not entity.lower() in ['true', 'false', 'none', 'null', 'undefined']):
                            stats[entity] += 1
            
            conn.close()
            print(f"  📊 Found {len(stats)} unique entities in KB")
        except Exception as e:
            print(f"❌ DB Error: {e}")
            
        return dict(stats)
    
    def find_underrepresented_entities(self, stats: Dict[str, int], threshold: float = 0.5) -> List[str]:
        """Finde unterrepräsentierte Entitäten"""
        if not stats:
            return []
            
        values = list(stats.values())
        avg = sum(values) / len(values) if values else 0
        # Bei niedrigem Durchschnitt absoluten Schwellwert verwenden
        threshold_value = max(2, avg * threshold)  # Mindestens 2 Verbindungen
        
        underrepresented = [
            entity for entity, count in stats.items()
            if count < threshold_value and count > 0
        ]
        
        return sorted(underrepresented, key=lambda x: stats[x])[:20]
    
    def find_isolated_entities(self, min_connections: int = 2) -> List[str]:
        """Finde isolierte Entitäten mit wenigen Verbindungen"""
        isolated = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Finde Entities die nur in wenigen Fakten vorkommen
            cursor.execute("""
                SELECT entity, COUNT(*) as cnt
                FROM (
                    SELECT DISTINCT 
                        SUBSTR(statement, 
                               INSTR(statement, '(') + 1,
                               INSTR(statement, ',') - INSTR(statement, '(') - 1
                        ) as entity
                    FROM facts
                    WHERE statement LIKE '%,%'
                )
                GROUP BY entity
                HAVING cnt <= ?
                LIMIT 50
            """, (min_connections,))
            
            isolated = [row[0] for row in cursor.fetchall()]
            conn.close()
            
        except Exception as e:
            print(f"❌ Isolation check error: {e}")
            
        # Post-Filter: Junk-Entities entfernen (Dates, IDs, generics)
        filtered: List[str] = []
        for entity in isolated:
            if not entity:
                continue
            e = entity.strip()
            if len(e) <= 2:
                continue
            if e.isdigit():
                continue
            if re.match(r'^\d{4}_\d{2}_\d{2}$', e):
                continue
            if re.match(r'^\d+User$', e):
                continue
            if e.lower() in ['true', 'false', 'none', 'null', 'undefined']:
                continue
            filtered.append(e)
        return filtered
    
    def suggest_connections(self, underrepresented: List[str], well_connected: List[str]) -> List[Tuple[str, str]]:
        """Schlage sinnvolle Verbindungen vor"""
        suggestions = []
        
        for under in underrepresented[:10]:
            for well in well_connected[:5]:
                if under != well:
                    suggestions.append((under, well))
        
        return suggestions[:20]

# --- INTELLIGENT TOPIC GENERATOR ---
class IntelligentTopicGenerator:
    """Generiert Topics basierend auf echten Knowledge Gaps"""
    
    def __init__(self, gap_analyzer: KnowledgeGapAnalyzer):
        self.gap_analyzer = gap_analyzer
        self.exhausted_topics = set()
        self.priority_queue = []
        
    def generate_priority_topics(self) -> List[Dict]:
        """Generiere priorisierte Topics basierend auf Gaps"""
        topics = []
        
        # 1. Hole Entity-Statistiken
        stats = self.gap_analyzer.get_entity_statistics()
        
        if not stats:
            print("⚠️ Keine Entity-Statistiken verfügbar")
            return self._fallback_topics()
        
        # 2. Finde unterrepräsentierte Bereiche
        underrepresented = self.gap_analyzer.find_underrepresented_entities(stats)
        
        # Noise-Heuristik: filtere Token-Muster wie "3_5M_Parameters_Not_572k"
        def is_noise_entity(entity: str) -> bool:
            if not entity:
                return True
            e = entity.strip()
            el = e.lower()
            # sehr kurz
            if len(e) <= 2:
                return True
            # Zahlen kombiniert mit Underscores
            if '_' in e and re.search(r'\d', e):
                return True
            # Alphanumerische Mischungen mit Ziffern direkt an Buchstaben (z. B. 5gNetworks)
            if re.search(r'\d+[A-Za-z]|[A-Za-z]+\d+', e):
                # Erlaube gängige Tech-Begriffe explizit
                if el not in { '5gnetworks', '4g', '3g'}:
                    return True
            # Parameter-/Metrik-Tokens
            metric_tokens = {'parameters','not','count','ms','seconds','percent','kb','mb','gb'}
            if any(tok in el for tok in metric_tokens):
                return True
            return False
        
        underrepresented = [u for u in underrepresented if not is_noise_entity(u)]
        
        # 3. Finde gut vernetzte Entities
        well_connected = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:20]
        well_connected_names = [e[0] for e in well_connected]

        # Domain Guard: nur sinnvolle Domänen-Bridges zulassen
        def classify_entity(entity: str) -> str:
            el = entity.lower()
            if el.startswith('source_') or 'venv' in el or 'scripts' in el or 'activate' in el:
                return 'system_internal'
            # einfache History-Pattern (Jahreszahlen/epochen)
            if re.match(r'^\d+\s*(bce|ce)$', el):
                return 'history'
            history_set = {'silkroad', 'frenchrevolution', 'immanuelkant'}
            if el in history_set:
                return 'history'
            tech_set = {'hak_gal', 'machinelearning', 'hexagonal', 'flask', 'react', 'sqlite', 'knowledgebase'}
            if el in tech_set:
                return 'technology'
            return 'default'

        def bridge_allowed(a: str, b: str) -> bool:
            ca, cb = classify_entity(a), classify_entity(b)
            allowed = {
                ('system_internal', 'system_internal'),
                ('system_internal', 'technology'),
                ('technology', 'technology'),
                ('history', 'history')
            }
            return (ca, cb) in allowed or (cb, ca) in allowed
        
        # 3.1 Tech-Hub-Priorisierung für Bridges
        tech_hubs = [
            'HAK_GAL', 'MachineLearning', 'KnowledgeBase', 'Hexagonal',
            'SQLite', 'Flask', 'React'
        ]
        for under in underrepresented[:8]:
            if classify_entity(under) != 'technology':
                continue
            for hub in tech_hubs:
                if hub in well_connected_names and bridge_allowed(under, hub):
                    if (under, hub) in self.exhausted_topics:
                        continue
                    topics.append({
                        'name': f"Bridge_{under}_{hub}",
                        'type': 'bridge',
                        'priority': 11,  # höher priorisieren
                        'source': under,
                        'target': hub,
                        'rationale': f"Tech-bridge: connect {under} with hub {hub}"
                    })

        # 4. Generiere Bridge-Topics (höchste Priorität)
        for under in underrepresented[:5]:
            for well in well_connected_names[:5]:
                if (under, well) in self.exhausted_topics:
                    continue
                if not bridge_allowed(under, well):
                    continue
                topics.append({
                    'name': f"Bridge_{under}_{well}",
                    'type': 'bridge',
                    'priority': 10,
                    'source': under,
                    'target': well,
                    'rationale': f"Connect underrepresented {under} (count: {stats.get(under, 0)}) with hub {well}"
                })
        
        # 5. Generiere Expansion-Topics (mittlere Priorität)
        isolated = self.gap_analyzer.find_isolated_entities()
        isolated = [i for i in isolated if not is_noise_entity(i)]
        # Priorisierung: nur sinnvolle Domains und lange genug
        def good_expansion_candidate(e: str) -> bool:
            if len(e) < 3:
                return False
            c = classify_entity(e)
            return c in ('technology', 'default')

        isolated = [e for e in isolated if good_expansion_candidate(e)]
        for entity in isolated[:10]:
            topic_name = f"Expand_{entity}"
            if topic_name in self.exhausted_topics:
                continue
            # Expansion nicht auf system_internal oder Junk
            if classify_entity(entity) == 'system_internal':
                continue
            topics.append({
                'name': topic_name,
                'type': 'expansion',
                'priority': 7,
                'entity': entity,
                'rationale': f"Expand isolated entity {entity}"
            })
        
        # 6. Generiere Domain-Topics für leere Bereiche
        empty_domains = self._find_empty_domains(stats)
        for domain in empty_domains[:3]:
            topics.append({
                'name': f"InitializeDomain_{domain}",
                'type': 'new_domain',
                'priority': 5,
                'domain': domain,
                'rationale': f"Initialize empty domain {domain}"
            })
        
        # Sortiere nach Priorität
        topics.sort(key=lambda x: x['priority'], reverse=True)
        
        return topics[:10]
    
    def _find_empty_domains(self, stats: Dict[str, int]) -> List[str]:
        """Finde Domains die noch nicht in der KB sind"""
        potential_domains = [
            "QuantumComputing", "Nanotechnology", "Genetics", "Neuroscience",
            "Cryptography", "Robotics", "ClimateScience", "Astronomy",
            "MaterialScience", "GameTheory", "InformationTheory", "Topology"
        ]
        
        empty = []
        for domain in potential_domains:
            # Check if domain or related terms exist
            domain_lower = domain.lower()
            related_count = sum(
                count for entity, count in stats.items()
                if domain_lower in entity.lower()
            )
            if related_count < 5:
                empty.append(domain)
        
        return empty
    
    def _fallback_topics(self) -> List[Dict]:
        """Fallback wenn keine Stats verfügbar"""
        return [
            {'name': 'Mathematics', 'type': 'fallback', 'priority': 5},
            {'name': 'Science', 'type': 'fallback', 'priority': 5},
            {'name': 'Technology', 'type': 'fallback', 'priority': 5}
        ]
    
    def mark_exhausted(self, topic_name: str):
        """Markiere Topic als erschöpft"""
        self.exhausted_topics.add(topic_name)

# --- SMART FACT GENERATOR ---
class SmartFactGenerator:
    """Generiert intelligente, nicht-redundante Fakten"""
    
    def __init__(self, cache: IntelligentCache):
        self.cache = cache
        self.generated_patterns = set()
        
    def generate_bridge_facts(self, source: str, target: str, count: int = 5) -> List[str]:
        """Generiere Brücken-Fakten zwischen zwei Entities ohne Platzhalter, KB- & LLM-gestützt.
        - Nur 2-stellige, whitelisted Prädikate
        - Kandidaten durch KB-Kontext & LLM-Hinweise
        """
        def fetch_statements(entity: str) -> List[str]:
            try:
                r = requests.post(
                    f"{API_BASE_URL}/search",
                    headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
                    json={"query": entity, "limit": 25},
                    timeout=20
                )
                if r.status_code == 200:
                    res = r.json().get("results", [])
                    return [x.get("statement", "") for x in res if isinstance(x, dict) and x.get("statement")]
            except Exception:
                return []
            return []

        def predicates_from_kb(stmts: List[str]) -> List[str]:
            preds: Dict[str, int] = {}
            for s in stmts:
                m = re.match(r'^([A-Za-z0-9_]+)\(', s)
                if not m:
                    continue
                p = m.group(1)
                preds[p] = preds.get(p, 0) + 1
            # sort by count desc
            return [p for p, _ in sorted(preds.items(), key=lambda kv: kv[1], reverse=True)]

        def llm_suggested_predicates(src: str, dst: str) -> List[str]:
            try:
                r = requests.post(
                    f"{API_BASE_URL}/llm/get-explanation",
                    headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
                    json={"topic": f"List concise relation predicates between {src} and {dst} using 1-3 word predicates like PartOf, UsedFor, Requires"},
                    timeout=20
                )
                if r.status_code != 200:
                    return []
                txt = (r.json().get("explanation") or "").lower()
                candidates = []
                for p in PREDICATE_WHITELIST:
                    if p.lower() in txt:
                        candidates.append(p)
                return candidates
            except Exception:
                return []

        # 1) KB-Kontext sammeln
        src_stmts = fetch_statements(source)
        dst_stmts = fetch_statements(target)
        kb_preds = predicates_from_kb(src_stmts + dst_stmts)

        # 2) LLM-Hinweise
        llm_preds = llm_suggested_predicates(source, target)

        # 3) Prädikate priorisieren: Schnittmenge aus KB und LLM, sonst KB, sonst LLM, sonst Fallback
        whitelist = list(PREDICATE_WHITELIST)
        pri = [p for p in kb_preds if p in llm_preds and p in whitelist]
        if not pri:
            pri = [p for p in kb_preds if p in whitelist]
        if not pri:
            pri = [p for p in llm_preds if p in whitelist]
        if not pri:
            pri = [p for p in ("Supports", "Provides", "Uses", "Requires") if p in whitelist]

        # 4) Kandidatenfakten bauen (nur 2-stellig, keine Platzhalter)
        candidates: List[str] = []
        for p in pri:
            candidates.append(f"{p}({source}, {target}).")
            # Einige Prädikate sinnvoll auch reversed versuchen
            if p in ("Supports", "Provides", "InfluencedBy"):
                candidates.append(f"{p}({target}, {source}).")
            if len(candidates) >= max(2*count, count+3):
                break

        # 5) Duplikate im Cache vermeiden und harte Begrenzung
        out: List[str] = []
        for f in candidates:
            if not self.cache.is_duplicate(f):
                out.append(f)
            if len(out) >= count:
                break
        return out
    
    def generate_expansion_facts(self, entity: str, count: int = 5) -> List[str]:
        """Erweitere eine einzelne Entity mit 2-stelligen, KB-gestützten Fakten (ohne Platzhalter).
        Zusätzlich werden LLM-extrahierte Fakten zum Entity-Thema berücksichtigt (Bulk-Ingest).
        """
        def fetch_statements(entity: str) -> List[str]:
            try:
                r = requests.post(
                    f"{API_BASE_URL}/search",
                    headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
                    json={"query": entity, "limit": 50},
                    timeout=20
                )
                if r.status_code == 200:
                    res = r.json().get("results", [])
                    return [x.get("statement", "") for x in res if isinstance(x, dict) and x.get("statement")]
            except Exception:
                return []
            return []

        def extract_neighbors(stmts: List[str], center: str) -> List[str]:
            neighbors: Dict[str, int] = {}
            c_norm = center.strip()
            for s in stmts:
                m = re.match(r'^([A-Za-z0-9_]+)\(([^)]+)\)\.$', s)
                if not m:
                    continue
                args = [a.strip() for a in m.group(2).split(',')]
                # nur 2-stellige Sätze berücksichtigen
                if len(args) != 2:
                    continue
                a1, a2 = args[0], args[1]
                if a1 == c_norm and a2 != c_norm:
                    neighbors[a2] = neighbors.get(a2, 0) + 1
                elif a2 == c_norm and a1 != c_norm:
                    neighbors[a1] = neighbors.get(a1, 0) + 1
            # sort by frequency desc
            return [n for n, _ in sorted(neighbors.items(), key=lambda kv: kv[1], reverse=True)]

        stmts = fetch_statements(entity)
        neigh = extract_neighbors(stmts, entity)

        # Priorisierte Prädikate für Expansion
        candidate_preds = [p for p in ("PartOf", "Uses", "UsedFor", "UsedIn", "Requires", "Supports", "Provides") if p in PREDICATE_WHITELIST]

        candidates: List[str] = []
        for nb in neigh[:10]:
            for p in candidate_preds:
                if nb == entity:
                    continue
                candidates.append(f"{p}({entity}, {nb}).")
                if p in ("Supports", "Provides"):
                    candidates.append(f"{p}({nb}, {entity}).")
            if len(candidates) >= 3 * count:
                break

        # LLM-Bulk-Kandidaten für das Entity hinzufügen
        try:
            r = requests.post(
                f"{API_BASE_URL}/llm/get-explanation",
                headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
                json={"topic": entity},
                timeout=15
            )
            if r.status_code == 200:
                data = r.json()
                facts_suggested = []
                for key in ("facts", "suggested_facts"):
                    v = data.get(key)
                    if isinstance(v, list):
                        facts_suggested.extend([str(x) for x in v])
                for f in facts_suggested[:30]:
                    fs = f.strip()
                    if not fs.endswith('.'):
                        fs += '.'
                    # Nur 2-stellig, Whitelist-Prädikat
                    m = re.match(r'^([A-Za-z0-9_]+)\(([^,)]+),\s*([^)]+)\)\.$', fs)
                    if not m:
                        continue
                    pred = m.group(1)
                    if pred not in PREDICATE_WHITELIST:
                        continue
                    candidates.append(fs)
        except Exception:
            pass

        # Duplikate vermeiden
        unique = []
        seen = set()
        for f in candidates:
            if f in seen:
                continue
            seen.add(f)
            if not self.cache.is_duplicate(f):
                unique.append(f)
            if len(unique) >= max(count, 5):
                break
        return unique[:count]
    
    def generate_domain_facts(self, domain: str, count: int = 10) -> List[str]:
        """Generiere Domain-spezifische Fakten"""
        facts = []
        
        domain_templates = {
            "QuantumComputing": [
                "Uses(QuantumComputing, Qubits).",
                "Enables(QuantumComputing, Superposition).",
                "Implements(QuantumComputing, QuantumGates).",
                "Algorithm(Shor, QuantumComputing, Factorization).",
                "Algorithm(Grover, QuantumComputing, Search).",
                "Requires(QuantumComputing, ErrorCorrection).",
                "Challenge(QuantumComputing, Decoherence).",
                "Application(QuantumComputing, Cryptography)."
            ],
            "Nanotechnology": [
                "Scale(Nanotechnology, Nanometer).",
                "Uses(Nanotechnology, CarbonNanotubes).",
                "Application(Nanotechnology, Medicine).",
                "Enables(Nanotechnology, Miniaturization).",
                "Creates(Nanotechnology, Nanomaterials).",
                "Requires(Nanotechnology, PrecisionControl)."
            ],
            "Cryptography": [
                "Uses(Cryptography, Encryption).",
                "Algorithm(RSA, Cryptography, PublicKey).",
                "Algorithm(AES, Cryptography, Symmetric).",
                "Provides(Cryptography, Security).",
                "Protects(Cryptography, Information).",
                "Challenge(Cryptography, QuantumThreat)."
            ]
        }
        
        if domain in domain_templates:
            for fact in domain_templates[domain][:count]:
                if not self.cache.is_duplicate(fact):
                    facts.append(fact)
        else:
            # Generic domain facts
            facts = [
                f"IsA({domain}, Field).",
                f"StudiedIn({domain}, Research).",
                f"HasApplications({domain}, Industry).",
                f"Evolves({domain}, Continuously).",
                f"Requires({domain}, Expertise)."
            ]
            facts = [f for f in facts if not self.cache.is_duplicate(f)]
        
        return facts

# --- MAIN INTELLIGENT ENGINE ---
class IntelligentGrowthEngine:
    """Hauptengine mit intelligenter Gap-Detection und Duplikat-Vermeidung"""
    
    def __init__(self):
        self.api_base = API_BASE_URL
        self.cache = IntelligentCache(CACHE_FILE)
        self.gap_analyzer = KnowledgeGapAnalyzer(DB_PATH, API_BASE_URL)
        self.topic_generator = IntelligentTopicGenerator(self.gap_analyzer)
        self.fact_generator = SmartFactGenerator(self.cache)
        self.qgate = QualityGate(self.api_base, API_KEY)
        
        self.session_stats = {
            'facts_added': 0,
            'duplicates_avoided': 0,
            'topics_explored': [],
            'gaps_filled': 0,
            'bridges_created': 0,
            'start_time': time.time()
        }
        
    def call_api(self, endpoint: str, method: str = 'POST', data: dict = None) -> dict:
        """API Call mit Error Handling"""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }
        
        try:
            if method == 'GET':
                response = requests.get(
                    f"{self.api_base}{endpoint}",
                    headers=headers,
                    timeout=30
                )
            else:
                response = requests.post(
                    f"{self.api_base}{endpoint}",
                    headers=headers,
                    json=data,
                    timeout=30
                )
            
            if response.status_code < 400:
                return response.json()
            else:
                return {"error": response.text, "status": response.status_code}
                
        except Exception as e:
            return {"error": str(e)}
    
    def smart_add_fact(self, fact: str) -> bool:
        """Intelligentes Hinzufügen mit Duplikat-Check"""
        
        # 1. Check Cache first
        if self.cache.is_duplicate(fact):
            self.session_stats['duplicates_avoided'] += 1
            print(f"  ⏭️ Skipped (cached): {fact[:40]}...")
            return False
        
        # 2. Try to add
        result = self.call_api("/facts", data={"statement": fact})
        
        # 3. Handle response
        if result.get('success'):
            self.session_stats['facts_added'] += 1
            print(f"  ✅ Added: {fact[:60]}...")
            return True
        elif 'exists' in str(result.get('message', '')).lower():
            # Mark as existing
            self.cache.add_existing(fact)
            self.session_stats['duplicates_avoided'] += 1
            print(f"  ⏭️ Already exists: {fact[:40]}...")
            return False
        else:
            # Mark as failed
            self.cache.add_failed(fact)
            print(f"  ❌ Failed: {fact[:40]}... - {result.get('error', 'Unknown')}")
            return False
    
    def explore_topic(self, topic: Dict) -> int:
        """Exploriere ein Topic intelligent"""
        print(f"\n🎯 Topic: {topic['name']}")
        print(f"   Type: {topic['type']}")
        print(f"   Priority: {topic['priority']}")
        print(f"   Rationale: {topic.get('rationale', 'N/A')}")
        
        facts_added = 0
        
        if topic['type'] == 'bridge':
            # Generiere Bridge-Fakten
            raw_facts = self.fact_generator.generate_bridge_facts(
                topic['source'], topic['target'], count=8
            )
            facts = [f for f in raw_facts if self.qgate.passes(f)]
            for fact in facts:
                if self.smart_add_fact(fact):
                    facts_added += 1
            if facts_added > 0:
                self.session_stats['bridges_created'] += 1
                
        elif topic['type'] == 'expansion':
            # Erweitere isolierte Entity
            raw_facts = self.fact_generator.generate_expansion_facts(
                topic['entity'], count=8
            )
            facts = [f for f in raw_facts if self.qgate.passes(f)]
            for fact in facts:
                if self.smart_add_fact(fact):
                    facts_added += 1
                    
        elif topic['type'] == 'new_domain':
            # Initialisiere neue Domain
            raw_facts = self.fact_generator.generate_domain_facts(
                topic['domain'], count=12
            )
            facts = [f for f in raw_facts if self.qgate.passes(f)]
            for fact in facts:
                if self.smart_add_fact(fact):
                    facts_added += 1
            if facts_added > 0:
                self.session_stats['gaps_filled'] += 1
        
        # Mark topic as explored
        self.session_stats['topics_explored'].append(topic['name'])
        
        if facts_added == 0:
            self.topic_generator.mark_exhausted(topic['name'])
            print(f"   ⚠️ Topic exhausted")
        
        return facts_added
    
    def run_intelligent_growth(self, cycles: int = 20):
        """Hauptloop mit intelligenter Steuerung"""
        print("=" * 80)
        print("HAK-GAL INTELLIGENT GROWTH ENGINE v2.0")
        print("=" * 80)
        print("Features:")
        print("  ✓ Real-time gap detection")
        print("  ✓ Duplicate prevention cache")
        print("  ✓ Priority-based topic selection")
        print("  ✓ Adaptive learning system")
        print("=" * 80)
        
        # Initial analysis
        print("\n📊 Initial Knowledge Base Analysis...")
        stats = self.gap_analyzer.get_entity_statistics()
        
        if stats:
            total_entities = len(stats)
            # Ensure we have numeric values
            numeric_values = []
            for v in stats.values():
                if isinstance(v, (int, float)):
                    numeric_values.append(v)
                elif isinstance(v, list):
                    numeric_values.append(len(v))
            avg_connections = sum(numeric_values) / len(numeric_values) if numeric_values else 0
            
            print(f"  Entities: {total_entities}")
            print(f"  Avg connections: {avg_connections:.1f}")
            
            # Find gaps
            underrepresented = self.gap_analyzer.find_underrepresented_entities(stats)
            isolated = self.gap_analyzer.find_isolated_entities()
            
            print(f"  Underrepresented: {len(underrepresented)}")
            print(f"  Isolated: {len(isolated)}")
        
        # Main growth loop
        consecutive_failures = 0
        
        for cycle in range(1, cycles + 1):
            print(f"\n{'='*60}")
            print(f"CYCLE {cycle}/{cycles}")
            print(f"  Cache: {len(self.cache.failed_attempts)} failed, {len(self.cache.existing_facts)} known")
            print(f"  Stats: +{self.session_stats['facts_added']} facts, -{self.session_stats['duplicates_avoided']} duplicates")
            print(f"{'='*60}")
            
            # Generate priority topics häufiger und bis zu 2 Topics pro Zyklus
            if cycle % 2 == 1 or consecutive_failures >= 2 or 'topics' not in locals() or not topics:
                print("\n🔄 Regenerating priority topics...")
                topics = self.topic_generator.generate_priority_topics()
                consecutive_failures = 0
            
            if not topics:
                print("⚠️ No topics available, generating fallback...")
                topics = self.topic_generator._fallback_topics()
            
            # Select up to two highest priority topics
            selected = []
            if topics:
                selected.append(topics.pop(0))
            if topics:
                selected.append(topics.pop(0))

            if not selected:
                print("❌ No topics to explore")
                break
            
            # Explore selected topics
            facts_added = 0
            for topic in selected:
                facts_added += self.explore_topic(topic)
            
            print(f"\n📈 Cycle result: +{facts_added} facts")
            
            if facts_added == 0:
                consecutive_failures += 1
            else:
                consecutive_failures = 0
            
            # Early stop if too many failures
            if consecutive_failures >= 5:
                print("\n⚠️ Too many consecutive failures, stopping early")
                break
            
            # Save cache periodically
            if cycle % 5 == 0:
                self.cache.save_cache()
                print("💾 Cache saved")
            
            time.sleep(0.5)  # Rate limiting
        
        # Final report
        elapsed = time.time() - self.session_stats['start_time']
        
        print("\n" + "=" * 80)
        print("INTELLIGENT GROWTH COMPLETE - FINAL REPORT")
        print("=" * 80)
        print(f"  Duration: {elapsed:.1f} seconds")
        print(f"  Facts added: {self.session_stats['facts_added']}")
        print(f"  Duplicates avoided: {self.session_stats['duplicates_avoided']}")
        print(f"  Topics explored: {len(self.session_stats['topics_explored'])}")
        print(f"  Bridges created: {self.session_stats['bridges_created']}")
        print(f"  Gaps filled: {self.session_stats['gaps_filled']}")
        print(f"  Efficiency: {(100 - (self.session_stats['duplicates_avoided'] / max(1, self.session_stats['facts_added'] + self.session_stats['duplicates_avoided']) * 100)):.1f}%")
        print("=" * 80)
        
        # Save final cache
        self.cache.save_cache()
        print("\n💾 Final cache saved")
        
        # Show top unexplored topics
        remaining_topics = self.topic_generator.generate_priority_topics()[:3]
        if remaining_topics:
            print("\n🎯 Recommended next topics:")
            for topic in remaining_topics:
                print(f"  - {topic['name']} (priority: {topic['priority']})")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='HAK-GAL Intelligent Growth Engine')
    parser.add_argument('--cycles', type=int, default=20, help='Number of growth cycles')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze KB')
    parser.add_argument('--clear-cache', action='store_true', help='Clear failed attempts cache')
    
    args = parser.parse_args()
    
    if args.clear_cache:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
            print("✅ Cache cleared")
    
    engine = IntelligentGrowthEngine()
    
    if args.analyze_only:
        stats = engine.gap_analyzer.get_entity_statistics()
        if stats:
            print(f"\n📊 Knowledge Base Analysis:")
            print(f"  Total entities: {len(stats)}")
            
            # Top entities
            top = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]
            print(f"\n  Top entities:")
            for entity, count in top:
                print(f"    {entity}: {count}")
            
            # Underrepresented
            under = engine.gap_analyzer.find_underrepresented_entities(stats)
            print(f"\n  Underrepresented entities: {len(under)}")
            if under:
                print(f"    Examples: {', '.join(under[:5])}")
            
            # Isolated
            isolated = engine.gap_analyzer.find_isolated_entities()
            print(f"\n  Isolated entities: {len(isolated)}")
            if isolated:
                print(f"    Examples: {', '.join(isolated[:5])}")
    else:
        engine.run_intelligent_growth(cycles=args.cycles)

if __name__ == "__main__":
    main()
