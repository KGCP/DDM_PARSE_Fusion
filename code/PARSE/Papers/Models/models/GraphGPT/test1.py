from urllib.parse import quote

uri = "https://www.anu.edu.au/onto/scholarly#AcademicEntity-compare_\\fspice:-"

# 对URI进行URL编码
encoded_uri = quote(uri, safe=':/#')

print(f"原始URI: {uri}\n编码后的URI: {encoded_uri}")