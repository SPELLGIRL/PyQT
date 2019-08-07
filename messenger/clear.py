import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
for root, dirs, files in os.walk(cur_dir):
    for file in files:
        if file.endswith(('.log', '.db')):
            print(os.path.join(root, file))
            os.remove(os.path.join(root, file))
