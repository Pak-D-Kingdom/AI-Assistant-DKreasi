import os
import json
from app.layers.l1_dkreasi.tools import L1IntentRouter


def run_evaluation():
    eval_file = os.path.join(os.path.dirname(__file__), "l1_routing_set.json")
    with open(eval_file, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    passed = 0
    total = len(dataset)

    print(f"\n==========================================")
    print(f"RUNNING EVALUATION ON L1 ROUTING SET ({total} CASES)")
    print(f"==========================================")

    for case in dataset:
        cid = case["id"]
        query = case["query"]
        expected_intent = case["expected_intent"]
        expected_action = case["expected_action"]
        expected_target = case.get("expected_target")

        decision = L1IntentRouter.detect_and_route(query)
        actual_intent = decision["intent"]
        actual_action = decision["action"]
        actual_target = decision.get("target_url")

        intent_match = actual_intent == expected_intent
        action_match = actual_action == expected_action
        target_match = True
        if expected_target:
            target_match = actual_target is not None and expected_target in actual_target

        if intent_match and action_match and target_match:
            passed += 1
            print(f"[{cid}] PASS: '{query}' -> {actual_intent} ({actual_action})")
        else:
            print(f"[{cid}] FAIL: '{query}' -> Expected: {expected_intent}/{expected_action}, Got: {actual_intent}/{actual_action}")

    accuracy = (passed / total) * 100
    print(f"==========================================")
    print(f"EVALUATION RESULT: {passed}/{total} Passed ({accuracy:.1f}%)")
    print(f"==========================================\n")
    return accuracy >= 100.0


if __name__ == "__main__":
    success = run_evaluation()
    exit(0 if success else 1)
