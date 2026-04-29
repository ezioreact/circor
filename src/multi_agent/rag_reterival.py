from src.multi_agent.bom_llm_agent import connect_raginfer_boomllm
from src.multi_agent.embeddings import TenderRAG
import pandas as pd
import time
import json


# Save to EXCEL data
async def save_to_excel(all_results, filename=None):
    if not filename:
        filename = f"rag_output_{int(time.time())}.xlsx"

    cleaned_data = []

    for query, results in all_results.items():
        for item in results:

            print("item: ",item)
            cleaned_data.append({
                "Query": query.strip(),
                "Answer": item.get("answer", ""),
                "Page": ", ".join(map(str, item.get("page_number") or [])),
                "Status": item.get("status", "")
            })

    df = pd.DataFrame(cleaned_data)

    # Optional: sort by Query + Status priority
    priority = {"Exact": 0, "Partial": 1, "Approximate": 2}
    df["priority"] = df["Status"].map(priority).fillna(99)
    df = df.sort_values(by=["Query", "priority"]).drop(columns=["priority"])

    df.to_excel(filename, index=False)
    print(f"\n Saved to {filename}")






async def reterive_list_of_query(list_of_query, collections_name):
    """ 
    Input: ["aaa","bbbb"]

    proccess: 
        Input -> reterivl -> Bom_llm -> output -> save Excel

    This is the global function used for Summary generation. chat_ai
    """
    print("reteriving Collection name",collections_name)
    rag_engine = TenderRAG(collection_name=collections_name)

    all_results = {}
    for query in list_of_query:
        print(f"\n================ QUERY: {query} ================\n")
        results = await rag_engine.query(question=query)
# 
        # print("Reterival result: ",json.dumps(results, indent=4))
        # 
        # input("..contine.....")
        # """un comment if you want to continue with llm """
        final_response = await connect_raginfer_boomllm(
            chunks=results,
            query=query,
            collections=collections_name
        )

        # print("\n Bom-LLM-response: ",json.dumps(final_response,indent=4))

        all_results[query] = final_response

    import json
    # print("rag_response: ",json.dumps(results, indent=4))
    save_to_excel(all_results)
    return all_results    

