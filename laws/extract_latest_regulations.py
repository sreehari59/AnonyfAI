import json
import PyPDF2
import sys
sys.path.append("../")
from utils import *

with open(regulations_file, "r") as file:
    regulations = json.load(file)

def get_most_recent_file(folderPath):
    if not os.path.isdir(folderPath):
        print("Invalid folder path.")
        return None

    # Get full paths of files only (ignore directories)
    files = [os.path.join(folderPath, f) for f in os.listdir(folderPath)
             if os.path.isfile(os.path.join(folderPath, f))]

    if not files:
        return None

    # Find file with latest creation/modification time
    most_recent_file = max(files, key=os.path.getctime)
    return most_recent_file

def read_pdf_text(filename):
    text = ""

    try:
        with open(filename, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ''
    except Exception as e:
        print(f"Error reading PDF: {e}")

    return text

def get_personal_data_definition(filename):
    pdfText = read_pdf_text(filename)
    system_prompt = "You are an expert in laws and regulations. Based on the input text, generate a list of attributes mentioned in the text with denote personal data. Do not make assumptions and do not proide any explanations. Output should be comma separated strings"
    prompt = make_prompt(system_prompt, pdfText)
    response = ask_ai(prompt)
    lis = [i.lower().strip().encode('ascii', 'ignore').decode('ascii') for i in response.split(",")]
    return lis

# check if regulations exist for a particular law, else add empty json
for d in regulations_dir:
    regulation_name = d.split("/")[-1]
    if not regulations or regulation_name not in regulations.keys():
        regulations[regulation_name] = {}

for d in regulations_dir:
    print(f"For the regulation: {d}")
    regulation_name = d.split("/")[-1]
    current_file = None
    
    if regulations and regulations[regulation_name]:
        current_file = regulations[regulation_name]["filename"]
        
    recent_file = get_most_recent_file(d)
    if current_file and current_file == recent_file:
        print("Most recent file already used.")
        continue
    
    definition = get_personal_data_definition(recent_file)
    if definition == []:
        continue
    regulations[regulation_name]['filename'] = recent_file
    regulations[regulation_name]['definition'] = definition
    
# write into regulations json
with open(regulations_file, "w") as file:
    json.dump(regulations, file, indent=4)