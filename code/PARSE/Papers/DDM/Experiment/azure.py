from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.ai.language.generation import LanguageGenerationClient
from azure.ai.language.generation.models import GenerateLanguageInput
# 创建一个搜索客户端
search_client = SearchClient(
    endpoint="<Your Search Service endpoint>",
    index_name="<Your Index Name>",
    credential=AzureKeyCredential("<Your Search Service query key>")
)

# 查询数据
results = search_client.search(search_text="<Your query>", size=5)

# 输出结果
for result in results:
    print("{}: {}".format(result["id"], result["content"]))




# 创建一个语言生成客户端
gen_client = LanguageGenerationClient(
    endpoint="<Your OpenAI endpoint>",
    credential=AzureKeyCredential("<Your OpenAI key>")
)

# 使用模型生成文本
prompt = GenerateLanguageInput(prompt="How do I reset my password?", temperature=0.8, max_tokens=100)
response = gen_client.generate_language(inputs=prompt)

# 输出生成的文本
print(response.value[0].text)



from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Create a search client
search_client = SearchClient(
    endpoint="<Your Search Service endpoint>",
    index_name="<Your Index Name>",
    credential=AzureKeyCredential("<Your Search Service query key>")
)

# Query data
results = search_client.search(search_text="<Your query>", size=5)

# Print results
for result in results:
    print("{}: {}".format(result["id"], result["content"]))

from azure.core.credentials import AzureKeyCredential
from azure.ai.language.generation import LanguageGenerationClient
from azure.ai.language.generation.models import GenerateLanguageInput

# Create a language generation client
gen_client = LanguageGenerationClient(
    endpoint="<Your OpenAI endpoint>",
    credential=AzureKeyCredential("<Your OpenAI key>")
)

# Generate text using the model
prompt = GenerateLanguageInput(prompt="How do I reset my password?", temperature=0.8, max_tokens=100)
response = gen_client.generate_language(inputs=prompt)

# Print the generated text
print(response.value[0].text)
