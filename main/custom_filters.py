from django import template
import json

register = template.Library()

@register.filter(name="parse")
def parse(value, key):
    try:
        # Parse the JSON string into a Python dictionary
        json_data = json.loads(value)
        
        # Check if the key exists in the dictionary
        if key in json_data:
            return json_data[key]
        else:
            return None  # Return None if the key is not found
    except (json.JSONDecodeError, TypeError):
        return None  # Handle invalid JSON or non-string input gracefully
