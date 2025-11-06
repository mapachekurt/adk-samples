
import os
import httpx
from adk.mcp import Mcp, must_provide, tool
from dotenv import load_dotenv
import google.auth
from google.cloud import aiplatform

load_dotenv()

@tool()
def get_doc(query: str, project: str = must_provide(description="The Google Cloud project ID."),
              location: str = must_provide(description="The Google Cloud location for the AI Platform."),
              api_endpoint: str = "us-central1-aiplatform.googleapis.com") -> str:
    """
    Retrieves documentation for a given query using Google's Vertex AI Search.

    Args:
        query: The query to search for.
        project: The Google Cloud project ID.
        location: The Google Cloud location for the AI Platform.
        api_endpoint: The API endpoint for the AI Platform.

    Returns:
        The search results as a string.
    """
    # Set up the API client
    client_options = {"api_endpoint": api_endpoint}
    client = aiplatform.gapic.VertexRagDataServiceClient(client_options=client_options)

    # Set up the request
    rag_resources = [
        aiplatform.gapic.RagResource(
            rag_corpus="projects/1011885463695/locations/us-central1/ragCorpora/3518131347352322048",
        )
    ]
    request = aiplatform.gapic.RetrieveContextsRequest(
        parent=f"projects/{project}/locations/{location}",
        query=query,
        rag_resources=rag_resources,
    )

    # Send the request and return the response
    response = client.retrieve_contexts(request=request)
    return str(response)


if __name__ == "__main__":
    mcp = Mcp()
    mcp.register(get_doc)
    mcp.run()
