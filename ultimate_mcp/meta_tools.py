#!/usr/bin/env python3
"""
HAK-GAL Meta-Tools Module
Wissenschaftliche Evaluations- und Orchestrierungsfunktionen
"""

import json
import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter
import difflib
from datetime import datetime
import hashlib

class ConsensusEvaluatorTool:
    """Evaluiert Konsens zwischen mehreren Tool/LLM-Outputs"""
    
    def __init__(self):
        self.history = []
        
    def evaluate_consensus(
        self,
        task_id: str,
        outputs: List[Dict[str, Any]],
        method: str = "semantic_similarity",
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Hauptfunktion für Konsens-Evaluierung
        
        Args:
            task_id: Eindeutige Task-ID
            outputs: Liste von Tool-Outputs [{tool_name, model, content, confidence}]
            method: "majority_vote" | "semantic_similarity" | "kappa"
            threshold: Konsens-Schwellwert
        """
        
        # Extrahiere Contents
        contents = [o.get("content", "") for o in outputs]
        
        # Berechne Konsens-Score basierend auf Methode
        if method == "majority_vote":
            consensus_score, consensus_result = self._majority_vote(contents)
        elif method == "semantic_similarity":
            consensus_score, consensus_result = self._semantic_similarity(contents)
        elif method == "kappa":
            consensus_score, consensus_result = self._cohen_kappa(contents)
        else:
            consensus_score, consensus_result = self._semantic_similarity(contents)
        
        # Finde Divergenzen
        divergences = self._find_divergences(outputs)
        
        # Berechne Tool-Ranking
        ranking = self._rank_tools(outputs, consensus_result)
        
        # Erstelle Synthese
        synthesis = self._create_synthesis(outputs, consensus_result, divergences)
        
        result = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "consensus_score": round(consensus_score, 3),
            "consensus_result": consensus_result,
            "synthesis": synthesis,
            "divergences": divergences,
            "ranking": ranking,
            "method": method,
            "threshold": threshold,
            "confidence": self._calculate_confidence(consensus_score, len(outputs))
        }
        
        # Speichere in History
        self.history.append(result)
        
        return result
    
    def _majority_vote(self, contents: List[str]) -> Tuple[float, str]:
        """Einfaches Majority Voting"""
        if not contents:
            return 0.0, ""
        
        # Normalisiere und zähle
        normalized = [self._normalize_content(c) for c in contents]
        counter = Counter(normalized)
        
        if not counter:
            return 0.0, contents[0]
        
        most_common = counter.most_common(1)[0]
        consensus_result = most_common[0]
        consensus_score = most_common[1] / len(contents)
        
        return consensus_score, consensus_result
    
    def _semantic_similarity(self, contents: List[str]) -> Tuple[float, str]:
        """Semantische Ähnlichkeit zwischen Outputs"""
        if not contents:
            return 0.0, ""
        
        # Similarity Matrix
        n = len(contents)
        similarity_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    ratio = difflib.SequenceMatcher(None, contents[i], contents[j]).ratio()
                    similarity_matrix[i][j] = ratio
                else:
                    similarity_matrix[i][j] = 1.0
        
        # Durchschnittliche Ähnlichkeit pro Output
        avg_similarities = similarity_matrix.mean(axis=1)
        
        # Output mit höchster durchschnittlicher Ähnlichkeit
        best_idx = np.argmax(avg_similarities)
        consensus_result = contents[best_idx]
        consensus_score = avg_similarities[best_idx]
        
        return consensus_score, consensus_result
    
    def _cohen_kappa(self, contents: List[str]) -> Tuple[float, str]:
        """Cohen's Kappa für Übereinstimmung"""
        # Vereinfachte Implementation
        # In Produktion: sklearn.metrics.cohen_kappa_score verwenden
        
        if len(contents) < 2:
            return 0.0, contents[0] if contents else ""
        
        # Extrahiere Keywords aus jedem Content
        keywords_lists = []
        for content in contents:
            words = set(w.lower() for w in content.split() if len(w) > 4)
            keywords_lists.append(words)
        
        # Berechne paarweise Übereinstimmung
        agreements = []
        for i in range(len(keywords_lists)):
            for j in range(i+1, len(keywords_lists)):
                intersection = len(keywords_lists[i] & keywords_lists[j])
                union = len(keywords_lists[i] | keywords_lists[j])
                if union > 0:
                    agreements.append(intersection / union)
        
        kappa = np.mean(agreements) if agreements else 0.0
        
        # Wähle Content mit meisten gemeinsamen Keywords
        consensus_result = contents[0]
        
        return kappa, consensus_result
    
    def _find_divergences(self, outputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifiziert Hauptdifferenzen zwischen Outputs"""
        divergences = []
        
        # Extrahiere Keywords pro Output
        all_keywords = []
        for output in outputs:
            content = output.get("content", "")
            keywords = set(w.lower() for w in content.split() if len(w) > 5)
            all_keywords.append({
                "tool": output.get("tool_name", "unknown"),
                "keywords": keywords
            })
        
        # Finde einzigartige Keywords pro Tool
        for i, tool_kw in enumerate(all_keywords):
            unique = tool_kw["keywords"].copy()
            for j, other_kw in enumerate(all_keywords):
                if i != j:
                    unique -= other_kw["keywords"]
            
            if unique:
                divergences.append({
                    "tool": tool_kw["tool"],
                    "unique_focus": list(unique)[:5],
                    "type": "content_divergence"
                })
        
        return divergences
    
    def _rank_tools(self, outputs: List[Dict[str, Any]], consensus: str) -> List[Dict[str, float]]:
        """Rankt Tools nach Alignment mit Konsens"""
        ranking = []
        
        for output in outputs:
            content = output.get("content", "")
            similarity = difflib.SequenceMatcher(None, content, consensus).ratio()
            
            ranking.append({
                "tool_name": output.get("tool_name", "unknown"),
                "model": output.get("model", ""),
                "alignment_score": round(similarity, 3)
            })
        
        # Sortiere nach Alignment
        ranking.sort(key=lambda x: x["alignment_score"], reverse=True)
        
        return ranking
    
    def _create_synthesis(
        self, 
        outputs: List[Dict[str, Any]], 
        consensus: str,
        divergences: List[Dict[str, Any]]
    ) -> str:
        """Erstellt eine konsolidierte Synthese"""
        
        # Extrahiere gemeinsame Themen
        all_words = []
        for output in outputs:
            words = output.get("content", "").lower().split()
            all_words.extend([w for w in words if len(w) > 4])
        
        word_freq = Counter(all_words)
        common_themes = [w for w, c in word_freq.most_common(10) 
                        if c >= len(outputs) * 0.6]
        
        synthesis = f"Konsens über {len(outputs)} Outputs: "
        synthesis += f"Hauptthemen: {', '.join(common_themes[:5])}. "
        
        if divergences:
            div_tools = [d["tool"] for d in divergences[:3]]
            synthesis += f"Divergenzen bei: {', '.join(div_tools)}."
        
        return synthesis
    
    def _normalize_content(self, content: str) -> str:
        """Normalisiert Content für Vergleiche"""
        # Lowercase, remove extra spaces, strip
        normalized = " ".join(content.lower().split())
        return normalized.strip()
    
    def _calculate_confidence(self, consensus_score: float, n_outputs: int) -> str:
        """Berechnet Confidence-Level"""
        if consensus_score >= 0.8 and n_outputs >= 3:
            return "HIGH"
        elif consensus_score >= 0.6:
            return "MEDIUM"
        else:
            return "LOW"


class ReliabilityCheckerTool:
    """Prüft Konsistenz von Tools über mehrere Ausführungen"""
    
    def __init__(self):
        self.reliability_scores = {}
    
    def check_reliability(
        self,
        tool_name: str,
        task_function: callable,
        task_params: Dict[str, Any],
        n_runs: int = 5
    ) -> Dict[str, Any]:
        """
        Führt Task mehrfach aus und misst Konsistenz
        
        Args:
            tool_name: Name des zu testenden Tools
            task_function: Funktion die den Task ausführt
            task_params: Parameter für den Task
            n_runs: Anzahl der Wiederholungen
        """
        
        outputs = []
        execution_times = []
        
        for i in range(n_runs):
            start_time = datetime.now()
            try:
                output = task_function(**task_params)
                outputs.append(output)
                execution_times.append((datetime.now() - start_time).total_seconds())
            except Exception as e:
                outputs.append(f"ERROR: {str(e)}")
                execution_times.append(-1)
        
        # Berechne Konsistenz-Metriken
        consistency_score = self._calculate_consistency(outputs)
        
        # Berechne Fleiss' Kappa (vereinfacht)
        kappa = self._calculate_fleiss_kappa(outputs)
        
        # Sichere Berechnung der durchschnittlichen Execution Time
        valid_times = [t for t in execution_times if t > 0]
        avg_time = round(np.mean(valid_times), 3) if valid_times else 0.0
        
        result = {
            "tool_name": tool_name,
            "n_runs": n_runs,
            "consistency_score": round(consistency_score, 3),
            "fleiss_kappa": round(kappa, 3),
            "avg_execution_time": avg_time,
            "stability": "STABLE" if consistency_score > 0.8 else "UNSTABLE" if consistency_score < 0.5 else "MODERATE",
            "errors": sum(1 for o in outputs if "ERROR" in str(o)),
            "timestamp": datetime.now().isoformat()
        }
        
        # Update reliability history
        if tool_name not in self.reliability_scores:
            self.reliability_scores[tool_name] = []
        self.reliability_scores[tool_name].append(result)
        
        return result
    
    def _calculate_consistency(self, outputs: List[Any]) -> float:
        """Berechnet Konsistenz-Score"""
        if len(outputs) < 2:
            return 1.0
        
        # String-Vergleiche
        str_outputs = [str(o) for o in outputs]
        
        similarities = []
        for i in range(len(str_outputs)):
            for j in range(i+1, len(str_outputs)):
                sim = difflib.SequenceMatcher(None, str_outputs[i], str_outputs[j]).ratio()
                similarities.append(sim)
        
        return np.mean(similarities) if similarities else 0.0
    
    def _calculate_fleiss_kappa(self, outputs: List[Any]) -> float:
        """Vereinfachte Fleiss' Kappa Berechnung"""
        # In Produktion: statsmodels.stats.inter_rater.fleiss_kappa verwenden
        
        # Extrahiere kategoriale Features
        categories = set()
        for output in outputs:
            # Vereinfacht: erste 3 Wörter als Kategorien
            words = str(output).split()[:3]
            categories.update(words)
        
        if len(categories) == 0:
            return 0.0
        
        # Vereinfachte Kappa-Approximation
        category_agreement = len(categories) / (len(outputs) * 3)
        kappa = 1.0 - category_agreement
        
        return max(0.0, min(1.0, kappa))


class BiasDetectorTool:
    """Erkennt systematische Verzerrungen in Tool-Outputs"""
    
    def __init__(self):
        self.bias_patterns = {}
    
    def detect_bias(
        self,
        tool_outputs: Dict[str, List[str]],
        baseline: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Analysiert Tool-Outputs auf systematische Verzerrungen
        
        Args:
            tool_outputs: {tool_name: [outputs]}
            baseline: Erwartete Verteilung
        """
        
        biases = []
        
        for tool_name, outputs in tool_outputs.items():
            # Analysiere Themenfokus
            theme_bias = self._detect_theme_bias(outputs)
            
            # Analysiere Längen-Bias
            length_bias = self._detect_length_bias(outputs)
            
            # Analysiere Sentiment-Bias
            sentiment_bias = self._detect_sentiment_bias(outputs)
            
            tool_bias = {
                "tool_name": tool_name,
                "theme_bias": theme_bias,
                "length_bias": length_bias,
                "sentiment_bias": sentiment_bias,
                "overall_bias_score": np.mean([
                    theme_bias["score"],
                    length_bias["score"],
                    sentiment_bias["score"]
                ])
            }
            
            biases.append(tool_bias)
        
        # Identifiziere Ausreißer
        bias_scores = [b["overall_bias_score"] for b in biases]
        mean_bias = np.mean(bias_scores)
        std_bias = np.std(bias_scores)
        
        outliers = []
        for bias in biases:
            if abs(bias["overall_bias_score"] - mean_bias) > 2 * std_bias:
                outliers.append(bias["tool_name"])
        
        return {
            "biases": biases,
            "outliers": outliers,
            "mean_bias": round(mean_bias, 3),
            "recommendation": self._generate_recommendation(biases, outliers)
        }
    
    def _detect_theme_bias(self, outputs: List[str]) -> Dict[str, Any]:
        """Erkennt thematische Verzerrungen"""
        all_themes = []
        for output in outputs:
            # Extrahiere Hauptthemen (vereinfacht: häufigste Substantive)
            words = output.lower().split()
            themes = [w for w in words if len(w) > 6][:5]
            all_themes.extend(themes)
        
        theme_counter = Counter(all_themes)
        
        # Berechne Entropie als Maß für Diversität
        total = sum(theme_counter.values())
        if total == 0:
            return {"score": 0.0, "dominant_themes": []}
        
        probs = [count/total for count in theme_counter.values()]
        entropy = -sum(p * np.log(p + 1e-10) for p in probs)
        max_entropy = np.log(len(theme_counter))
        
        diversity = entropy / max_entropy if max_entropy > 0 else 0
        
        return {
            "score": 1.0 - diversity,  # Higher score = more bias
            "dominant_themes": [t for t, _ in theme_counter.most_common(3)]
        }
    
    def _detect_length_bias(self, outputs: List[str]) -> Dict[str, Any]:
        """Erkennt Längen-Verzerrungen"""
        lengths = [len(output) for output in outputs]
        
        if not lengths:
            return {"score": 0.0, "pattern": "none"}
        
        mean_length = np.mean(lengths)
        std_length = np.std(lengths)
        
        # Coefficient of Variation als Bias-Indikator
        cv = std_length / mean_length if mean_length > 0 else 0
        
        pattern = "consistent"
        if cv > 0.5:
            pattern = "highly_variable"
        elif cv < 0.1:
            pattern = "too_uniform"
        
        return {
            "score": min(1.0, cv),
            "pattern": pattern,
            "avg_length": round(mean_length, 0)
        }
    
    def _detect_sentiment_bias(self, outputs: List[str]) -> Dict[str, Any]:
        """Erkennt Sentiment-Verzerrungen (vereinfacht)"""
        positive_words = {"good", "excellent", "great", "best", "perfect", "optimal"}
        negative_words = {"bad", "poor", "worst", "terrible", "problematic", "critical"}
        
        pos_count = 0
        neg_count = 0
        
        for output in outputs:
            words = set(output.lower().split())
            pos_count += len(words & positive_words)
            neg_count += len(words & negative_words)
        
        total = pos_count + neg_count
        if total == 0:
            return {"score": 0.0, "tendency": "neutral"}
        
        pos_ratio = pos_count / total
        
        tendency = "neutral"
        if pos_ratio > 0.7:
            tendency = "positive_bias"
        elif pos_ratio < 0.3:
            tendency = "negative_bias"
        
        # Bias score: Abweichung von 0.5 (neutral)
        bias_score = abs(pos_ratio - 0.5) * 2
        
        return {
            "score": bias_score,
            "tendency": tendency,
            "positivity_ratio": round(pos_ratio, 2)
        }
    
    def _generate_recommendation(self, biases: List[Dict], outliers: List[str]) -> str:
        """Generiert Handlungsempfehlung"""
        if not outliers:
            return "Alle Tools zeigen ausgewogenes Verhalten."
        
        rec = f"Achtung: Tools mit auffälligen Verzerrungen: {', '.join(outliers)}. "
        rec += "Empfehlung: Gewichtung anpassen oder zusätzliche Tools einbeziehen."
        
        return rec


class DelegationOptimizerTool:
    """Optimiert dynamische Task-Delegation basierend auf Performance-Historie"""
    
    def __init__(self):
        self.performance_history = {}
        self.task_patterns = {}
    
    def optimize_delegation(
        self,
        task_description: str,
        available_tools: List[str],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Wählt optimale Tools für Task aus
        
        Args:
            task_description: Beschreibung des Tasks
            available_tools: Liste verfügbarer Tools
            context: Zusätzlicher Kontext
        """
        
        # Extrahiere Task-Features
        task_features = self._extract_task_features(task_description)
        
        # Berechne Tool-Scores
        tool_scores = {}
        for tool in available_tools:
            score = self._calculate_tool_score(tool, task_features)
            tool_scores[tool] = score
        
        # Sortiere nach Score
        sorted_tools = sorted(tool_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Wähle Top-Tools
        recommended_tools = []
        for tool, score in sorted_tools[:3]:
            recommended_tools.append({
                "tool": tool,
                "score": round(score, 3),
                "confidence": self._get_confidence(tool, task_features)
            })
        
        # Generiere Delegation-Strategie
        strategy = self._generate_strategy(recommended_tools, task_features)
        
        return {
            "task_hash": hashlib.md5(task_description.encode()).hexdigest()[:8],
            "recommended_tools": recommended_tools,
            "strategy": strategy,
            "task_features": task_features,
            "fallback_tool": sorted_tools[-1][0] if len(sorted_tools) > 3 else None
        }
    
    def update_performance(
        self,
        tool_name: str,
        task_hash: str,
        success: bool,
        execution_time: float,
        quality_score: float = None
    ):
        """Aktualisiert Performance-Historie"""
        if tool_name not in self.performance_history:
            self.performance_history[tool_name] = []
        
        self.performance_history[tool_name].append({
            "task_hash": task_hash,
            "success": success,
            "execution_time": execution_time,
            "quality_score": quality_score,
            "timestamp": datetime.now().isoformat()
        })
    
    def _extract_task_features(self, task_description: str) -> Dict[str, Any]:
        """Extrahiert Features aus Task-Beschreibung"""
        features = {
            "length": len(task_description),
            "complexity": len(task_description.split()) / 10,
            "has_data": "data" in task_description.lower(),
            "has_analysis": "analys" in task_description.lower(),
            "has_security": "secur" in task_description.lower(),
            "has_code": "code" in task_description.lower() or "implement" in task_description.lower(),
            "keywords": [w for w in task_description.lower().split() if len(w) > 5][:10]
        }
        return features
    
    def _calculate_tool_score(self, tool: str, task_features: Dict[str, Any]) -> float:
        """Berechnet Score für Tool basierend auf Historie"""
        base_score = 0.5
        
        # Check Performance History
        if tool in self.performance_history:
            recent_performance = self.performance_history[tool][-10:]
            success_rate = sum(1 for p in recent_performance if p["success"]) / len(recent_performance)
            base_score = success_rate
        
        # Adjust based on features
        if "deepseek" in tool.lower() and task_features.get("has_data"):
            base_score += 0.1
        if "claude" in tool.lower() and task_features.get("has_analysis"):
            base_score += 0.1
        if "gemini" in tool.lower() and task_features.get("has_code"):
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _get_confidence(self, tool: str, task_features: Dict[str, Any]) -> str:
        """Bestimmt Confidence-Level für Tool-Wahl"""
        if tool not in self.performance_history:
            return "LOW"
        
        history_size = len(self.performance_history[tool])
        if history_size < 5:
            return "LOW"
        elif history_size < 20:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _generate_strategy(
        self, 
        recommended_tools: List[Dict[str, Any]], 
        task_features: Dict[str, Any]
    ) -> str:
        """Generiert Delegation-Strategie"""
        if not recommended_tools:
            return "No suitable tools found. Use default."
        
        top_tool = recommended_tools[0]
        
        if top_tool["confidence"] == "HIGH" and top_tool["score"] > 0.8:
            return f"Single delegation to {top_tool['tool']} (high confidence)"
        elif len(recommended_tools) >= 3:
            tools_list = ", ".join([t["tool"] for t in recommended_tools[:3]])
            return f"Parallel delegation to: {tools_list} with consensus evaluation"
        else:
            return f"Sequential delegation starting with {top_tool['tool']}"


# Export für Integration
META_TOOLS = {
    "consensus_evaluator": ConsensusEvaluatorTool(),
    "reliability_checker": ReliabilityCheckerTool(),
    "bias_detector": BiasDetectorTool(),
    "delegation_optimizer": DelegationOptimizerTool()
}
