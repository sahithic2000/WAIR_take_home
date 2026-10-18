# Findings

Name:

How to reproduce every number below: `python audit.py`

## Recommendation

One or two sentences: should the team ship Model B? How confident are you, and what would
change your mind?

I would not recommend shipping Model B at this moment. By fixing the labels and extractor function, we minimzed the pp gap between Model A and Model B by 5 pp. B also performs worse on multi-step questions overall. I need further evidence that the judge is not influenced by the first seen model response through a counterbalanced rerun. I also did not get the chance to check any potential data leakage issues with the finetuning data to see if some of the exact examples might have influenced B to be a better model. 


## Issues found

Most important first. "Effect" means how much this issue changes the A vs B comparison.

| # | Issue | Evidence (how you know) | Effect on the result | Fixed? |
|---|-------|-------------------------|----------------------|--------|
| 1 | Gold-answer errors in test labels | The arithmetic audit flagged 16/400 labels. Examples: q0034 has gold 11 but 760 ÷ 19 = 40; q0074 has gold 1485 but 270 × 11 = 2970; q0210 has gold 127 but 17 × 15 = 255. | After updating the labels, exact match rose from 61.3% to 64.2% for A (+3.0 pp) and 68.6% to 71.2% for B (+2.6 pp). The B−A gap narrowed from 7.4 to 7.0 pp (−0.4 pp). | Yes: corrected labels are in `data/test_questions_correct.jsonl`. |
| 2 | Answer extractor selected an operand instead of the final answer | `audit.md` shows the old extractor returned 5 instead of 275 for A’s q0002 and 10 instead of 10,191 for B’s q0021. The old/new comparison found changed extractions in 76/400 A responses and 49/400 B responses. | With corrected gold labels, A exact match increased from 64.2% (257/400) to 79.0% (316/400), +14.8 pp. B increased from 71.2% (270/379) to 82.1% (311/379), +10.8 pp. The B−A gap narrowed from 7.0 to 3.1 pp (−3.9 pp). | Yes for the audit comparison: the new extractor is implemented and measured. |
| 3 | Aggregate accuracy hides opposite performance by task subset | The corrected exact-match subset table in `results/audit.md` breaks results out by the dataset's `single_step` and `multi_step` labels, using 220 and 180 questions respectively. | With the new extractor and corrected labels, A is higher on multi-step (76.7%, 138/180) than B (71.1%, 113/159 parseable). B leads on single-step (90.0%, 198/220) vs A (80.9%, 178/220). Therefore the overall +3.1 pp parseable-only lead for B hides a 5.6 pp multi-step disadvantage and a 9.1 pp single-step advantage; | Fixed the score function to reflect the performance by task subset. |
| 4 | Pairwise judge presentation order may be associated with its preference | In 400 judge comparisons, B was shown first 294 times and A first 106 times. Among decided comparisons, the judge chose B 76.1% when B was first, but 31.6% when B was second; Fisher's exact two-sided p-value is 1.07 × 10⁻¹². | This is a strong association between B-first order and B winning, but it does not show that order caused the difference: the order groups may contain different questions or responses. The judge's aggregate preference for B should therefore be treated as unreliable supporting evidence, not as an independent confirmation of B's advantage. | Not fixed: this analysis detects an association only. A potential fix is to rerun the same A/B response pairs in counterbalanced order and check whether the judge gives consistent preferences. |

## Corrected results

Your best estimate of A vs B, with uncertainty, and anything the single headline number hides.

Based on the table above, B scores 90% accuracy on single-step questions, and 71.1% accuracy on multi-step questions. A, on the other hand, scores 80.9% accuracy in the single-step questions and 76.7% accuracy in multi-step questions.


## Discussion

At most 700 words in total for this file, excluding the table. What matters most and why,
how your predictions compared with what you found, assumptions you made, and what you
would check next with more time.

My initial prediction was that B's lead would narrow to roughly 1-3 percentage points. The audit supports that direction as correcting the 16 of the gold lables reduced the reported gap from 7.4 to 7.0 points. Additionally, using the new extractor function, affecting 76 answers for model A and 49 answers for model B, reduced the gap further to 3.1 percentage points. Checking the labels first was important because they are the reference used to score both models, and incorrect labels can distort their measured accuracy and comparison. The extractor also needed to identify the final answer rather than the first number it sees, which was not always the final answer. 

I also broke accuracy down by task type to see whether the aggregate score hid different strengths. On single-step questions, B scores 90.0% compared with A's 80.9%; on multi-step questions, A scores 76.7%, compared with B's 71.1% among parseable responses. All 21 of B's unparseable outputs are from the multi-step subset. If those outputs are counted as incorrect, B's multi-step accuracy falls to 62.8%, and its overall accuracy becomes 77.8%—1.3 percentage points below A's 79.0%. Thus, the shipping decision depends on the task mix and on whether unparseable outputs are treated as failures.

After checking and modifying the scoring logic, I examined the pairwise judge results and noticed that B was shown first much more than A: 294 comparisons versus 106. This seemed a bit suspicious after the judge overall prefers Model B as per the report. More specifically, when B was shown first, the judge preferred it in 76.1% of decided comparisons. When B was shown second, it preferred B in only 31.6%. Based on the p-value from the Fisher's test, we find tha there is a strong association between presentation order and judge's choice. However, this test by any means does not probe that seeing B first caused the difference. To test for presentation-order effect, I would rerun each question's same A and B responses with order reversed, so every pair is judged once with A first and once with B. I would compare the paired verdicts to see whether the judge's preference is biased with the order it sees it's reponses. 

I also compared the judge's verdicts with human preferences on the 120 questions that were labeled by both. They agreed on 74.2% of those questions with a Cohen's kappa of 0.578, which measures moderate agreement beyond chance. This provides some support for the judge’s usefulness, but the sample is still pretty limited. Further investigation is required that the judges preference reflects correctness and reasoning. Manual inspection of the cases where the judge prefers the response with the wrong answer is important to understand, and should be considered with additional time. Also, if given more time, I would try to check the fine tuning sample for any of the same questions to make sure that the model does not have any data leakage. Otherwise, B would not generalize well to newer types of questions, and is overfitting in performance. If there is overlap in questions in the fine-tuning set, then I want to score A and B on the overlap vs non-overlap questions to see where B is getting it's performance gain. I want to make sure that all the answers in the fine-tuning sample are correct, so we can avoid the model being pointed toward incorrect answers. 
