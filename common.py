import json

def extract_json(string):
    # Find the start and end positions of the JSON data
    start_pos = string.find('{')
    end_pos = string.rfind('}') + 1
    
    if start_pos != -1 and end_pos != -1:
        # Extract the JSON data substring
        json_str = string[start_pos:end_pos]
        
        try:
            # Attempt to parse the extracted substring as JSON
            json_data = json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            # If parsing fails, return None or handle the error as needed
            return None
    else:
        return None