import sys
import os
from unittest.mock import patch, MagicMock
import json
from pydantic import BaseModel, Field

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.core.consistency_checker import ConsistencyChecker
from backend.core.reasoning_analyzer import ReasoningAnalyzer
from backend.core.multipass_evaluator import evaluate_pass1
from backend.services.decision_support_service import generate_full_report
from backend.core.evaluation_engine import DualEvaluationEngine, evaluate_answer_dual

def test_robustness():
    print("Starting Evaluation Robustness Verification...")
    
    # Test Case 1: ConsistencyChecker
    print("\n[Test 1] ConsistencyChecker - Normalization and Clamping")
    checker = ConsistencyChecker()
    
    with patch("backend.core.consistency_checker.run_safe_json_task") as mock_run:
        from backend.core.consistency_checker import ConceptsExtractionModel, ConsistencyVerificationModel
        mock_run.side_effect = [
            ConceptsExtractionModel(concepts=["python", "machine learning"]),
            ConsistencyVerificationModel(concept_correctness=15, concept_consistency_score=15, consistency_score=15)
        ]
        res = checker.check("Q", "A", [])
        print(f"Result Concept Correctness (should be 10): {res['concept_correctness']}")
        assert res["concept_correctness"] == 10
        assert isinstance(res["concepts"], list)
    
    # Test Case 2: ReasoningAnalyzer
    print("\n[Test 2] ReasoningAnalyzer - Out-of-range scores")
    analyzer = ReasoningAnalyzer()
    
    with patch("backend.core.reasoning_analyzer.run_safe_json_task") as mock_run:
        from backend.core.reasoning_analyzer import ReasoningExtractionModel, ReasoningEvaluationModel
        mock_run.side_effect = [
            ReasoningExtractionModel(steps=["step 1", "step 2"], logic_flow="clear"),
            ReasoningEvaluationModel(logical_consistency=15, step_completeness=-5, causal_reasoning=8, confidence=-0.1)
        ]
        res = analyzer.analyze("Q", "A")
        print(f"Result Logical Consistency (should be 10): {res['metrics']['logical_consistency']}")
        print(f"Result Reasoning Score (should be 4.8): {res['reasoning_score']}")
        assert res["metrics"]["logical_consistency"] == 10
        assert res["metrics"]["step_completeness"] == 0
        assert res["reasoning_score"] == 4.8
        assert res["metrics"]["confidence"] == 0.0
        assert isinstance(res["steps"], list)

    # Test Case 3: MultipassEvaluator - Missing RUBRIC keys
    print("\n[Test 3] MultipassEvaluator - Missing rubric keys")
    
    with patch("backend.core.multipass_evaluator.run_safe_json_task") as mock_run:
        from backend.core.multipass_evaluator import Pass1EvaluationModel, CritiquePassModel
        mock_run.side_effect = [
            Pass1EvaluationModel(scores={"Technical Accuracy": 8}, feedback=["Good job"], summary="Overall good"),
            CritiquePassModel(issues=[], suggested_score_adjustment=0)
        ]
        res = evaluate_pass1("Q", "A")
        print(f"Result Scores Keys: {list(res['scores'].keys())}")
        assert "Clarity" in res["scores"]
        assert "Depth" in res["scores"]
        assert "Communication" in res["scores"]
        assert res["scores"]["Clarity"] == 0
    
    # Test Case 4: DualEvaluationEngine
    print("\n[Test 4] DualEvaluationEngine - Combined robustness")
    engine = DualEvaluationEngine()
    with patch("backend.core.evaluation_engine.run_safe_json_task") as mock_run:
        from backend.core.evaluation_engine import TechnicalEvalResult, BehavioralEvalResult
        mock_run.side_effect = [
            TechnicalEvalResult(accuracy=12, depth=8, problem_solving=9),
            BehavioralEvalResult(clarity=8, confidence=15, structure=9)
        ]
        res = engine.evaluate("Q", "A", {"skills": ["python"]})
        print(f"Technical Accuracy (should be 10): {res['technical']['accuracy']}")
        print(f"Confidence (should be 10): {res['behavioral']['confidence']}")
        assert res["technical"]["accuracy"] == 10
        assert res["behavioral"]["confidence"] == 10

    # Test Case 5: DecisionSupportService - Complete LLM failure
    print("\n[Test 5] DecisionSupportService - LLM Failure")
    with patch("backend.core.llm_brain._run_json_task", side_effect=Exception("LLM Timeout")):
        res = generate_full_report(answers=[])
        print(f"Result Candidate Summary: {res['candidate_summary']['overall_impression']}")
        assert res["candidate_summary"]["overall_impression"] == "Summary generation failed"
    
    # Test Case 6: Weighted Reconciliation
    print("\n[Test 6] Weighted Reconciliation Logic")
    
    with patch("backend.core.evaluation_engine.run_safe_json_task") as mock_run_json, \
         patch("backend.core.reasoning_analyzer.run_safe_json_task") as mock_run_reason, \
         patch("backend.core.consistency_checker.run_safe_json_task") as mock_run_consistency:
        
        from backend.core.evaluation_engine import TechnicalEvalResult, BehavioralEvalResult
        from backend.core.reasoning_analyzer import ReasoningExtractionModel, ReasoningEvaluationModel
        from backend.core.consistency_checker import ConceptsExtractionModel, ConsistencyVerificationModel
        
        # Mocking returns
        mock_run_json.side_effect = [
            TechnicalEvalResult(accuracy=8, depth=8, problem_solving=8),
            BehavioralEvalResult(clarity=8, confidence=8, structure=8)
        ]
        
        mock_run_reason.side_effect = [
            ReasoningExtractionModel(steps=["step 1", "step 2"], logic_flow="clear"),
            ReasoningEvaluationModel(logical_consistency=7, step_completeness=7, causal_reasoning=7, confidence=1.0)
        ]
        
        mock_run_consistency.side_effect = [
            ConceptsExtractionModel(concepts=[]),
            ConsistencyVerificationModel(concept_correctness=5, concept_consistency_score=5, consistency_score=5)
        ]
        
        # Long answer to avoid shallow penalty
        long_answer = "This is a comprehensive answer that explains the concepts in great detail to avoid any penalties for being too short or shallow."
        res = evaluate_answer_dual("Q", long_answer, {"skills": ["python"]})
        
        print(f"Base Score: {res['final']['score']}")
        print(f"Reasoning Score: {res['reasoning']['reasoning_score']}")
        print(f"Consistency Score: {res['consistency']['concept_consistency_score']}")
        print(f"Reconciled Score: {res['reconciled_score']}")
        
        # Expected: (8.0 * 0.6) + (7.0 * 0.2) + (5.0 * 0.2) = 4.8 + 1.4 + 1.0 = 7.2
        assert res['reconciled_score'] == 7.2
        assert res['scores']['Reconciled'] == 7.2
        
        # Verify metadata presence
        assert "meta" in res
        print("Metadata present in final response.")
    
    print("\nAll Robustness Tests Passed!")

if __name__ == "__main__":
    try:
        test_robustness()
    except Exception as e:
        print(f"\nTest Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
