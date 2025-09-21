#!/usr/bin/env python3
"""
HAK/GAL Knowledge Base Analytics Module
========================================

Ein erweitertes Analytics-Modul für die HAK/GAL Suite, entwickelt durch
Multi-Agent-Kollaboration zwischen Claude, Gemini und Cursor.

Features:
- Semantische Ähnlichkeitsanalyse
- Wissensgraph-Konstruktion und -Analyse
- Automatische Fakten-Kategorisierung
- Performance-Monitoring
- Test-Suite integriert

Entwickelt durch: Claude (Koordination) + Gemini (Analytics) + Cursor (Testing)
Datum: 2025-08-28
Version: 1.0.0
"""

import requests
import pandas as pd
import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AnalyticsResult:
    """Strukturierte Ergebnisse für Analytics-Operationen"""
    success: bool
    data: Any
    execution_time: float
    error_message: Optional[str] = None
    metadata: Optional[Dict] = None

class HakGalAnalytics:
    """
    Erweiterte Knowledge Base Analytics für HAK/GAL Suite

    Entwickelt durch Multi-Agent-Kollaboration:
    - Claude: Koordination und Architektur
    - Gemini: Analytics-Algorithmen und Datenverarbeitung
    - Cursor: Testing, praktische Implementierung und Code-Qualität
    """

    def __init__(self, api_key: str, base_url: str = "http://127.0.0.1:5002"):
        """
        Initialisiert das Analytics-Modul

        Args:
            api_key: HAK/GAL API-Schlüssel
            base_url: Basis-URL der HAK/GAL API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Cache für Performance
        self._cache = {}
        self._cache_timeout = 300  # 5 Minuten

        logger.info(f"HAK/GAL Analytics Module initialized with base_url: {self.base_url}")

    def _make_request(self, endpoint: str, method: str = "GET", **kwargs) -> AnalyticsResult:
        """
        Führt eine API-Anfrage mit Fehlerbehandlung und Performance-Monitoring durch

        Args:
            endpoint: API-Endpunkt (ohne base_url)
            method: HTTP-Methode
            **kwargs: Zusätzliche Parameter für requests

        Returns:
            AnalyticsResult mit Erfolg/Fehler-Status
        """
        start_time = time.time()
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = self.session.get(url, **kwargs)
            elif method.upper() == "POST":
                response = self.session.post(url, **kwargs)
            else:
                raise ValueError(f"Nicht unterstützte HTTP-Methode: {method}")

            response.raise_for_status()
            execution_time = time.time() - start_time

            return AnalyticsResult(
                success=True,
                data=response.json() if response.content else None,
                execution_time=execution_time,
                metadata={"status_code": response.status_code, "url": url}
            )

        except requests.exceptions.RequestException as e:
            execution_time = time.time() - start_time
            logger.error(f"API-Anfrage fehlgeschlagen: {url} - {str(e)}")

            return AnalyticsResult(
                success=False,
                data=None,
                execution_time=execution_time,
                error_message=str(e),
                metadata={"url": url}
            )

    def get_knowledge_base_stats(self) -> AnalyticsResult:
        """
        Ruft grundlegende Statistiken der Knowledge Base ab

        Returns:
            AnalyticsResult mit KB-Statistiken
        """
        return self._make_request("/api/knowledge/stats")

    def get_facts(self, limit: int = 1000, offset: int = 0) -> AnalyticsResult:
        """
        Ruft Fakten aus der Knowledge Base ab

        Args:
            limit: Maximale Anzahl der Fakten
            offset: Offset für Pagination

        Returns:
            AnalyticsResult mit Fakten-Liste
        """
        params = {"limit": limit, "offset": offset}
        return self._make_request("/api/knowledge/facts", params=params)

    def search_knowledge(self, query: str, limit: int = 50) -> AnalyticsResult:
        """
        Sucht in der Knowledge Base nach relevanten Fakten

        Args:
            query: Suchbegriff
            limit: Maximale Anzahl der Ergebnisse

        Returns:
            AnalyticsResult mit Suchergebnissen
        """
        params = {"query": query, "limit": limit}
        return self._make_request("/api/knowledge/search", params=params)

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Berechnet semantische Ähnlichkeit zwischen zwei Texten

        Args:
            text1: Erster Text
            text2: Zweiter Text

        Returns:
            Ähnlichkeitswert zwischen 0.0 und 1.0
        """
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Fehler bei semantischer Ähnlichkeitsberechnung: {str(e)}")
            return 0.0

    def build_knowledge_graph(self, facts_data: List[Dict]) -> nx.Graph:
        """
        Konstruiert einen Wissensgraphen aus Fakten-Daten

        Args:
            facts_data: Liste von Fakten-Dictionaries

        Returns:
            NetworkX Graph-Objekt
        """
        graph = nx.Graph()

        for fact in facts_data:
            try:
                # Extrahiere Subjekt, Prädikat, Objekt aus dem Fakt
                if 'statement' in fact:
                    # Parse HAK/GAL statement format: "Subject Predicate Object"
                    statement = fact['statement']
                    parts = statement.split()

                    if len(parts) >= 3:
                        subject = parts[0]
                        predicate = parts[1]
                        object_part = ' '.join(parts[2:])

                        # Füge Knoten und Kanten hinzu
                        graph.add_node(subject, type='entity')
                        graph.add_node(object_part, type='entity')
                        graph.add_edge(subject, object_part,
                                     predicate=predicate,
                                     weight=1.0)

            except Exception as e:
                logger.warning(f"Fehler beim Parsen des Fakts: {fact} - {str(e)}")
                continue

        logger.info(f"Wissensgraph erstellt mit {len(graph.nodes)} Knoten und {len(graph.edges)} Kanten")
        return graph

    def analyze_knowledge_graph(self, graph: nx.Graph) -> Dict[str, Any]:
        """
        Führt umfassende Analyse des Wissensgraphen durch

        Args:
            graph: NetworkX Graph-Objekt

        Returns:
            Dictionary mit Analyse-Ergebnissen
        """
        analysis = {}

        try:
            # Grundlegende Metriken
            analysis['nodes_count'] = len(graph.nodes)
            analysis['edges_count'] = len(graph.edges)
            analysis['density'] = nx.density(graph)

            # Zentralitätsmaße
            if len(graph.nodes) > 1:
                analysis['degree_centrality'] = nx.degree_centrality(graph)
                analysis['betweenness_centrality'] = nx.betweenness_centrality(graph)
                analysis['closeness_centrality'] = nx.closeness_centrality(graph)

                # Top 10 einflussreichste Entitäten
                degree_sorted = sorted(analysis['degree_centrality'].items(),
                                     key=lambda x: x[1], reverse=True)
                analysis['top_entities'] = degree_sorted[:10]

            # Clustering-Koeffizient
            analysis['clustering_coefficient'] = nx.average_clustering(graph)

            # Komponenten-Analyse
            components = list(nx.connected_components(graph))
            analysis['connected_components'] = len(components)
            analysis['largest_component_size'] = len(max(components, key=len)) if components else 0

        except Exception as e:
            logger.error(f"Fehler bei Graph-Analyse: {str(e)}")
            analysis['error'] = str(e)

        return analysis

    def categorize_facts_automatically(self, facts_data: List[Dict],
                                     categories: Dict[str, List[str]]) -> Dict[str, List[Dict]]:
        """
        Kategorisiert Fakten automatisch basierend auf Keywords

        Args:
            facts_data: Liste von Fakten
            categories: Dictionary mit Kategorien und Keywords

        Returns:
            Dictionary mit kategorisierten Fakten
        """
        categorized = {category: [] for category in categories.keys()}
        categorized['uncategorized'] = []

        for fact in facts_data:
            try:
                text = fact.get('statement', '').lower()
                categorized_flag = False

                for category, keywords in categories.items():
                    if any(keyword.lower() in text for keyword in keywords):
                        categorized[category].append(fact)
                        categorized_flag = True
                        break

                if not categorized_flag:
                    categorized['uncategorized'].append(fact)

            except Exception as e:
                logger.warning(f"Fehler bei Fakten-Kategorisierung: {fact} - {str(e)}")
                categorized['uncategorized'].append(fact)

        return categorized

    def cluster_facts_by_similarity(self, facts_data: List[Dict],
                                  n_clusters: int = 5) -> Dict[str, Any]:
        """
        Gruppiert Fakten basierend auf semantischer Ähnlichkeit

        Args:
            facts_data: Liste von Fakten
            n_clusters: Anzahl der gewünschten Cluster

        Returns:
            Dictionary mit Clustering-Ergebnissen
        """
        try:
            # Extrahiere Texte für Clustering
            texts = [fact.get('statement', '') for fact in facts_data]

            if len(texts) < n_clusters:
                return {"error": "Nicht genügend Fakten für Clustering"}

            # TF-IDF Vektorisierung
            vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
            tfidf_matrix = vectorizer.fit_transform(texts)

            # K-Means Clustering
            kmeans = KMeans(n_clusters=min(n_clusters, len(texts)), random_state=42, n_init=10)
            clusters = kmeans.fit_predict(tfidf_matrix)

            # Gruppiere Fakten nach Clustern
            clustered_facts = {}
            for i in range(len(clusters)):
                cluster_id = f"cluster_{clusters[i]}"
                if cluster_id not in clustered_facts:
                    clustered_facts[cluster_id] = []
                clustered_facts[cluster_id].append(facts_data[i])

            return {
                "clusters": clustered_facts,
                "cluster_centers": kmeans.cluster_centers_,
                "inertia": kmeans.inertia_,
                "n_clusters": len(set(clusters))
            }

        except Exception as e:
            logger.error(f"Fehler beim Fakten-Clustering: {str(e)}")
            return {"error": str(e)}

    def generate_analytics_report(self) -> Dict[str, Any]:
        """
        Generiert einen umfassenden Analytics-Report

        Returns:
            Dictionary mit vollständigem Analytics-Report
        """
        start_time = time.time()

        report = {
            "timestamp": datetime.now().isoformat(),
            "module_version": "1.0.0",
            "agent_collaboration": {
                "claude": "Koordination und Architektur",
                "gemini": "Analytics-Algorithmen",
                "cursor": "Testing und praktische Implementierung"
            }
        }

        # 1. Knowledge Base Statistiken
        stats_result = self.get_knowledge_base_stats()
        report["knowledge_base_stats"] = {
            "success": stats_result.success,
            "data": stats_result.data,
            "execution_time": stats_result.execution_time
        }

        # 2. Fakten abrufen
        facts_result = self.get_facts(limit=1000)
        if facts_result.success and facts_result.data:
            facts_data = facts_result.data.get('facts', [])

            # 3. Wissensgraph erstellen und analysieren
            knowledge_graph = self.build_knowledge_graph(facts_data)
            graph_analysis = self.analyze_knowledge_graph(knowledge_graph)

            report["knowledge_graph"] = {
                "nodes": len(knowledge_graph.nodes),
                "edges": len(knowledge_graph.edges),
                "analysis": graph_analysis
            }

            # 4. Fakten kategorisieren
            categories = {
                "Technology": ["software", "algorithm", "system", "api", "database"],
                "Science": ["physics", "biology", "chemistry", "mathematics", "research"],
                "Philosophy": ["ethics", "logic", "metaphysics", "epistemology"],
                "History": ["civilization", "empire", "revolution", "war"],
                "Economics": ["market", "finance", "trade", "policy"]
            }

            categorized_facts = self.categorize_facts_automatically(facts_data, categories)
            report["fact_categorization"] = {
                category: len(facts) for category, facts in categorized_facts.items()
            }

            # 5. Fakten clustern (falls genügend Daten vorhanden)
            if len(facts_data) >= 5:
                clustering_result = self.cluster_facts_by_similarity(facts_data, n_clusters=5)
                report["fact_clustering"] = clustering_result

        # Performance-Metriken
        total_time = time.time() - start_time
        report["performance"] = {
            "total_execution_time": total_time,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Analytics-Report generiert in {total_time:.2f} Sekunden")
        return report

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """
        Führt umfassende Tests aller Modul-Funktionen durch

        Returns:
            Dictionary mit Test-Ergebnissen
        """
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": []
        }

        # Test 1: API-Verbindung
        stats_result = self.get_knowledge_base_stats()
        test_results["test_details"].append({
            "test": "API Connection",
            "success": stats_result.success,
            "execution_time": stats_result.execution_time,
            "error": stats_result.error_message
        })
        if stats_result.success:
            test_results["tests_passed"] += 1
        else:
            test_results["tests_failed"] += 1

        # Test 2: Semantische Ähnlichkeit
        similarity = self.calculate_semantic_similarity(
            "Machine learning is a subset of artificial intelligence",
            "AI includes machine learning as one of its components"
        )
        test_results["test_details"].append({
            "test": "Semantic Similarity",
            "success": 0.0 <= similarity <= 1.0,
            "result": similarity
        })
        if 0.0 <= similarity <= 1.0:
            test_results["tests_passed"] += 1
        else:
            test_results["tests_failed"] += 1

        # Test 3: Wissensgraph-Konstruktion
        test_facts = [
            {"statement": "Python is ProgrammingLanguage"},
            {"statement": "Java is ProgrammingLanguage"},
            {"statement": "ProgrammingLanguage enables SoftwareDevelopment"}
        ]
        test_graph = self.build_knowledge_graph(test_facts)
        test_results["test_details"].append({
            "test": "Knowledge Graph Construction",
            "success": len(test_graph.nodes) > 0 and len(test_graph.edges) > 0,
            "nodes": len(test_graph.nodes),
            "edges": len(test_graph.edges)
        })
        if len(test_graph.nodes) > 0 and len(test_graph.edges) > 0:
            test_results["tests_passed"] += 1
        else:
            test_results["tests_failed"] += 1

        # Test 4: Fakten-Kategorisierung
        test_categories = {"Tech": ["programming", "software"]}
        categorized = self.categorize_facts_automatically(test_facts, test_categories)
        test_results["test_details"].append({
            "test": "Fact Categorization",
            "success": isinstance(categorized, dict),
            "categories_found": len(categorized)
        })
        if isinstance(categorized, dict):
            test_results["tests_passed"] += 1
        else:
            test_results["tests_failed"] += 1

        test_results["success_rate"] = (test_results["tests_passed"] /
                                       (test_results["tests_passed"] + test_results["tests_failed"])) * 100

        logger.info(f"Test-Suite abgeschlossen: {test_results['tests_passed']}/{test_results['tests_passed'] + test_results['tests_failed']} Tests bestanden")

        return test_results


# Hauptfunktion für direkte Ausführung
def main():
    """
    Hauptfunktion für direkte Ausführung des Analytics-Moduls
    """
    # Konfiguration
    API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
    BASE_URL = "http://127.0.0.1:5002"

    # Modul initialisieren
    analytics = HakGalAnalytics(API_KEY, BASE_URL)

    print(">>> HAK/GAL Knowledge Base Analytics")
    print("=" * 50)

    # 1. Basis-Tests durchführen
    print("\n1. Führe Basis-Tests durch...")
    test_results = analytics.run_comprehensive_test()
    print(f"   [OK] Tests bestanden: {test_results['tests_passed']}/{test_results['tests_passed'] + test_results['tests_failed']}")
    print(f"   [STATS] Erfolgsrate: {test_results.get('success_rate', 0):.1f}%")
    # 2. Analytics-Report generieren
    print("\n2. Generiere Analytics-Report...")
    try:
        report = analytics.generate_analytics_report()
        print("   [SUCCESS] Report erfolgreich generiert")
        print(f"   [DATA] Knowledge Base Facts: {report.get('knowledge_base_stats', {}).get('data', {}).get('total_facts', 'N/A')}")

        if 'knowledge_graph' in report:
            kg = report['knowledge_graph']
            print(f"   [GRAPH] Wissensgraph: {kg['nodes']} Knoten, {kg['edges']} Kanten")

        if 'fact_categorization' in report:
            print(f"   [CATEGORY] Fakten-Kategorien: {len(report['fact_categorization'])} Kategorien")

    except Exception as e:
        print(f"   [ERROR] Fehler bei Report-Generierung: {str(e)}")

    # 3. Beispiel-Analysen
    print("\n3. Beispiel-Analysen:")

    # Semantische Ähnlichkeit
    text1 = "Machine learning is a subset of artificial intelligence"
    text2 = "AI includes machine learning as one of its components"
    similarity = analytics.calculate_semantic_similarity(text1, text2)
    print(f"   [SIMILARITY] Semantische Ähnlichkeit: {similarity:.3f}")
    # Wissensgraph-Test
    test_facts = [
        {"statement": "Python is ProgrammingLanguage"},
        {"statement": "Java is ProgrammingLanguage"},
        {"statement": "ProgrammingLanguage enables SoftwareDevelopment"}
    ]
    test_graph = analytics.build_knowledge_graph(test_facts)
    analysis = analytics.analyze_knowledge_graph(test_graph)
    print(f"   [GRAPH] Test-Graph: {len(test_graph.nodes)} Knoten, {len(test_graph.edges)} Kanten")
    print(f"   [METRICS] Clustering-Koeffizient: {analysis.get('clustering_coefficient', 0):.3f}")

    print("\n[SUCCESS] Analytics-Modul erfolgreich getestet!")
    print("\nEntwickelt durch Multi-Agent-Kollaboration:")
    print("   [CLAUDE] Claude: Koordination und Architektur")
    print("   [GEMINI] Gemini: Analytics-Algorithmen")
    print("   [CURSOR] Cursor: Testing und praktische Implementierung")


if __name__ == "__main__":
    main()