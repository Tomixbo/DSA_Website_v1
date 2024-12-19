import random

def code_generator(length=10):
    a = ["maj", "min", "num"]
    code = ""
    for i in range(length):
        k = a[random.randint(0, 2)]
        if k == "maj":
            code += chr(random.randint(ord('A'), ord('Z')))
        elif k == "min":
            code += chr(random.randint(ord('a'), ord('z')))
        else:
            code += str(random.randint(0, 9))
    return code
