import os

files = os.listdir(path='questions')
with open(f'questions/{files[3]}', "r", encoding='KOI8-R') as f:
    content = f.read().split('\n\n')
    for paragraph in content:
        if paragraph.startswith('Вопрос'):
            print(" ".join(paragraph.split("\n")[1:]), '\n')
            continue
        if paragraph.startswith('Ответ'):
            print(paragraph.split("\n")[1])
            print(10*'=')
