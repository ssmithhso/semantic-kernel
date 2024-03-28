# Copyright (c) Microsoft. All rights reserved.

import os

from dotenv import load_dotenv

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.search_engine import BingConnector
from semantic_kernel.core_plugins import WebSearchEnginePlugin


async def main():

    kernel = sk.Kernel()
    # deployment, key, endpoint, api_version = sk.azure_openai_settings_from_dot_env(include_api_version=True)
    service_id = "chat-gpt"
    kernel.add_service(
        AzureChatCompletion(
            service_id="chat-gpt",
            deployment_name="hso_gpt4",
            api_key="bb6ecad7708346f28bfee99a8fa096ec",
            endpoint="https://hso-openai-gpt4.openai.azure.com/",
            api_version="2024-02-15-preview",
        ),
    )
    connector = BingConnector(api_key="281113fcc16943b7b121b0c42e1fc0bb")
    web_plugin = kernel.import_plugin_from_object(WebSearchEnginePlugin(connector), "WebSearch")

    print("---------------- Question 1 -----------------\n")

    query = "Which country receives the most rain per year?"
    search = web_plugin["search"]
    result = await kernel.invoke(search, query=query)
    print(f"Question: {query}\n")
    print(f"Answer: {result}\n")

    print("---------------- Question 2 -----------------\n")

    prompt = """
    Answer the question using only the data that is provided in the data section.
    Do not use any prior knowledge to answer the question.
    Data: {{WebSearch.search "What is semantic kernel?"}}
    Question: {{$question}}?
    Answer:
    """

    req_settings = kernel.get_service("chat-gpt").get_prompt_execution_settings_class()(service_id=service_id)
    req_settings.temperature = 0.2

    prompt_template_config = sk.PromptTemplateConfig(
        template=prompt,
        name="qna",
        template_format="semantic-kernel",
        execution_settings=req_settings,
    )

    question = "Who is the prrsident of th e us?"
    qna = kernel.create_function_from_prompt(
        function_name="seacrh", plugin_name="search", prompt_template_config=prompt_template_config
    )
    result = await qna.invoke(kernel, question=question, num_results=10, offset=0)

    print(f"Question: {question}\n")
    print(f"Answer: {result}\n")

    """
    Output:
    Semantic Kernel is an open-source SDK that lets you easily combine AI services like OpenAI,
    Azure OpenAI, and Hugging Face with conventional programming languages like C# and Python.
    By doing so, you can create AI apps that combine the best of both worlds.
    Semantic Kernel is at the center of the copilot stack.
    """


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
