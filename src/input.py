user_input = []
while True:
    path = input('csv path:')
    if path == '':
        break
    else:
        user_input.append(path)

print(user_input)