# from multi_agent.dev_final_Extraction import generate_embeddings
# from rag_reterival import reterive_list_of_query
# from excel_reader import read_excel_questions
# import pandas as pd
# import time


# # Save to EXCEL data
# async def save_to_excel(all_results, filename=None):
#     if not filename:
#         filename = f"rag_output_{int(time.time())}.xlsx"

#     cleaned_data = []

#     for query, results in all_results.items():
#         for item in results:

#             print("item: ",item)
#             cleaned_data.append({
#                 "Query": query.strip(),
#                 "Answer": item.get("answer", ""),
#                 "Page": ", ".join(map(str, item.get("page_number") or [])),
#                 "Status": item.get("status", "")
#             })

#     df = pd.DataFrame(cleaned_data)

#     # Optional: sort by Query + Status priority
#     priority = {"Exact": 0, "Partial": 1, "Approximate": 2}
#     df["priority"] = df["Status"].map(priority).fillna(99)
#     df = df.sort_values(by=["Query", "priority"]).drop(columns=["priority"])

#     df.to_excel(filename, index=False)
#     print(f"\n Saved to {filename}")



# #Start Create embeddings
# generate_embeddings(document_url="",collections_name="")

# #start infer embeddings and llm 
# list_of_questions = read_excel_questions(file_path="")
# final_results = reterive_list_of_query(list_of_query=list_of_questions)
# save_to_excel(final_results)

