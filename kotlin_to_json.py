import json
import re

def kotlin_to_json(kotlin_file, json_file):
    question_pattern = re.compile(r'Question\"(.+?)\", listOf\((.+?)\),(\d+)')

    with open(kotlin_file, 'r', encoding='utf-8') as kf:
        kotlin_content = kf.read()

    questions = []

    for match in question_pattern.finditer(kotlin_content):
        question_text = match.group(1)
        options = [opt.strip().strip('"') for opt in match.group(2).split(',')]
        answer = int(match.group(3))

        questions.append({
            "question": question_text,
            "options": options,
            "answer": answer
        })

    with open(json_file, 'w', encoding='utf-8') as jf:
        json.dump(questions, jf, ensure_ascii=False, indent=4)

# Use the function
kotlin_to_json('Datas.kt', 'questions_converted.json')
