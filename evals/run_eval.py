import os
import json
import argparse
from app.layers.l1_dkreasi.tools import L1IntentRouter
from app.layers.l3_webia.tools import L3IntentRouter


def evaluate_dataset(eval_file: str, router_cls, layer_name: str) -> bool:
    if not os.path.exists(eval_file):
        print(f"Dataset {eval_file} not found.")
        return False

    with open(eval_file, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    passed = 0
    total = len(dataset)

    print(f"\n==========================================")
    print(f"RUNNING EVALUATION ON {layer_name.upper()} DATASET ({total} CASES)")
    print(f"==========================================")

    for case in dataset:
        cid = case["id"]
        query = case["query"]
        expected_intent = case["expected_intent"]
        expected_action = case["expected_action"]
        expected_target = case.get("expected_target")

        decision = router_cls.detect_and_route(query)
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
            print(f"[{cid}] FAIL: '{query}'")
            print(f"   Expected: {expected_intent} | {expected_action} | {expected_target}")
            print(f"   Actual:   {actual_intent} | {actual_action} | {actual_target}")

    accuracy = (passed / total) * 100 if total > 0 else 0
    print(f"==========================================")
    print(f"{layer_name.upper()} RESULT: {passed}/{total} Passed ({accuracy:.1f}%)")
    print(f"==========================================\n")
    return accuracy >= 100.0


def run_all(layer: str = "all"):
    base_dir = os.path.dirname(__file__)
    success = True

    if layer in ["l1", "all"]:
        l1_file = os.path.join(base_dir, "l1_routing_set.json")
        res1 = evaluate_dataset(l1_file, L1IntentRouter, "L1 D-KREASI Routing")
        success = success and res1

    if layer in ["l3", "all"]:
        l3_file = os.path.join(base_dir, "l3_recommendation_set.json")
        res3 = evaluate_dataset(l3_file, L3IntentRouter, "L3 WEBIA Recommendation")
        success = success and res3

    return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--layer", default="all", choices=["l1", "l3", "all"], help="Layer evaluation target")
    args = parser.parse_args()
    ok = run_all(args.layer)
    exit(0 if ok else 1)
