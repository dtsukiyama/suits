import subprocess

command = """pip install -r requirements.txt
             python -m spacy download en
          """ 

print("Installing requirements and english models...")
subprocess.call(command, shell = True)
print("done")



