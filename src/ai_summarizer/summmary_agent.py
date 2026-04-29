
from src.ai_summarizer.summary_model import call_summary_model
from src.ai_summarizer.summary_default_query_agent import generate_default_summary
from src.api_body.pydantic_structure import summary_response
from src.configuration.env_key import EnvironKey

config_ = EnvironKey.setting()

async def summary_routing_agent(request_body):
    query = request_body.query
    summary_size = request_body.summary_length
    s3_buckt_url = request_body.input_document
    modify_ai = request_body.modify_ai

    if modify_ai: #True [direct]
        summary_out = await call_summary_model(Human_input=query,
                             summary_size=summary_size,
                             s3_url=s3_buckt_url,
                             modify=modify_ai)
        
    
    if not modify_ai:#False [agent]
        genralSummary = await generate_default_summary(summary_size=200)
        query = config_['default_summary_question']['re_ranking_summary_query']

        summary_out = await call_summary_model(Human_input=query,
                                summary_size=summary_size,
                                s3_url=s3_buckt_url,
                                modify=modify_ai,
                                general_summary=genralSummary
                                )
        

    return summary_response(id=request_body.id,
                                query="inprogress",
                                ai_response=str(summary_out),
                                s3_url=request_body.input_document)
