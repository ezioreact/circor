# class instruction:
#     system_instruction = """You are a specialized Technical Data Extraction engine for Industrial Engineering and Procurement documents.

#     TASK:
#     Extract the most relevant answer for the given Key from the provided Chunk. Always attempt to return the closest possible answer — even if it is not an exact match.

#     Technical Word & direct meaning:
#     -Stream parameter = you have to see any relevant [flow, temprature, pressure, flow condition] from the chunk.
#     -water parameter = you have to see any relevant [condensate, colling water, quenching water, pressure, temprature, flow] from the chunk.
#     -product type = you have to see any relevant [Mentioned as itm - DSH 65h- TCV, global value, control valve , PCV] from the chunk.
#     -pressure rating = you have to see any relevant [could be mentioned as Rating or #symbol] from the chunk.
#     -nominal bore / valve size = you have to see any relevant [valvae size could be mentioned as size, nominal bore, body size, pipe size, DN] from the chunk.
#     -Body = you have to see any relevant [body it could be mentioned with body/bonnet] from the chunk.
#     -Trim = you have to see any relevant [It could be Mentioned as Plug, Stem, Spindle, Seat, Cage, Balanced, un-balanced, Multi stage trim, Trim Characterstics] from the chunk.
#     -End connection = you have to see any relevant [it could be mentioned as Raised Flage(RF), ring joint(RTJ), But Welded(BW), socket weld, threaded, NPT, flatface(FF)] from the chunk.
#     -Accessaories = you have to see any relevant [It could be mentioned as Positioner, Limit switch, Solenoid Valve, Position transmitter, Air lock valve (ARV), Volume booster (VB), Volume tank, Tubings, Gauges, Transmitter, Air Filter Regulator, QEV (Quick Exhaust Valve), Pilot Valve] from the chunk.
#     -inspection,NDT = you have to see any relevant [It could menetioned as Non-Destructive Testing (NDT), Ultrasonic Testing, Liquid Penetrant Testing, Magnetic Particle Testing, Eddy Current Testing, Radiographic Testing] from the chunk.
#     -delivery schedule = you have to see any relevant [Delivery mentioned as Incoterms - FOR Destination (Friegt on Road),Ex-Works, FOB, DDP, DAP, CIF] from the chunk.
#     -price format inclusive of = you have to see any relevant [It could be mentioned as Inclusive of Packing, freight, with GST] from the chunk.
#     -guarantee/warranty = you have to see any relevant [Next to Delivery Terms, Guarantee/Warranty] from the chunk.
#     -LD clause = you have to see any relevant [It could be mentioned as Liquidated damage, Cancellation, PO value] from the chunk.
#     -inspection and testing = you have to see any relevant [inspection and testing] from the chunk.
#     -Bid Security and Prformance Bank Guarantee = you have to see any relevant [It could be mentioned as PBG] from the chunk.

#     MANDATORY:
#     - If an exact or highly relevant answer is not found for the given key, return the closest matching chunk available.
#     - Always provide at least a low-relevance match instead of returning empty or null.
#     - If specific parameters, values, or technical specifications are missing or do not exactly match, return the most relevant contextual chunk.
    
#     FALLBACK RULE:
#         - If the key is not found in the chunk, never return null or empty.
#         - Instead write: "This information was not identified in the provided document section and may be available in the relevant datasheet or annexure."
#         - Set status = "NotFound".
    
#     RULES:
#     1. SEMANTIC MATCHING:
#     - Match the key using synonyms, abbreviations, or related terms.
#     - Examples: "Differential Pressure" = "Delta P" = "DP" = "P1-P2"
#     - Examples: "Body" = "Body Material" = "Material of Construction" = "MOC"
#     - Examples: "LD Clause" = "Liquidated Damages" = "Penalty Clause"

#     2. ANSWER LENGTH:
#     - Do NOT limit to one word. Return as much as needed to fully answer the question.
#     - Single value question (e.g. "What is the pressure rating?") => return the value: "Class 300"
#     - Material question (e.g. "What is the body material?") => return: "A105N (Carbon Steel Forged)"
#     - Clause or terms question (e.g. "What are the payment terms?") => return the full relevant sentence or paragraph.
#     - Table data => return all relevant columns: "Min: 200, Normal: 250, Max: 280 DEG C"

#     3. COLUMN PRIORITY:
#     - If data is in a table with Min / Normal / Max columns, return all three values unless the question specifically asks for one.

#     4. BEST EFFORT — NEVER GIVE UP:
#     - If the exact key is not found, return the closest or related information from the chunk.
#     - if the chunk has absolutely zero relevant information.please return the closest chunks.
#     - If partially found, return what is available and set status to "Partial".
#     - always return the answer if key is not directly found

#     5. CONFIDENCE LEVELS:
#     - "Exact"      => Key or standard abbreviation found literally in the chunk.
#     - "Approximate" => Value derived via synonym, context, or calculation.
#     - "Partial"    => Only part of the answer found in the chunk.

#     6. NO HALLUCINATION:
#     - Only extract what is present in the chunk.
#     - Do not invent or assume values not written in the document.

#     7. OUTPUT QUALITY CONTROL:
#     - If extracted text is noisy or unclear => just return the relevant chunk.
#     """
 
#     user_context = """
#     ## Input
#     Key: {Key}
#     Chunk: {chunk}
 
#     # RESPONSE FORMAT
#     # Return result in this exact JSON structure:
#     {{
#         "key": "{Key}",
#         "answer": "<extracted value, sentence, or paragraph — never empty unless truly NotFound>",
#         "page_number": <list[int] or null>,
#         "status": "Exact | Approximate | Partial | NotFound"
#     }}
#     """

#     re_phrase_system_prompt = """You are a procurement engineering assistant specializing in industrial valve and instrumentation specifications.
#     CONTEXT:
#     The document is a Purchase Order / Technical Specification for industrial control valves.
#     It contains sections like: Project Name, Scope of Supply, Steam Parameters, Water Parameters, Product Type, Pressure Rating, Body Material, Trim, End Connection, Accessories, Payment Terms, Delivery Schedule, Warranty, LD Clause, Approvals, Compliance, Bid Security, Integrity Pact.

#     TASK:
#     Take a short keyword and rephrase it into one simple, direct retrieval question.
#     The question must target the exact section heading in the document — not over-interpret the meaning.

#     RULES:
#     - Return ONLY in English
#     - Keep the question SIMPLE and CLOSE to the original keyword
#     - Do NOT add technical assumptions (e.g. do not assume "project name" means "valve project identifier")
#     - Do NOT add fixed suffixes like "as per the purchase specification"
#     - Return ONLY valid JSON in the exact format shown below

#     EXAMPLES:
#     Input: "project name"
#     Output: {{"user_input": "project name", "question": "What is the project name?"}}

#     Input: "product type"
#     Output: {{"user_input": "product type", "question": "What is the product type or item description?"}}

#     Input: "payment terms"
#     Output: {{"user_input": "payment terms", "question": "What are the payment terms and due dates?"}}

#     Input: "LD clause"
#     Output: {{"user_input": "LD clause", "question": "What are the liquidated damages terms for delivery delay?"}}

#     Input: "steam parameters"
#     Output: {{"user_input": "steam parameters", "question": "What are the steam flow rate, temperature and pressure values?"}}

#     RESPONSE FORMAT:
#     {{
#         "user_input": "{user_input_question}",
#         "question": "your rephrased question here"
#     }}"""

#     re_phrase_user_prompt = """Keyword: "{keyword}" """


#     chatbot_system_prompt = """
#         You are a friendly and helpful assistant for industrial engineering documents. You help users understand tenders, RFQs, and technical datasheets about valves, instruments, and process equipment.

#         HOW TO INTERACT:
#         - Be polite, warm, and conversational
#         - Always try to answer if there's any relevant information in the context
#         - Only say "out of context" when the question is completely unrelated to the document

#         GUIDELINES:
#         - Answer from the provided context only
#         - Context may be partial (few lines, fragments, abbreviations) - work with what you have
#         - Same concepts have different names - interpret naturally:
#         * Flow/Temp/Pressure = process parameters
#         * Water/Condensate/Cooling Water/Quenching Water = related fluids
#         * Size/NB/DN/Body Size = valve size
#         * Rating/#/Class = pressure rating
#         * Body/Bonnet = valve body
#         * Plug/Stem/Spindle/Seat/Cage = trim parts
#         * Balanced/Unbalanced/Multi-stage = trim types
#         - Parameters can be shared across lines ("same as", "ditto", "see above")
#         - If partially related but info missing, say what you found and what's missing
#         - If completely irrelevant, return "out of context"

#         TONE:
#         - Warm: "Here's what I found..."
#         - Helpful with partial info: "I can see [X], though [Y] isn't specified here."
#         - Honest about irrelevance: "out of context"

#         OUTPUT FORMAT:
#         {
#             "question": "user question",
#             "answer": "your conversational answer or out of context",
#             "page": []
#         }
#         """

#     chatbot_user_prompt = """
#         CONTEXT:
#         {context}

#         QUESTION:
#         {question}

#         Please answer in a friendly, helpful manner based on the context above. Return your response in the required JSON format.
#         """

#     summary_sys_prompt = """
#     You are an intelligent summarization assistant.

#     Your job is to generate a summary based on:
#     1. The provided text
#     2. The user's specific instructions

#     Rules:
#     - Always prioritize the user's instruction over default behavior
#     - Keep the summary approximately {TARGET_TOKENS} tokens (±10%)
#     - Maintain accuracy and avoid hallucination
#     - Use a natural, human-like tone
#     - Do not include meta phrases like "this summary"

#     Response should be in strcit Json
#     """
#     summary_user_prompt = """
#     Summarize the following text according to the user's preference.
#     reponse on strict JSON format.

#     User Instruction:
#     {USER_INSTRUCTION}

#     Requirements:
#     - Target length: ~{TARGET_TOKENS} tokens (±10%)
#     - Keep title and author if present
#     - Adapt tone, depth, and style based on user instruction

#     Guidelines:
#     1. Focus on what the user asked (e.g., technical, simple, brief, detailed)
#     2. Include key ideas and important details unless user says otherwise
#     3. Expand or compress content based on instruction
#     4. Avoid repetition and unnecessary filler
#     5. Do not include references, citations, or metadata

#     Text:
#     {TEXT}

#     ##Response Format Strictly JSON
#     {{
#         "user_instruction":"{USER_INSTRUCTION}",
#         "summary":"str"
#     }}
#     """

#     default_summary_sys_prmpt = """
#     You are an expert technical document summarizer specializing in industrial tenders, specifications, and procurement documents. Your task is to create a comprehensive, structured summary based on retrieved document chunks.

#     ## Your Objective:
#     Synthesize information from multiple document sections into a coherent, well-organized summary that captures all critical aspects of the document.

#     ## Summary Structure (MANDATORY):
#     Generate a JSON response
    
#     {{
#         "user_instruction":"{default_question}",
#         "summary":"str"
#     }}
#     """
    
#     default_summary_user_prompt = """
#     Create a structured technical summary from the following document chunks retrieved based on the given questions:
#     chunk: {TEXT}

#     ##question:
#     {default_question}

#     ## Requirements:
#     - Target summary size: Approximately {TARGET_TOKENS} tokens
#     - Focus on actionable, specific information
#     - Preserve all critical technical data, numbers, and standards
#     - If information for a section is not found, explicitly state "Not specified in document"
#     Generate the summary now."""




import json
import re
from src.multi_agent.llm_json_repair import json_parse_repairing


async def safe_json_loads(content):
    try:
        return json.loads(content)

    except Exception:
        # Step 1: Extract JSON array
        match = re.search(r"\[.*\]", content, re.DOTALL)
        
        if match:
            extracted = match.group(0)

            try:
                return json.loads(extracted)
            except Exception:
                # Step 2: Repair extracted JSON
                try:
                    return await json_parse_repairing(json_docs=extracted)
                except Exception:
                    print(" Invalid JSON after extraction:\n", extracted)
                    return []

        # Step 3: Repair full content
        try:
            return await json_parse_repairing(json_docs=content)
        except Exception:
            print(" Invalid JSON:\n", content)
            return []


# # con = '[\n  {"subject": "Actuator spring material requirement", "relation": "must be manufactured from", "object": "corrosion resistant steel", "context": "Technical Table Data, e)"},\n  {"subject": "Actuator spring material requirement", "relation": "shall be nickel-plated", "object": "true", "context": "Technical Table Data, e)"},\n  {"subject": "Actuator spring material requirement", "relation": "alternatively acceptable", "object": "vendor standard coating", "context": "Technical Table Data, e)"},\n  {"subject": "Actuator spring material requirement", "relation": "shall be enclosed in", "object": "actuator casing", "context": "Technical Table Data, e)"},\n  {"subject": "Desuperheater actuator and valve actuator", "relation": "shall be provided with", "object": "stem position indicator", "context": "Technical Table Data, f)"},\n  {"subject": "Stem position indicator", "relation": "shall have scale calibrated from", "object": "0 to 100%", "context": "Technical Table Data, f)"},\n  {"subject": "Stem position indicator", "relation": "shall have scale in steps of", "object": "10%", "context": "Technical Table Data, f)"},\n  {"subject": "Actuator sizing", "relation": "vendor must ensure compliance with", "object": "sizing factors indicated below", "context": "Technical Table Data, g)"},\n  {"subject": "Actuator sizing", "relation": "higher sizing factor may be considered if", "object": "found necessary by vendor", "context": "Technical Table Data, g)"},\n  {"subject": "Actuator sizing for leakage class IV and below", "relation": "shall consider actuator thrust more than", "object": "1.3 times the total force induced by shut-off conditions", "context": "Technical Table Data, i.1)"},\n  {"subject": "Actuator sizing for leakage class IV and below", "relation": "shall consider actuator thrust more than", "object": "1.3 times the force required to overcome packing friction", "context": "Technical Table Data, i.1)"},\n  {"subject": "Actuator sizing for leakage class IV and below", "relation": "vendor shall utilize factor as", "object": "1.5", "context": "Technical Table Data, i.1", "condition": "when desuperheater/PRDS operates between 80% to 90% or 10% to 20%"},\n  {"subject": "Actuator sizing for leakage class V and above", "relation": "shall consider actual thrust more than", "object": "1.7 times the total force induced by shut-off conditions", "context": "Technical Table Data, ii.1")},\n  {"subject": "Actuator sizing for leakage class V and above", "relation": "shall consider actual thrust more than", "object": "1.7 times the force required to overcome packing friction", "context": "Technical Table Data, ii.1)"},\n  {"subject": "Stroke time with positioner", "relation": "shall be equal to", "object": "valve body size in seconds", "context": "Technical Table Data, h)"},\n  {"subject": "Actuator", "relation": "shall be sized for", "object": "shut-off differential pressure indicated in datasheet / variant table", "context": "Technical Table Data, i)"},\n  {"subject": "Actuator", "relation": "shall be designed to move valve to", "object": "failure position specified in datasheet / variant table", "context": "Technical Table Data, j)"},\n  {"subject": "Actuator casing", "relation": "shall be made of", "object": "pressed steel", "context": "Technical Table Data, k)"},\n  {"subject": "Actuator casing", "relation": "shall not be made of", "object": "non-metallic material", "context": "Technical Table Data, k)"},\n  {"subject": "Springs", "relation": "shall be corrosion-resistant", "object": "true", "context": "Technical Table Data, l)"},\n  {"subject": "Springs", "relation": "shall be cadmium or nickel-plated", "object": "true", "context": "Technical Table Data, l)"},\n  {"subject": "Springs", "relation": "alternatively acceptable", "object": "vendor standard coating", "context": "Technical Table Data, l", "condition": "if accepted by customer"},\n  {"subject": "Springs", "relation": "shall be of", "object": "enclosed type", "context": "Technical Table Data, l)"},\n  {"subject": "Springs", "relation": "shall have compression", "object": "adjustable", "context": "Technical Table Data, l)"},\n  {"subject": "Actuator operating range", "relation": "in general preferred", "object": "0.2 to 1.0 kg/cm2g", "context": "Technical Table Data, m)"},\n  {"subject": "Actuator operating range", "relation": "higher range may be offered if", "object": "vendor standard actuator model cannot meet specified shutoff pressure", "context": "Technical Table Data, m)"},\n  {"subject": "Actuator type", "relation": "in general shall be", "object": "spring opposed diaphragm type", "context": "Technical Table Data, n)"},\n  {"subject": "Actuator type", "relation": "piston and cylinder type shall be considered only if", "object": "extremely unwieldy based on data in datasheet / variant table", "context": "Technical Table Data, n)"},\n  {"subject": "Piston and cylinder actuator", "relation": "shall be single acting spring return type", "object": "true", "context": "Technical Table Data, o)"},\n  {"subject": "Double acting spring less actuator", "relation": "shall have all accessories including", "object": "pilot valves, booster relays, non-return valve, pressure gauge, volume tank", "context": "Technical Table Data, p)"},\n  {"subject": "Volume tank", "relation": "shall be sized considering", "object": "full stroking of valve for THREE complete cycles", "context": "Technical Table Data, p)"},\n  {"subject": "Volume tank", "relation": "shall be of construction", "object": "carbon steel, epoxy painted or stainless steel", "context": "Technical Table Data, p", "reference": "datasheet"},\n  {"subject": "Volume tank", "relation": "shall be sized as per", "object": "ASME Section VIII", "context": "Technical Table Data, p"},\n  {"subject": "Volume tank", "relation": "shall have design pressure of", "object": "10.5 kg/cm2g gas minimum", "context": "Technical Table Data, p"},\n  {"subject": "Accessories like pressure relief valves, pressure gauge and tubing", "relation": "shall be of material", "object": "316/316L Stainless", "context": "Technical Table Data, p"}\n]'
# con = '[\n  {"subject": "Actuator spring material requirement", "relation": "must be manufactured from", "object": "corrosion resistant steel", "context": "Technical Table Data, e)"},\n  {"subject": "Actuator spring material requirement", "relation": "shall be nickel-plated", "object": "true", "context": "Technical Table Data, e)"},\n  {"subject": "Actuator spring material requirement", "relation": "alternatively acceptable", "object": "vendor standard coating", "context": "Technical Table Data, e)"},\n  {"subject": "Actuator spring material requirement", "relation": "shall be enclosed in", "object": "actuator casing", "context": "Technical Table Data, e)"},\n  {"subject": "Desuperheater actuator and valve actuator", "relation": "shall be provided with", "object": "stem position indicator", "context": "Technical Table Data, f)"},\n  {"subject": "Stem position indicator", "relation": "shall have scale calibrated from", "object": "0 to 100%", "context": "Technical Table Data, f)"},\n  {"subject": "Stem position indicator", "relation": "shall have scale in steps of", "object": "10%", "context": "Technical Table Data, f)"},\n  {"subject": "Actuator sizing", "relation": "vendor must ensure compliance with", "object": "sizing factors indicated below", "context": "Technical Table Data, g)"},\n  {"subject": "Actuator sizing", "relation": "higher sizing factor may be considered if", "object": "found necessary by vendor", "context": "Technical Table Data, g)"},\n  {"subject": "Actuator sizing for leakage class IV and below", "relation": "shall consider actuator thrust more than", "object": "1.3 times the total force induced by shut-off conditions", "context": "Technical Table Data, i.1)"},\n  {"subject": "Actuator sizing for leakage class IV and below", "relation": "shall consider actuator thrust more than", "object": "1.3 times the force required to overcome packing friction", "context": "Technical Table Data, i.1)"},\n  {"subject": "Actuator sizing for leakage class IV and below", "relation": "vendor shall utilize factor as", "object": "1.5", "context": "Technical Table Data, i.1", "condition": "when desuperheater/PRDS operates between 80% to 90% or 10% to 20%"},\n  {"subject": "Actuator sizing for leakage class V and above", "relation": "shall consider actual thrust more than", "object": "1.7 times the total force induced by shut-off conditions", "context": "Technical Table Data, ii.1")},\n  {"subject": "Actuator sizing for leakage class V and above", "relation": "shall consider actual thrust more than", "object": "1.7 times the force required to overcome packing friction", "context": "Technical Table Data, ii.1)"},\n  {"subject": "Stroke time with positioner", "relation": "shall be equal to", "object": "valve body size in seconds", "context": "Technical Table Data, h)"},\n  {"subject": "Actuator", "relation": "shall be sized for", "object": "shut-off differential pressure indicated in datasheet / variant table", "context": "Technical Table Data, i)"},\n  {"subject": "Actuator", "relation": "shall be designed to move valve to", "object": "failure position specified in datasheet / variant table", "context": "Technical Table Data, j)"},\n  {"subject": "Actuator casing", "relation": "shall be made of", "object": "pressed steel", "context": "Technical Table Data, k)"},\n  {"subject": "Actuator casing", "relation": "shall not be made of", "object": "non-metallic material", "context": "Technical Table Data, k)"},\n  {"subject": "Springs", "relation": "shall be corrosion-resistant", "object": "true", "context": "Technical Table Data, l)"},\n  {"subject": "Springs", "relation": "shall be cadmium or nickel-plated", "object": "true", "context": "Technical Table Data, l)"},\n  {"subject": "Springs", "relation": "alternatively acceptable", "object": "vendor standard coating", "context": "Technical Table Data, l", "condition": "if accepted by customer"},\n  {"subject": "Springs", "relation": "shall be of", "object": "enclosed type", "context": "Technical Table Data, l)"},\n  {"subject": "Springs", "relation": "shall have compression", "object": "adjustable", "context": "Technical Table Data, l)"},\n  {"subject": "Actuator operating range", "relation": "in general preferred", "object": "0.2 to 1.0 kg/cm2g", "context": "Technical Table Data, m)"},\n  {"subject": "Actuator operating range", "relation": "higher range may be offered if", "object": "vendor standard actuator model cannot meet specified shutoff pressure", "context": "Technical Table Data, m)"},\n  {"subject": "Actuator type", "relation": "in general shall be", "object": "spring opposed diaphragm type", "context": "Technical Table Data, n)"},\n  {"subject": "Actuator type", "relation": "piston and cylinder type shall be considered only if", "object": "extremely unwieldy based on data in datasheet / variant table", "context": "Technical Table Data, n)"},\n  {"subject": "Piston and cylinder actuator", "relation": "shall be single acting spring return type", "object": "true", "context": "Technical Table Data, o)"},\n  {"subject": "Double acting spring less actuator", "relation": "shall have all accessories including", "object": "pilot valves, booster relays, non-return valve, pressure gauge, volume tank", "context": "Technical Table Data, p)"},\n  {"subject": "Volume tank", "relation": "shall be sized considering", "object": "full stroking of valve for THREE complete cycles", "context": "Technical Table Data, p)"},\n  {"subject": "Volume tank", "relation": "shall be of construction", "object": "carbon steel, epoxy painted or stainless steel", "context": "Technical Table Data, p", "reference": "datasheet"},\n  {"subject": "Volume tank", "relation": "shall be sized as per", "object": "ASME Section VIII", "context": "Technical Table Data, p"},\n  {"subject": "Volume tank", "relation": "shall have design pressure of", "object": "10.5 kg/cm2g gas minimum", "context": "Technical Table Data, p"},\n  {"subject": "Accessories like pressure relief valves, pressure gauge and tubing", "relation": "shall be of material", "object": "316/316L Stainless", "context": "Technical Table Data, p"}\n]'
# import asyncio
# print(asyncio.run(safe_json_loads(content=con)))

# D:\.AI-EzioProject\development\circor_dev_2\src\multi_agent\bom_llm_agent.py

# from src.multi_agent.bom_llm_agent import 