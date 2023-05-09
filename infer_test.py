import json

def extract_bug_details(json_file_path):
    with open(json_file_path, 'r') as f:
        try:
            json_data = json.load(f)
            bug_type = json_data[0]['bug_type']
            qualifier = json_data[0]['qualifier']
            line = json_data[0]['line']
    
            return bug_type, qualifier, line
        except:
            bug_type = None
            qualifier = None
            line = None
    
    return bug_type, qualifier, line
#bug_type, qualifier, line = extract_bug_details('infer-out/report.json')
#print(bug_type, qualifier, line)

