import os

files = os.listdir(path='questions')
with open(f'questions/{files[0]}', "r", encoding='KOI8-R') as f:
    file_contents = f.read()
print(file_contents)
