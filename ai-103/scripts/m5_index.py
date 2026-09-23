#!/usr/bin/env python3

import os, re, time
import json
from pathlib import Path
from azure.core.exceptions import ResourceNotFoundError
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)

from m3_analyze import get_endpoint, build_token_provider   # reuse, don't rewrite

BASE_DIR = Path(__file__).parent
DOCUMENT_PATH = BASE_DIR / ".." / "iip-docs" / "Loan_Agreement_Promissory_Note-CUPortal-Custom-Schema.json"
EMBEDDING_DIMENSIONS = 1536   # text-embedding-3-small default -- verify against the deployment, not assumed


# get_search_admin_key() REMOVED 2026-09-23 (M10 clause 1, own commit). It
# fetched the Search admin key via `az search admin-key show`; nothing tracked
# had called it since the keyless migration at aa96bea -- Search is queried
# with Entra ID and Search Index Data Reader (probe_keyless_search.py).

def load_document_markdown() -> str:
    """Read the CU analyzer output JSON at DOCUMENT_PATH, return
    result["contents"][0]["markdown"]. Same source m6_generate.py uses.
    """
    with open(DOCUMENT_PATH) as f:
        doc_md = json.load(f)["result"]["contents"][0]["markdown"]
    return doc_md


def chunk_by_section(markdown: str) -> list[dict]:
    """Split the markdown into one chunk per roman-numeral section, plus
    the trailing signature block.

    Expected result: 16 chunks -- I through XV (confirmed live in the
    markdown, e.g. "I. THE PARTIES.", "II. PAYMENTS.") plus one unnumbered
    signature block. Each chunk: {"id": ..., "section": ..., "content": ...}.
    """
    # Find every heading and where it sits in the text and stick them in a list
    text = markdown
    headings = list(re.finditer(r'[IVXLCDM]+\.\s+[A-Z][\-\'A-Z\s]*\.', text))
    
    # Pair each heading with the content that comes AFTER it and BEFORE the next one. 
    # The last heading has no "next" to look ahead to, so its
    # content runs to the end of the string (folds the signature block into
    # the final section for now -- separate, deferred problem
    
    chunks = []
    for i, heading in enumerate(headings):
        chunk_id = heading.group(0).split('.')[0]
        section_title = heading.group(0).strip()
        start_of_content = heading.end()
        end_of_content = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        chunks.append({
            "id": chunk_id,
            "section": section_title,
            "content": text[start_of_content:end_of_content]
        })

    sig_line = chunks[-1]["content"]
    split_point = sig_line.find("With my signature below")
    sig_line = sig_line[split_point:]  # This is the signature block
    chunks[-1]["content"] = chunks[-1]["content"][:split_point]  # truncate section XV's content to remove the signature block
    chunks.append({
        "id": "signature",
        "section": "SIGNATURE",
        "content": sig_line
    })

    return chunks


def build_embedding_client() -> OpenAI:
    """v1 GA client shape: plain OpenAI pointed at Azure's v1 base_url,
    not AzureOpenAI + api_version. No api_version parameter exists on
    this class -- the deployment name goes in as model= per-call in
    embed_chunks(), not baked in here.
    """
    load_dotenv()
    account, rg = os.environ["AIF_ACCOUNT"], os.environ["AIF_RESOURCE_GROUP"]

    endpoint = get_endpoint(account, rg)
    # M10 (2026-09-22): keyless. This is the ONLY site using a plain OpenAI
    # client (the v1 GA shape, kept deliberately -- see this function's
    # docstring and the Aug 11/12 embeddings 404 in STATUS.md's Key Lessons).
    # The plain class has no azure_ad_token_provider, so the token provider
    # goes in as api_key: openai-python resolves api_key into an
    # 'Authorization: Bearer <...>' header, which is what this route wants.
    #
    # AUDIENCE: probe_keyless_v1_scope.py tested BOTH candidates against this
    # deployment on 2026-09-22 -- cognitiveservices.azure.com AND
    # ai.azure.com both returned a 1536-dim vector. The docs disagree about
    # which the /openai/v1/ route requires; empirically it takes either.
    # Using the classic audience for consistency with every other call site.
    #
    # A CALLABLE was accepted as api_key (also probed), so the SDK can
    # refresh and there is no token-expiry ceiling on a long indexing run.
    # Refresh-on-expiry is the documented SDK contract, not something the
    # probe observed directly -- it ran for seconds, not 90 minutes.
    client = OpenAI(
        api_key=build_token_provider(),
        base_url=f"{endpoint}/openai/v1/",
    )
    return client


def ensure_index_exists(index_client: SearchIndexClient, index_name: str) -> None:
    """Create `loan-agreement-index` if it doesn't already exist (check
    first -- don't assume this is always a fresh run)."""

    try:
        index_client.get_index(index_name)
        print(f"Index '{index_name}' already exists, skipping creation.")
        return
    except ResourceNotFoundError:
        pass  # Index doesn't exist - create it

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw-algo")],
        profiles=[VectorSearchProfile(name="vector-profile", algorithm_configuration_name="hnsw-algo")],
    )

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="section"),
        SearchableField(name="content"),
        SearchField(
            name="contentVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=EMBEDDING_DIMENSIONS,
            vector_search_profile_name="vector-profile"
        )
    ]

    index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
    index_client.create_index(index)
    print(f"Index '{index_name}' created successfully.")


def embed_chunks(client: OpenAI, deployment: str, chunks: list[dict]) -> list[dict]:
    """Call client.embeddings.create() against every chunk's "content" in
    one batch call, then attach each resulting vector to its chunk dict
    as "contentVector". Matched back by the response's per-item .index,
    not list position -- cheap insurance against relying on an ordering
    guarantee that isn't checked here. Return the chunks, now embedded.
    """
    embeddings = client.embeddings.create(
        model=deployment, 
        input=[chunk["content"] for chunk in chunks]
        )
    
    #Using item.index rather than zip() because the OpenAI Embeddings API returns a list of embeddings in the same order as the input, but it also includes an index field for each embedding. This is useful if you want to ensure that the embeddings are matched with the correct chunks, especially if you were to process them in parallel or if the order could be changed for some reason.
    
    for item in embeddings.data:
        chunks[item.index]["contentVector"]= item.embedding

    return chunks


def upload_chunks(search_client: SearchClient, chunks: list[dict]) -> None:
    """Upload the embedded chunks via search_client.upload_documents().

    Check the per-document result for succeeded=False entries --
    upload_documents() doesn't raise on partial failure, it returns a list
    of per-item results. Same kind of silent-failure trap as
    m6_evaluate.py's wrong-keyword-argument bug (Aug 5) -- verify each
    chunk actually landed.
    """

    results = search_client.upload_documents(documents=chunks)
    failed_results = [result for result in results if not result.succeeded]
    if failed_results:
        print(f"WARNING: {len(failed_results)} chunks failed to upload:")
        for result in failed_results:
            print(f"  - {result.key}: {result.error_message}")
    else:
        print(f"All {len(chunks)} chunks uploaded successfully.")


def main():
    load_dotenv()

    # --- Foundry (embeddings) ---
    aif_account = os.environ["AIF_ACCOUNT"]
    aif_rg = os.environ["AIF_RESOURCE_GROUP"]
    embedding_deployment = os.environ["EMBEDDING_DEPLOYMENT"]

    # --- Search ---
    search_service = os.environ["SEARCH_SERVICE"]
    search_rg = aif_rg   # same resource group -- no separate var needed
    index_name = os.environ["SEARCH_INDEX_NAME"]
    search_endpoint = f"https://{search_service}.search.windows.net"
    # M10 (2026-09-22): keyless. NOTE this path needs MORE than the query
    # path in m5_retrieve.py: ensure_index_exists() is a control-plane
    # action (Search Service Contributor) and upload_chunks() is a
    # dataAction (Search Index Data Contributor). Gerard's Owner
    # inheritance on the Non-Prod management group covers the former,
    # which is why probe_keyless_search.py step [3/3] passed -- that
    # success was NOT evidence the Function identity could do it.
    credential = DefaultAzureCredential()

    # --- Pipeline ---
    markdown = load_document_markdown()
    chunks = chunk_by_section(markdown)
    print(f"Chunked into {len(chunks)} sections")   # expect 16 -- verify, don't assume

    index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
    ensure_index_exists(index_client, index_name)

    embedding_client = build_embedding_client()
    chunks = embed_chunks(embedding_client, embedding_deployment, chunks)

    search_client = SearchClient(endpoint=search_endpoint, index_name=index_name, credential=credential)
    upload_chunks(search_client, chunks)

    # --- Verify, don't assume ---
    # Before checking for count, wait for the indexing to complete. Azure Search may take a few seconds to index the documents after upload. Wait loop to check the document count until it matches the number of chunks uploaded or until a timeout occurs.

    timeout = 30  # seconds
    interval = 2  # seconds
    elapsed = 0
    while True:
        count = search_client.get_document_count()
        if count == len(chunks) or elapsed >= timeout:
            break
        time.sleep(interval)
        elapsed += interval

    print(f"Indexed: {count} documents in '{index_name}'")
    if count != len(chunks):
        print(f"WARNING: uploaded {len(chunks)} chunks but index reports {count} documents")


if __name__ == "__main__":
    main()