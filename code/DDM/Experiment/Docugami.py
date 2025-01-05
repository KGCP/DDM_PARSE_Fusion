#Set environment variables(optional)
import os
os.environ['DOCUGAMI_API_KEY'] = 'Your API Key'

import requests

access_token = "Your Access Token"
document_id = "document ID"
headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(f"https://api.docugami.com/v1preview1/documents/{document_id}", headers=headers)

# Print out the detailed information of the document.
print(response.json())




url = "https://api.docugami.com/v1preview1/documents"

headers = {
    "Authorization": "Authorization: Bearer {access_token}"}
response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Request failed with status code {response.status_code}")






url = "https://api.docugami.com/v1preview1/docsets"

headers = {
    "Authorization": "Authorization: Bearer {access_token}"}

params = {
    # If you want to use specific query parameters, you can add them here.
    # "name": "<NAME>",
    # "limit": <LIMIT>,
    # "status": "<STATUS>",
    # "minPages": <MINPAGES>,
    # "maxPages": <MAXPAGES>,
    # "minSize": <MINSIZE>,
    # "maxSize": <MAXSIZE>,
    # "samples": <SAMPLES>
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Request failed with status code {response.status_code}")



from langchain.document_loaders import DocugamiLoader
access_token = "Your Access Token"
docset_id = "40itqf14h7r7"  # Replace it with the actual docset_id
document_id = "pj7tzwh7uem7"  # Replace it with the actual document_id

#loader = DocugamiLoader(access_token=access_token, docset_id=docset_id, document_ids=[document_id])
loader = DocugamiLoader(access_token=access_token, docset_id=docset_id, document_ids=[document_id])
docs = loader.load()

# Print the loaded document
for doc in docs:
    print(doc)
