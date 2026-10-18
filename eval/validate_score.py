"""Validate exact-match scoring overall and by benchmark subset."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

from eval import score as score_module
from eval.extract import extract_answer_new
from eval.score import score_model, score_model_unparsable


def score_with_new_extractor(outputs: dict, questions: dict, scorer):
	with patch.object(score_module, "extract_answer", extract_answer_new):
		return scorer(outputs, questions)


def compare_overall_scores(outputs_by_model, questions): 
	results = {}
	for model in ("A", "B"):
		outputs = outputs_by_model[model]
		results[model] = {
			"parseable_only": score_with_new_extractor(outputs, questions, score_model),
			"unparseable_incorrect": score_with_new_extractor(outputs, questions, score_model_unparsable),
		}
	return results


def compare_subset_scores(outputs_by_model, questions):
	
	subsets = sorted({question["subset"] for question in questions.values()})
	results = {}
	for model in ("A", "B"):
		results[model] = {}
		for subset in subsets:
			subset_questions = {
				qid: question for qid, question in questions.items()
				if question["subset"] == subset
			}
			parseable_score = score_with_new_extractor(outputs_by_model[model], subset_questions, score_model)
			all_counted_score = score_with_new_extractor(outputs_by_model[model], subset_questions, score_model_unparsable)
			correct = round(parseable_score["accuracy"] * parseable_score["n_scored"])
			incorrect = parseable_score["n_scored"] - correct
			total = len(subset_questions)
			unparseable = all_counted_score["n_unparseable"]
			results[model][subset] = {
				"denominator": total,
				"parseable": parseable_score["n_scored"],
				"correct": correct,
				"incorrect": incorrect,
				"unparseable": unparseable,
				"accuracy_parseable_only": parseable_score["accuracy"],
				"accuracy_unparseable_incorrect": all_counted_score["accuracy"],
				"category_rates": {
					"correct": correct / total if total else 0.0,
					"incorrect": incorrect / total if total else 0.0,
					"unparseable": unparseable / total if total else 0.0,
				},
			}
	return results