import yaml
import json
from typing import Any, List, Dict 

with open(file='./src/templates/app_manifest_template.yaml', mode='r') as file:
    data = yaml.safe_load(file)

print(data)
