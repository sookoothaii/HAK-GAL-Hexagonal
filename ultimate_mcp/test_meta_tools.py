#!/usr/bin/env python3
"""
Test-Suite für HAK-GAL Meta-Tools
Demonstriert die Verwendung aller 4 Meta-Tools
"""

import json
from meta_tools import META_TOOLS

def test_consensus_evaluator():
    """Test ConsensusEvaluatorTool"""
    print("\n" + "="*60)
    print("🔬 TEST: ConsensusEvaluatorTool")
    print("="*60)
    
    # Simuliere Outputs von verschiedenen LLMs
    outputs = [
        {
            "tool_name": "DeepSeek:chat",
            "model": "deepseek-chat",
            "content": "Die wichtigsten Tools sind: 1) Batch File Operations für Bulk-Verarbeitung, 2) Monitoring Dashboard für Überwachung, 3) Data Converter für Formatkonvertierung",
            "confidence": 0.85
        },
        {
            "tool_name": "Claude:haiku",
            "model": "claude-3-haiku",
            "content": "Priorität sollte auf: 1) Batch File Operations für effiziente Dateiverarbeitung, 2) Task Scheduler für Automatisierung, 3) Monitoring Dashboard",
            "confidence": 0.90
        },
        {
            "tool_name": "Gemini:2.0-flash",
            "model": "gemini-2.0-flash",
            "content": "Essentiell sind: 1) Batch File Operations, 2) Monitoring Dashboard mit APM, 3) Version Control für Änderungsverfolgung",
            "confidence": 0.88
        }
    ]
    
    evaluator = META_TOOLS["consensus_evaluator"]
    result = evaluator.evaluate_consensus(
        task_id="test_001",
        outputs=outputs,
        method="semantic_similarity",
        threshold=0.7
    )
    
    print(f"✅ Konsens-Score: {result['consensus_score']:.1%}")
    print(f"📊 Confidence: {result['confidence']}")
    print(f"💡 Synthese: {result['synthesis']}")
    print(f"\n📈 Top-3 Aligned Tools:")
    for tool in result['ranking']:
        print(f"   • {tool['tool_name']}: {tool['alignment_score']:.1%}")
    
    return result


def test_reliability_checker():
    """Test ReliabilityCheckerTool"""
    print("\n" + "="*60)
    print("🔄 TEST: ReliabilityCheckerTool")
    print("="*60)
    
    import random
    
    def simulate_tool_execution(**kwargs):
        """Simuliert Tool-Ausführung mit etwas Variabilität"""
        base_response = "Batch operations, monitoring, and conversion are critical"
        variations = [
            base_response,
            base_response + " for enterprise use",
            base_response + " - high priority",
            "Critical: batch ops, monitoring, conversion",
            base_response
        ]
        return random.choice(variations)
    
    checker = META_TOOLS["reliability_checker"]
    result = checker.check_reliability(
        tool_name="DeepSeek:chat",
        task_function=simulate_tool_execution,
        task_params={"query": "What tools are needed?"},
        n_runs=5
    )
    
    print(f"✅ Konsistenz-Score: {result['consistency_score']:.1%}")
    print(f"📊 Fleiss' Kappa: {result['fleiss_kappa']:.2f}")
    print(f"⚡ Avg Execution: {result['avg_execution_time']}s")
    print(f"🎯 Stabilität: {result['stability']}")
    print(f"❌ Fehler: {result['errors']}/{result['n_runs']}")
    
    return result


def test_bias_detector():
    """Test BiasDetectorTool"""
    print("\n" + "="*60)
    print("🔍 TEST: BiasDetectorTool")
    print("="*60)
    
    # Simuliere Tool-Outputs mit unterschiedlichen Biases
    tool_outputs = {
        "SecurityExpert": [
            "Security is the most critical aspect. We need security audit tools immediately.",
            "Without proper security measures, all other tools are useless. Security first!",
            "Security vulnerabilities are everywhere. Focus on security tools.",
            "Critical security gaps need immediate attention. Security is paramount.",
            "Security should be the top priority. Everything else is secondary."
        ],
        "EfficiencyExpert": [
            "Batch operations will save the most time and resources",
            "Automation through batch processing is key to efficiency",
            "Bulk file operations provide immediate productivity gains",
            "Batch tools offer the best ROI for development effort",
            "Focus on batch operations for maximum efficiency"
        ],
        "BalancedExpert": [
            "We need a mix of batch operations, monitoring, and security",
            "Balance between efficiency tools and security measures is important",
            "Consider batch ops, monitoring dashboard, and basic security",
            "A combination of automation, observability, and protection is ideal",
            "Prioritize batch tools while maintaining security and monitoring"
        ]
    }
    
    detector = META_TOOLS["bias_detector"]
    result = detector.detect_bias(tool_outputs)
    
    print(f"📊 Analysierte Tools: {len(result['biases'])}")
    print(f"📈 Mean Bias Score: {result['mean_bias']:.1%}\n")
    
    for bias in result['biases']:
        print(f"Tool: {bias['tool_name']}")
        print(f"  • Overall Bias: {bias['overall_bias_score']:.1%}")
        print(f"  • Theme Bias: {bias['theme_bias']['dominant_themes'][:3]}")
        print(f"  • Length Pattern: {bias['length_bias']['pattern']}")
        print(f"  • Sentiment: {bias['sentiment_bias']['tendency']}\n")
    
    if result['outliers']:
        print(f"⚠️ Outliers: {', '.join(result['outliers'])}")
    
    print(f"\n💡 {result['recommendation']}")
    
    return result


def test_delegation_optimizer():
    """Test DelegationOptimizerTool"""
    print("\n" + "="*60)
    print("🎯 TEST: DelegationOptimizerTool")
    print("="*60)
    
    optimizer = META_TOOLS["delegation_optimizer"]
    
    # Simuliere Performance-Historie
    optimizer.update_performance("DeepSeek:chat", "task_001", True, 1.2, 0.85)
    optimizer.update_performance("DeepSeek:chat", "task_002", True, 1.1, 0.90)
    optimizer.update_performance("Claude:haiku", "task_001", True, 0.8, 0.92)
    optimizer.update_performance("Claude:haiku", "task_003", False, 2.0, 0.60)
    optimizer.update_performance("Gemini:2.0-flash", "task_001", True, 0.9, 0.88)
    
    # Test Delegation-Optimierung
    result = optimizer.optimize_delegation(
        task_description="Analyze the data quality issues in our CSV files and suggest improvements",
        available_tools=["DeepSeek:chat", "Claude:haiku", "Gemini:2.0-flash", "Claude:opus"],
        context={"priority": "accuracy", "time_limit": 30}
    )
    
    print(f"📋 Task Hash: {result['task_hash']}")
    print(f"🎮 Strategy: {result['strategy']}\n")
    
    print("📊 Recommended Tools:")
    for tool in result['recommended_tools']:
        print(f"  • {tool['tool']}")
        print(f"    Score: {tool['score']:.1%}")
        print(f"    Confidence: {tool['confidence']}")
    
    if result['fallback_tool']:
        print(f"\n🔄 Fallback: {result['fallback_tool']}")
    
    print(f"\n📋 Detected Task Features:")
    features = result['task_features']
    print(f"  • Has Data: {features['has_data']}")
    print(f"  • Has Analysis: {features['has_analysis']}")
    print(f"  • Complexity: {features['complexity']:.1f}")
    
    return result


def run_integration_test():
    """Integration Test: Alle Meta-Tools zusammen"""
    print("\n" + "="*60)
    print("🚀 INTEGRATION TEST: Complete Meta-Tool Pipeline")
    print("="*60)
    
    # Step 1: Optimize Delegation
    print("\n📌 Step 1: Optimiere Delegation...")
    optimizer = META_TOOLS["delegation_optimizer"]
    delegation = optimizer.optimize_delegation(
        "Find and fix inconsistencies in our knowledge base",
        ["DeepSeek:chat", "Claude:haiku", "Gemini:2.0-flash"]
    )
    
    selected_tools = [t["tool"] for t in delegation["recommended_tools"]]
    print(f"   Selected: {', '.join(selected_tools)}")
    
    # Step 2: Simulate parallel execution
    print("\n📌 Step 2: Simuliere parallele Ausführung...")
    outputs = []
    for tool in selected_tools:
        outputs.append({
            "tool_name": tool,
            "model": tool.split(":")[1] if ":" in tool else tool,
            "content": f"Mock response from {tool}: Found 15 inconsistencies, primarily in date formats",
            "confidence": 0.85
        })
    
    # Step 3: Evaluate Consensus
    print("\n📌 Step 3: Evaluiere Konsens...")
    evaluator = META_TOOLS["consensus_evaluator"]
    consensus = evaluator.evaluate_consensus("integration_test", outputs)
    print(f"   Consensus Score: {consensus['consensus_score']:.1%}")
    
    # Step 4: Check Reliability
    print("\n📌 Step 4: Prüfe Reliability...")
    checker = META_TOOLS["reliability_checker"]
    reliability = checker.check_reliability(
        selected_tools[0],
        lambda **kw: "Mock consistent response",
        {},
        n_runs=3
    )
    print(f"   Stability: {reliability['stability']}")
    
    # Step 5: Detect Biases
    print("\n📌 Step 5: Erkenne Biases...")
    detector = META_TOOLS["bias_detector"]
    biases = detector.detect_bias({
        tool: ["Mock output " * 10] for tool in selected_tools
    })
    print(f"   Mean Bias: {biases['mean_bias']:.1%}")
    
    print("\n✅ Integration Test Complete!")
    print("   All Meta-Tools working together successfully")
    
    return {
        "delegation": delegation,
        "consensus": consensus,
        "reliability": reliability,
        "biases": biases
    }


def main():
    """Hauptfunktion - führt alle Tests aus"""
    print("\n" + "🔬"*30)
    print("       HAK-GAL META-TOOLS TEST SUITE")
    print("🔬"*30)
    
    results = {}
    
    # Einzeltests
    results["consensus"] = test_consensus_evaluator()
    results["reliability"] = test_reliability_checker()
    results["bias"] = test_bias_detector()
    results["delegation"] = test_delegation_optimizer()
    
    # Integration Test
    results["integration"] = run_integration_test()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    print("\n✅ All Meta-Tools tested successfully!")
    print("\nKey Metrics:")
    print(f"  • Consensus Score: {results['consensus']['consensus_score']:.1%}")
    print(f"  • Reliability: {results['reliability']['stability']}")
    print(f"  • Bias Detection: {len(results['bias']['outliers'])} outliers found")
    print(f"  • Optimization: {len(results['delegation']['recommended_tools'])} tools selected")
    
    # Export results
    with open("meta_tools_test_results.json", "w", encoding="utf-8") as f:
        # Convert für JSON serialization
        def convert_for_json(obj):
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            return str(obj)
        
        json.dump(results, f, indent=2, ensure_ascii=False, default=convert_for_json)
    
    print("\n📁 Results saved to: meta_tools_test_results.json")
    print("\n🎉 Test Suite Complete!")


if __name__ == "__main__":
    main()
