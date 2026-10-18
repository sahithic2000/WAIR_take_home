"""
Validate the extraction function.
"""

import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

from eval.extract import extract_answer, extract_answer_new
from eval import score as score_module
from eval.score import score_model

def count_extraction_changes(outputs, model_name): 
	changed = []
	for question_id, response in outputs.items():
		old_answer = extract_answer(response)
		new_answer = extract_answer_new(response)
		# If the answers are different, add to the list of changed answers
		if old_answer != new_answer:
			changed.append({
				"id": question_id,
				"old_answer": old_answer,
				"new_answer": new_answer,
				"response": response,
			})

	return {"model": model_name, "count": len(changed), "details": changed}
			


def score_with_extractor(outputs, questions, extractor):
	# modify the extract call using patch.object to use the new extractor function
	with patch.object(score_module, "extract_answer", extractor):
		result = score_model(outputs, questions)

	return {
		**result,
		"correct": round(result["accuracy"] * result["n_scored"]),
	}
