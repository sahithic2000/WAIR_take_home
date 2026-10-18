# AI usage log

## Tools used

Which tools, roughly how much, and for what (writing code, debugging, reading code,
brainstorming, editing prose, ...).

I used github copilot and for helping me write a lot of the audit.py code, and some helper functions especially the stats based ones and helped edit my paragraphs that I first self wrote. 

## Where AI helped most

AI helped most with the debugging and helping my ideas flow in writing better. It also helped me understand what is usually done in practice when trying to audit models such as this. AI helped me notice that the judge was seeing B's response most of the time, so I thought I could lead some kind of analysis there. 

## At least one time an AI suggestion was wrong, or you chose not to follow it

What it suggested, how you noticed, and what you did instead.

Copilot suggested reporting Model B’s unparseable responses as incorrect, which would lower its accuracy to 77.8% and put it 1.3 percentage points below Model A. I noticed the existing scorer explicitly treats unparseable outputs as formatting noise and excludes them, so counting them as incorrect would change the scoring assumption rather than simply fix a bug. I kept the original parseable-only score and reported the all-incorrect result as a sensitivity analysis instead.

## Anything you deliberately did without AI, and why

I wrote the functions in validate_answer.py, validate_extract.py and validate_score.py on my own. These functions were pretty straightforward to implement. Checking the gold standard data, extractor and scoring subsets questions were all my ideas. Even the ideas about checking exact fine tuning matches were my ideas. 


