from sympy import solve
from sympy import (Symbol, Eq)

def parse_equation(equation):
    eq = list(equation.replace('^', '**'))
    to_parse = ''
    chars = []
    for i, char in enumerate(eq):
        if char.isalpha():
            if char in chars:
                pass
            else:
                chars.append(char)
            if eq[i-1].isdigit():
                if i != 0:
                    to_parse += f'{eq[i-1]}*{eq[i]}'
                else:
                    to_parse += char
            else:
                to_parse += char
        else:
            if i != len(eq)-1:
                if eq[i].isdigit():
                    if eq[i+1].isalpha():
                        continue
            to_parse += char
    return (to_parse, chars)
    


#for debugging

#equation = "4x + x - 6 - 19"
equation = "x + y -2x + 3"
parsed = parse_equation(equation)
eq = parsed[0] 
symbols = parsed[1]
solved = solve(eq, symbols)
print(solved)
#x = Symbol('x')
#solve(4 * x + x - 6, 19)
