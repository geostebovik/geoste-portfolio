#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from m3_analyze import get_endpoint, get_subscription_key   # reuse, don't rewrite
from m5_index import get_search_admin_key, build_embedding_client   # reuse, don't rewrite


def build_chat_client() -> AzureOpenAI:
    """Same shape as m6_generate.py's build_client() -- classic AzureOpenAI
    client, not the v1 GA OpenAI+base_url pattern build_embedding_client()
    uses. Decision, not an oversight: the Aug 11/12 404 that forced the v1
    GA migration was specific to the *embeddings* endpoint under the
    classic client (see STATUS.md's Key Lessons). Chat completions is a
    different endpoint, and m6_generate.py already proves classic
    AzureOpenAI + CHAT_API_VERSION works there in real runs. Rewritten
    fresh here rather than imported from m6_generate.py, because that file
    has real work at module scope (file reads, a live generate loop) that
    would fire as a side effect of importing it.
    """

    load_dotenv()
    account, rg = os.environ["AIF_ACCOUNT"], os.environ["AIF_RESOURCE_GROUP"]
    endpoint = get_endpoint(account, rg)
    key = get_subscription_key(account, rg)

    return AzureOpenAI(azure_endpoint=endpoint, api_key=key, api_version=os.environ["CHAT_API_VERSION"])


def embed_query(client: OpenAI, deployment: str, question: str) -> list[float]:
    """Single-question sibling of m5_index.py's embed_chunks() -- same
    client.embeddings.create() call, one string in and one vector out
    instead of a batch. Must use the same deployment used at indexing time
    (EMBEDDING_DEPLOYMENT in .env) -- vectors from two different
    embedding models are not comparable to each other.
    """

    response = client.embeddings.create(model=deployment, input=[question])
    response_embedding = response.data[0].embedding

    return response_embedding
    

def search_chunks(search_client: SearchClient, query_vector: list[float], top_k: int = 3) -> list[dict]:
    """ azure-search-documents' vector query path
    (VectorizedQuery, search_client.search(vector_queries=...)).

    Expected result once built: a list of dicts (id/section/content, plus
    a relevance score) for the top_k chunks closest to query_vector in
    loan-agreement-index -- the fields set up in m5_index.py's
    ensure_index_exists().
    
    Shorthand version of the code. Long version is for educational purposes: 
    to show how to iterate over the results and build a list of dicts. The 
    shorthand version uses a list comprehension to achieve the same result in one line.

    return [
        {"id": r["id"], "section": r["section"], "content": r["content"], "score": r["@search.score"]}
        for r in results
    ]
    """

    results = search_client.search(
        search_text=None, # Skips the separate full-text ranking component -- vector_queries' k_nearest_neighbors
                          # still restricts results to the top_k nearest-neighbor matches, not every document.
        vector_queries=[VectorizedQuery(vector=query_vector, k_nearest_neighbors=top_k, fields="contentVector")],
        select=["id", "section", "content"],
    )

    chunks = []
    for result in results:
        chunk = {
            "id": result["id"],
            "section": result["section"],
            "content": result["content"],
            "score": result["@search.score"]
        }
        chunks.append(chunk)

    return chunks


def build_context(chunks: list[dict]) -> str:
    """Join the retrieved chunks' content into one prompt-ready string,
    labeled by section -- both so the chat model has section context and
    so you can read the printed context in main() and sanity-check which
    sections actually got retrieved.

    REQUIREMENT, not optional -- confirmed via a live test Aug 20: join
    every chunk in the `chunks` list passed in here, in whatever order
    search_chunks() returned them, not just chunks[0]. Vector search's
    top-ranked result is not guaranteed to be the chunk that actually
    answers the question -- a real test against this document ranked
    "III. SECURITY." (irrelevant to the test question) above
    "I. THE PARTIES." (which held the actual answer) by a 0.009 margin.
    top_k=3 already covers for this at the retrieval stage by returning
    multiple candidates; this function is what has to not throw that
    margin away. Using only the top result here would silently
    reintroduce the exact failure top_k>=1 was chosen to avoid (see
    STATUS.md's Aug 7 M5 design note and the Aug 20 Key Lessons entry on
    vector search's top-1 result not being guaranteed correct).

    """    

    # Generator Expression: an even more compact version, but less easily readable.
    #return "\n\n".join(f"[{chunk['section']}]\n{chunk['content']}" for chunk in chunks) 
    context_pieces = [f"[{chunk['section']}]\n{chunk['content']}" for chunk in chunks]
    return "\n\n".join(context_pieces)


def answer_question(client: AzureOpenAI, deployment: str, question: str, context: str) -> str:
    """One chat completion -- same shape as m6_generate.py's loop body,
    but a single question instead of a batch over qa_pairs. System prompt
    should mirror m6_generate.py's wording ("Answer the question using
    only information from the provided document. If the answer isn't in
    the document, say so.") so a future M6 evaluator run can compare this
    path's answers against the full-document-in-context path on equal
    footing -- swap "document" for "context" since here it's retrieved
    chunks, not the whole markdown.
"""
    response = client.chat.completions.create(model=deployment,
         temperature=0, messages=[{"role": "system", "content": "Answer the question using only information from the provided context. If the answer isn't in the context, say so."},
         {"role": "user", "content": f"{context}\n\nQuestion: {question}"}])
    return response.choices[0].message.content


def main():
    """Wire the retrieval pipeline together end to end. Hardcoded test
    question for this first pass, per plan -- generalize to a CLI arg or
    interactive prompt only after this runs clean once.
    """
    load_dotenv()
    account, rg = os.environ["AIF_ACCOUNT"], os.environ["AIF_RESOURCE_GROUP"]
    embedding_deployment = os.environ["EMBEDDING_DEPLOYMENT"]
    search_service, index_name = os.environ["SEARCH_SERVICE"], os.environ["SEARCH_INDEX_NAME"]
    chat_deployment = os.environ["CHAT_DEPLOYMENT_GPT_5_4_MINI"]   # same as m6_generate.py's second model -- need to compare answers
                   
    search_key = get_search_admin_key(search_service, rg)
    credential = AzureKeyCredential(search_key)

    search_client = SearchClient(endpoint=f"https://{search_service}.search.windows.net", index_name=index_name, credential=credential)

    embedding_client = build_embedding_client()
    chat_client = build_chat_client()

    question = "What is the loan amount?"
    query_vector = embed_query(embedding_client, embedding_deployment, question)
    chunks = search_chunks(search_client, query_vector)
    context = build_context(chunks)
    answer = answer_question(chat_client, chat_deployment, question, context)

    print("Retrieved chunks:")
    for chunk in chunks:
        print(f"Section: {chunk['section']}, Score: {chunk['score']}")
    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    main()
