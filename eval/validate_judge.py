"""Audit judge presentation-order effects and compare judge labels with humans."""
import json
import math
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

from eval.judge import judge_win_rate


def _judge_winner(row): 
	# Get the model that the judge picks per each row 
	counts = judge_win_rate([row])["counts"]
	return max(counts, key=counts.get)


def _fisher_exact_two_sided(a, b, c, d): 
	"""Return a two-sided Fisher exact p-value for the order/winner table.

	Inputs form the 2x2 table::

	                 B wins   A wins
	    B shown first   a        b
	    A shown first   c        d

	Ties are excluded. The test checks association between presentation order
	and which model won; it does not establish that order caused the difference.
	"""
	# Fix the row total for the B-first group and the total number of B wins.
	row_one, total = a + b, a + b + c + d
	column_one = a + c
	if total == 0:
		return 1.0

	# Under the null hypothesis of no association, the top-left cell follows a
	# hypergeometric distribution when row and column totals are fixed.
	denominator = math.comb(total, row_one)
	# Find the feasible range for the number of B wins in the B-first group.
	low = max(0, row_one - (total - column_one))
	high = min(row_one, column_one)
	# Probability of the observed table (top-left cell equals a).
	observed = math.comb(column_one, a) * math.comb(total - column_one, row_one - a) / denominator
	# The two-sided p-value sums probabilities of all feasible tables that are
	# at least as unlikely as the observed table.
	p_value = 0.0
	for value in range(low, high + 1):
		probability = math.comb(column_one, value) * math.comb(total - column_one, row_one - value) / denominator
		# Small epsilon accounts for floating-point rounding at equal probabilities.
		if probability <= observed + 1e-12:
			p_value += probability
	# Guard against tiny floating-point overshoot above one.
	return min(p_value, 1.0)

def _agreement_metrics(ids, judge_by_id, human_by_id,labels):

    # ids - a list of question ids
	# judge_by_id - a dictionary mapping question ids to judge decisions
	# human_by_id - a dictionary mapping question ids to human preferences
	# labels - a tuple of possible labels

	if not ids:
		return {"n": 0, "agreement": 0.0, "kappa": None, "confusion": {}}

	judge_labels = [_judge_winner(judge_by_id[qid]) for qid in ids]
	human_labels = [human_by_id[qid] for qid in ids]
	# see how many agree between the judge and the human pairwise 
	agreement = sum(judge == human for judge, human in zip(judge_labels, human_labels)) / len(ids)
	judge_counts, human_counts = Counter(judge_labels), Counter(human_labels)
	expected = sum(judge_counts[label] * human_counts[label] for label in labels) / len(ids) ** 2
	# measures agreement between judge and human label after ajdusting for agreement expected by chance
	kappa = (agreement - expected) / (1 - expected) if expected < 1 else None
	confusion = {judge: {human: 0 for human in labels} for judge in labels}
	for judge, human in zip(judge_labels, human_labels):
		confusion[judge][human] += 1
	return {"n": len(ids), "agreement": agreement, "kappa": kappa, "confusion": confusion}


def analyze_position_effect(judge_rows) :
	
	# Summarize wins/ties by which model was shown first and test asssociation by Fisher test
    # Initalize 3 by 2 dictionary 
	groups = {
		"B_first": {"rows": 0, "A_wins": 0, "B_wins": 0, "ties": 0},
		"A_first": {"rows": 0, "A_wins": 0, "B_wins": 0, "ties": 0},
	}
	for row in judge_rows:
		# collect which model was in what position per row 
		first, second = row["response_1_model"], row["response_2_model"]
		group_name = "B_first" if first == "B" else "A_first"
		# Tally based on which model the judge saw first
		group = groups[group_name]
		group["rows"] += 1
		# Assign the winner of that row a +1
		winner = _judge_winner(row)
		group["ties" if winner == "tie" else f"{winner}_wins"] += 1

	for name, group in groups.items():
		total = group["A_wins"] + group["B_wins"]
		group["total"] = total
		group["tie_rate"] = group["ties"] / group["rows"] if group["rows"] else 0.0
		# Calculate win rate for the model that was shown last
		group["B_win_rate_total"] = group["B_wins"] / total if total else 0.0
		# Calculate win rate for the model that was shown first
		first_model_wins = group["B_wins"] if name == "B_first" else group["A_wins"]
		group["first_position_win_rate_total"] = first_model_wins / total if total else 0.0

	b_first, a_first = groups["B_first"], groups["A_first"]
	# calculate the fisher test 
	p_value = _fisher_exact_two_sided(
		b_first["B_wins"], b_first["A_wins"],
		a_first["B_wins"], a_first["A_wins"],
	)
	return {"groups": groups, "fisher_exact_p_value": p_value}

def calibrate_judge_with_humans(judge_rows, human_rows):
	
	judge_by_id =  {row["id"]: row for row in judge_rows}
	# Get the human response
	human_by_id = {row["id"]: row["human_preference"] for row in human_rows}
	# See which ids exist in both 
	shared = sorted(judge_by_id.keys() & human_by_id.keys())
	labels = ("A", "B", "tie")
	by_order_ids = {"B_first": [], "A_first": []}
	
	for q_id in shared: 
		model = judge_by_id[q_id]["response_1_model"]
		by_order_ids["B_first" if model == "B" else "A_first"].append(q_id)
		
	return {
		"n_judge": len(judge_rows),
		"n_human": len(human_rows),
		"n_shared": len(shared),
		# provide counts for each group in the shared questions
		"human_label_counts_shared": dict(Counter(human_by_id[qid] for qid in shared)),
		"overall": _agreement_metrics(shared, judge_by_id, human_by_id, labels),
		"by_order": {
			name: _agreement_metrics(ids, judge_by_id, human_by_id, labels)
			for name, ids in by_order_ids.items()
		},
	}