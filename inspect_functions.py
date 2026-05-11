# a = {'assistant': [{'question': 'what is the project name', 'answer': "The document doesn't explicitly state the project name. However, it refers to the equipment as 'Desuperheater' and mentions 'Project Specifications & Design Philosophy' as a reference document, which likely contains the project name. The document title is 'Indicative Inspection & Test Plan for Desuperheater', suggesting the project involves a desuperheater system, but the exact project name isn't provided here.", 'page': 4, 'status': 'Partial'}, {'question': 'what is the project name', 'answer': "The document is an 'Indicative Inspection & Test Plan for Desuperheater', which suggests the project involves a desuperheater. However, the specific project name is not directly stated in the provided context.", 'page': 8, 'status': 'Partial'}, {'question': 'what is the project name', 'answer': "Based on the document, the project is related to a 'Desuperheater' as mentioned in the title: 'Indicative Inspection & Test Plan for Desuperheater'. However, the exact project name isn't explicitly stated in the provided context.", 'page': 7, 'status': 'Partial'}, {'question': 'what is the project name', 'answer': "I can see that this document is for a project involving a 'Desuperheater', but the specific project name isn't mentioned in the provided context. The document is an 'Indicative Inspection & Test Plan' for this equipment, and references 'Project Specifications & Design Philosophy' as a source, which might contain the project name.", 'page': 4, 'status': 'Partial'}, {'question': 'what is the project name', 'answer': "The document is an 'Indicative Inspection & Test Plan for Desuperheater', which suggests the project is related to a desuperheater. However, the specific project name isn't explicitly mentioned in the provided context.", 'page': 5, 'status': 'Partial'}], 'status': '200'}


# for i in a['assistant']:
#     print(i['page'])


import re
def s3_file_name(name: str):
    name = name.rsplit(".", 1)[0]
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    name = re.sub(r"^[^a-zA-Z0-9]+", "", name)
    name = re.sub(r"[^a-zA-Z0-9]+$", "", name)
    return name


# print(s3_file_name("https://boomai-bucket.s3.ap-south-1.amazonaws.com/aravindh/BHEL+Spec..pdf"))