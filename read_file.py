import os

files = os.listdir(path='questions')
with open(f'questions/{files[2]}', "r", encoding='KOI8-R') as f:
    content = f.read().rsplit('\n\nВопрос')[1:]
    for paragraph in content:
        chunks = paragraph.split('\n\n')
        print('вопрос')
        print(" ".join(chunks[0].split("\n")[1:]))
        print('ответ')
        print(" ".join(chunks[1].split("\n")[1:]))
