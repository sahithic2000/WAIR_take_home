# Predictions

Fill this in **before modifying any code**, and commit it before your first code change.
Short answers are fine. Being wrong is fine.

## 1. Do you believe the headline (B is better and should ship)? Why or why not?

The judge result and the higher reported accuracy is not enough evidence on why B should be shiped. 

1) It is important to consider how well each are doing in both single step and multi-step questions independently, not under one accuracy measure. We need to understand the entire picture if B's gains are in both styles of questions. 
2) We should also consider if 400 questions is enough to trust that this is a noticeble observed gap for being better. How can we statistically prove this? 
3) Also it seems like it scores the response based on if the number was in the answer but not based on if the answer was reached through a logical explanation, so unless that is validated, we cannot proceed with the "better" language model. 

## 2. What do you suspect might be wrong with this evaluation?

List each suspicion and what made you suspect it.

-  There might be some data error potentially as mentioned by the README, so we need to double check the gold standard document to make sure that we can actually trust all the answers, since we are using those answers for the exact match accuracy. 
- There is also the possibility that the extractor function might not be extracting the correct number if there is more than one number that occurs in the reasoning. We also need to check the scoring function to see how it handles ties, wins, and losses. 
- Also, we need to check for variability in the finetuning examples, so that the model was not just better because of overfitting, and that it can generalize well to the other questions that were not in the finetuning sample. This could also indicate some data leakage issues. 
- As for the judge pairwise, it seems like B's responses are shown first mose of the time, and so to understand if the judge is not biased toward the first answer it sees, we need to run this again but with the opposite order to see if the same answer comes out. 

## 3. After fixing what you can, which way do you expect the A vs B gap to move, and roughly by how much?

I would expect the B's lead to narrow as I uncover issues with the finetuning samples or if there was significant errors found in the gold standard document/extract and score functions that somehow favored the answers of B first.  Maybe, it won't be too much of a lead compared to A, like 1-3 percentage points higher. If we considered the 21 unparsable repsonses as incorrect, we would already bring down B's accuracy down to 65% which only gives a 3.7 lead compared to the previously reported lead of 7.4 percentage points. 


## 4. What would you check first, and why?

I would first check the gold standard document to see if the calculations are correct, because then we will get the true baseline to compare our other answers with. I would also check the extract and score functions to make sure that the baseline is also being computed correctly aside from data issues, and the answers are being picked up and graded correctly. 


