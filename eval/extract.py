"""Answer extraction for free-text model responses.

Models answer in natural language, so we pull the numeric answer out of the response
before comparing it to the gold label.
"""
import re

_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")

# this regex with commas embedded in the number such as a 1,000 
_NUMBER2 = re.compile(r"-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")

# this helps follow the keywords in the generated answer to further extract the answer
_ANSWER_MARKER = re.compile(r"\b(?:final\s+)?answer\s*(?:is\s*|:\s*)", re.IGNORECASE)


def extract_answer(response: str):
    """Return the numeric answer stated in `response`, or None if there isn't one.

    Responses usually lead with the answer ("The answer is 42. ..."), so we take the
    number that appears in the response.
    """
    if not response:
        return None
    match = _NUMBER.search(response)
    if match is None:
        return None
    return float(match.group(0))


def extract_answer_new(response): 
    # If there is no response, return None
	if not response:
		return None
	
    # 1st scenario: look for the last explicit Answer marker and take the number after it
	markers  = list(_ANSWER_MARKER.finditer(response))
	if markers:
		# gets the number right after "answer is " or "Answer: "
		match = _NUMBER2.search(response, markers[-1].end())
		if match:
			return float(match.group(0).replace(",", ""))
		
    # 2nd scenario: look for a number at the beginning of the response (including bold markdown)
	start_match = re.match(r"\s*\**\s*(" + _NUMBER2.pattern + r")", response)
	if start_match:
		return float(start_match.group(1).replace(",", ""))

    # 3rd scenario: look for the last number in the response '
	last_match = list(_NUMBER2.finditer(response))
	if not last_match:
		return None
	return float(last_match[-1].group(0).replace(",", ""))

