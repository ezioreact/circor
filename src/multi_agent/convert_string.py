

import sys
import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# from llm_output.output import llm_data
async def triplet_to_string(triplets):

    # print("Triplets: ", triplets)

    results = []

    for triplet in triplets:
        formatted = (
            f"{triplet['subject']} "
            f"{triplet['relation'].replace('_', ' ')} "
            f"{triplet['object']}. "
            f"Context: {triplet.get('context', '')}. "
        )
        results.append(formatted)

    return results