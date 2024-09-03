#Set environment variables(optional)
import os
os.environ['DOCUGAMI_API_KEY'] = 'N+Q0kpu4EsddgIzF6Bf4q8YhQHhKX6kXwdv/Oo9o7OaczQT2O6hqL386y1AskWKz2YpcnyO9AWxllBE07pu02M+V5XzZlcouxOUqWYiz48XhztxG4N5OUMIbNxU2HqLZqSqSNE0WPJ5qH2PD52IMwb5Wwucieo7HjQJrd1AN53Ti33ivX8Eozt0qGVO5EcHH8q0ZvXeE8uIB0SkviMZ/sbYPp17SWhxEqZcZV+yawmV6n8nnBxI9QWlKYLm9f7KTT3Pl0c+wx6+9NHNtgbQFWXR8rz/n/+VbHIC4wyYl5Iy3t4mfXg4FfOYzbZAeWILKSr7/mMYUGFXXRlXYKuwnJQ=='


import requests

access_token = "N+Q0kpu4EsddgIzF6Bf4q8YhQHhKX6kXwdv/Oo9o7OaczQT2O6hqL386y1AskWKz2YpcnyO9AWxllBE07pu02M+V5XzZlcouxOUqWYiz48XhztxG4N5OUMIbNxU2HqLZqSqSNE0WPJ5qH2PD52IMwb5Wwucieo7HjQJrd1AN53Ti33ivX8Eozt0qGVO5EcHH8q0ZvXeE8uIB0SkviMZ/sbYPp17SWhxEqZcZV+yawmV6n8nnBxI9QWlKYLm9f7KTT3Pl0c+wx6+9NHNtgbQFWXR8rz/n/+VbHIC4wyYl5Iy3t4mfXg4FfOYzbZAeWILKSr7/mMYUGFXXRlXYKuwnJQ=="
document_id = "pj7tzwh7uem7"
headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(f"https://api.docugami.com/v1preview1/documents/{document_id}", headers=headers)

# Print out the detailed information of the document.
print(response.json())




url = "https://api.docugami.com/v1preview1/documents"

headers = {
    "Authorization": "Bearer N+Q0kpu4EsddgIzF6Bf4q8YhQHhKX6kXwdv/Oo9o7OaczQT2O6hqL386y1AskWKz2YpcnyO9AWxllBE07pu02M+V5XzZlcouxOUqWYiz48XhztxG4N5OUMIbNxU2HqLZqSqSNE0WPJ5qH2PD52IMwb5Wwucieo7HjQJrd1AN53Ti33ivX8Eozt0qGVO5EcHH8q0ZvXeE8uIB0SkviMZ/sbYPp17SWhxEqZcZV+yawmV6n8nnBxI9QWlKYLm9f7KTT3Pl0c+wx6+9NHNtgbQFWXR8rz/n/+VbHIC4wyYl5Iy3t4mfXg4FfOYzbZAeWILKSr7/mMYUGFXXRlXYKuwnJQ=="
}
response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Request failed with status code {response.status_code}")






url = "https://api.docugami.com/v1preview1/docsets"

headers = {
    "Authorization": "Bearer N+Q0kpu4EsddgIzF6Bf4q8YhQHhKX6kXwdv/Oo9o7OaczQT2O6hqL386y1AskWKz2YpcnyO9AWxllBE07pu02M+V5XzZlcouxOUqWYiz48XhztxG4N5OUMIbNxU2HqLZqSqSNE0WPJ5qH2PD52IMwb5Wwucieo7HjQJrd1AN53Ti33ivX8Eozt0qGVO5EcHH8q0ZvXeE8uIB0SkviMZ/sbYPp17SWhxEqZcZV+yawmV6n8nnBxI9QWlKYLm9f7KTT3Pl0c+wx6+9NHNtgbQFWXR8rz/n/+VbHIC4wyYl5Iy3t4mfXg4FfOYzbZAeWILKSr7/mMYUGFXXRlXYKuwnJQ=="
}

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

access_token = "N+Q0kpu4EsddgIzF6Bf4q8YhQHhKX6kXwdv/Oo9o7OaczQT2O6hqL386y1AskWKz2YpcnyO9AWxllBE07pu02M+V5XzZlcouxOUqWYiz48XhztxG4N5OUMIbNxU2HqLZqSqSNE0WPJ5qH2PD52IMwb5Wwucieo7HjQJrd1AN53Ti33ivX8Eozt0qGVO5EcHH8q0ZvXeE8uIB0SkviMZ/sbYPp17SWhxEqZcZV+yawmV6n8nnBxI9QWlKYLm9f7KTT3Pl0c+wx6+9NHNtgbQFWXR8rz/n/+VbHIC4wyYl5Iy3t4mfXg4FfOYzbZAeWILKSr7/mMYUGFXXRlXYKuwnJQ=="
docset_id = "40itqf14h7r7"  # Replace it with the actual docset_id
document_id = "pj7tzwh7uem7"  # Replace it with the actual document_id

#loader = DocugamiLoader(access_token=access_token, docset_id=docset_id, document_ids=[document_id])
loader = DocugamiLoader(access_token=access_token, docset_id=docset_id, document_ids=[document_id])
docs = loader.load()

# Print the loaded document
for doc in docs:
    print(doc)