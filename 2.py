def classify_triangle(input_string: str)-> str:
    a, b, c = [int(side) for side in input_string.split()]
    result = {'nontreangel': 'Не треугольник', 
              'simpletreangel': 'Обычный',
              'equilateral': 'Равнобедренный'
               'isosceles': 'Равносторонний'}
    if a + b > c and a + c > b and c + b > a:
        if a == b == c:
            return result['isosceles']
        elif a == b or a == c or c == b:
            return result['equilateral']
        else:
            return result['simpletreangel']
    else:
        return result['nontreangel']


input_string = input()
result = classify_triangle(input_string)
print(result)
