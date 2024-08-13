def filter_passed_students(score_string: str, name_string: str) -> list[str]:
    score_list = [int(score) for score in score_string.split(',')]
    name_list = [name for name in name_string.split(',')]
    MAX_SCORE = 35
    result_name = []
    for index, score in enumerate(score_list):
        if score >= MAX_SCORE:
            result_name.append(name_list[index])
    if result_name:
        return result_name
    else:
        result_name.append('Никто')
        return result_name


score_string = input()
name_string = input()
passed_students = filter_passed_students(score_string, name_string)
for student in passed_students:
    print(student)