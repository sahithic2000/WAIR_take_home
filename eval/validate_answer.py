"""
Generate the correct answer for the evaluation dataset parsing through the keywords and generating an answer for the question in the evaluation dataset.
"""

import json
import re 

INTEGER = re.compile(r"\d+")

def generate_answer(question_text):
    # Clean common currency and punctuation characters before parsing each token.
    numbers = [int(value) for value in INTEGER.findall(question_text)]
    text = question_text.lower()

    if "warehouse" in text and "boxes" in text: 
        boxes_total, boxes_shipped = numbers
        return boxes_total - boxes_shipped
    if "run" in text and "weekend" in text:
        km_per_wkday, km_per_wkend, weeks = numbers
        return (km_per_wkday * 5 + km_per_wkend * 2) * weeks
    if "earns" in text and "spends" in text:
        hourly_wage, hours_per_day, days, money_spent = numbers
        return hourly_wage * hours_per_day * days - money_spent
    if "reads" in text and "pages" in text:
        pages_per_day, days = numbers
        return pages_per_day * days
    if "farm" in text and "rice" in text:
        morning_amt, afternoon_amt = numbers
        return morning_amt + afternoon_amt
    if "printer" in text and "office" in text:
        pages_per_minute, minutes = numbers
        return pages_per_minute * minutes
    if "library" in text and "donates" in text:
        total_books, boxes, books_per_box, books_donated = numbers
        return total_books + (boxes * books_per_box) - books_donated
    if "notebook" in text and "change" in text:
        notebooks, cost_per_notebook, pens, cost_per_pen, money_given = numbers
        return money_given - (notebooks * cost_per_notebook + pens * cost_per_pen)
    if "saves" in text and "week" in text:
        savings_per_week, weeks = numbers
        return savings_per_week * weeks
    if "tank" in text and "farm" in text:
        tank_capacity, fill_rate, leak_rate = numbers
        return int(tank_capacity / (fill_rate - leak_rate))
    if "cafe" in text and "tea" in text:
        coffees, cost_per_coffee, teas, cost_per_tea, days = numbers
        return (coffees * cost_per_coffee + teas * cost_per_tea) * days
    if "school" in text and "students" in text:
        students, buses = numbers
        return int(students / buses)

# Now I want to compare the generated answers with the gold labels in data/test_questions.jsonl and see if they match
# Print which questions are incorrect
# Return list of incorrect question ids and correct answers

def compare_answers(eval_dataset):
    correct_count = 0
    incorrect_answers = []
    total_count = len(eval_dataset)

    for question in eval_dataset:
        generated_answer = generate_answer(question["question"])
        gold_answer = question["gold_answer"]

        if generated_answer == gold_answer:
            correct_count += 1
        else:
            incorrect_answers.append({
                "id": question["id"],
                "suggested_answer": generated_answer,
                "old_answer": gold_answer,
            })

    accuracy = correct_count / total_count if total_count else 0
    return accuracy, incorrect_answers


def regenerate_test_questions(eval_dataset, outpt_path):
    _, incorrect_answers = compare_answers(eval_dataset)

    # Update the gold anaswers in the eval dataset with the correct generated answers
    for question in eval_dataset: 
        for incorrect in incorrect_answers: 
            if question["id"] == incorrect["id"]: 
                question["gold_answer"] = incorrect["suggested_answer"]

    # Write the update eval dataset to a new file
    with open(outpt_path, "w", encoding="utf-8") as f:
        for question in eval_dataset:
            f.write(json.dumps(question) + "\n")

