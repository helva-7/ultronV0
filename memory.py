import uuid
import chromadb

chroma_client = chromadb.PersistentClient(path="./DB")

collection = chroma_client.get_or_create_collection(name="memory")

def print_memories(memories):
    memories_string = "### Inserted memories:\n"
    memories_string +=  "\n".join([f"- {memory}" for memory in memories])
    print(memories_string, "\n")


def results_to_string(results):
    result_string = "### Memory recall results:\n"
    result_string += "\n".join([f"- {entry['document']}" for entry in results])
    print(result_string, "\n")
    return result_string

def process_results(results):
    return [
        {
            "id": results["ids"][0][i], 
            "document": results["documents"][0][i] 
        }
        for i in range(len(results["ids"][0]))
    ]


def insert_memories(memories):
    collection.add(
        documents=memories,
        ids=[f"{uuid.uuid4()}" for _ in range(len(memories))]
    )
    print_memories(memories)
    

def recall_memories(query, num_results=2):
    if num_results is None:
        num_results = 2

    results = collection.query(
        query_texts = [query], 
        n_results = num_results
    )
    processed_results = process_results(results)
    return results_to_string(processed_results)


# insert_memories([
#     "Interests: tech, programming, AI, martial arts (MMA, grappling)",
#     "Prefers quick answers",
#     "Tone preference: humorous",
#     "Favorite programming language: Python",
#     "Favorite MMA fighters: Islam Makhachev, Max Holloway",
#     "Favorite AI topic: LLMs",
#     "Favorite character: Batman",
# ])


# results = recall_memories("favorite activities")


