import os
import boto3
import streamlit as st


# Initialize Bedrock Agent Runtime client
bedrock_agent_runtime = boto3.client(
    'bedrock-agent-runtime',
    region_name='us-west-2',
    aws_access_key_id = st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key = st.secrets["AWS_SECRET_ACCESS_KEY"]
)

MODEL_ARN = "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"


chat_history = []

def chat(question: str):
    """
    Query AWS Bedrock KB and return a formatted response, maintaining context.
    """
    KNOWLEDGE_BASE_ID = st.secrets["BEDROCK_KNOWLEDGE_BASE_ID"]
    global chat_history

    try:
        # Add user's new question to the history
        chat_history.append({"role": "user", "content": question})

        # Combine messages into a single text block for context
        context_text = "\n".join(
            [f"{m['role'].capitalize()}: {m['content']}" for m in chat_history]
        )

        # Send the entire context to the model
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={'text': context_text},
            retrieveAndGenerateConfiguration={
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': KNOWLEDGE_BASE_ID,
                    'modelArn': MODEL_ARN
                },
                'type': 'KNOWLEDGE_BASE'
            }
        )

        # Extract and format assistant response
        formatted_response = format_response_with_references(response)

        # Add the assistant's reply to history
        chat_history.append({"role": "assistant", "content": formatted_response})

        return formatted_response

    except Exception as e:
        return f"❌ An error occurred while generating a response: {str(e)}"



def format_response_with_references(response):
    """
    Extract and format response with citations (if available).
    """
    try:
        text_response = response['output']['text']
        references = {}

        # Parse citations if they exist
        if 'citations' in response:
            for citation in response['citations']:
                if 'retrievedReferences' in citation:
                    for ref in citation['retrievedReferences']:
                        doc_name = ref['location']['s3Location']['uri'].split('/')[-1]
                        page_num = int(float(ref['metadata'].get('x-amz-bedrock-kb-document-page-number', 1)))

                        if doc_name not in references:
                            references[doc_name] = set()
                        references[doc_name].add(page_num)

        # Format response
        formatted_response = text_response
        if references:
            formatted_response += "\n\n**You can refer to the following sources:**\n"
            for doc, pages in references.items():
                formatted_response += f"* {doc} - Pages {', '.join(map(str, sorted(pages)))}\n"

        return formatted_response

    except Exception as e:
        return f"⚠️ Response formatting error: {str(e)}"


def clear_memory():
    global chat_history
    chat_history = []

