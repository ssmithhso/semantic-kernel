# Copyright (c) Microsoft. All rights reserved.

import asyncio

import semantic_kernel as sk
import semantic_kernel.connectors.ai.open_ai as sk_oai
from semantic_kernel.connectors.ai.open_ai.contents.azure_streaming_chat_message_content import (
    AzureStreamingChatMessageContent,
)
from semantic_kernel.connectors.ai.open_ai.contents.open_ai_chat_message_content import OpenAIChatMessageContent
from semantic_kernel.connectors.ai.open_ai.contents.tool_calls import ToolCall
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureAISearchDataSources,
    AzureChatPromptExecutionSettings,
    AzureDataSources,
    ExtraBody,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_role import ChatRole
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.prompt_template.input_variable import InputVariable
from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig

kernel = sk.Kernel()

# Load Azure OpenAI Settings
deployment, api_key, endpoint = sk.azure_openai_settings_from_dot_env()

# For example, AI Search index may contain the following document:

# Emily and David, two passionate scientists, met during a research expedition to Antarctica.
# Bonded by their love for the natural world and shared curiosity, they uncovered a
# groundbreaking phenomenon in glaciology that could potentially reshape our understanding of climate change.

azure_ai_search_settings = sk.azure_aisearch_settings_from_dot_env_as_dict()

# This example index has fields "title", "chunk", and "vector".
# Add fields mapping to the settings.
azure_ai_search_settings["fieldsMapping"] = {
    "titleField": "title",
    "contentFields": ["chunk"],
    "vectorFields": ["vector"],
}
# Add Ada embedding deployment name to the settings and use vector search.
azure_ai_search_settings["embeddingDependency"] = {
    "type": "DeploymentName",
    "deploymentName": "text-ada-002",
}
azure_ai_search_settings["queryType"] = "vector"

# Create the data source settings
az_source = AzureAISearchDataSources(**azure_ai_search_settings)
az_data = AzureDataSources(type="AzureCognitiveSearch", parameters=az_source)
extra = ExtraBody(dataSources=[az_data])
req_settings = AzureChatPromptExecutionSettings(service_id="default", extra_body=extra)

# When using data, set use_extensions=True and use the 2023-12-01-preview API version.
chat_service = sk_oai.AzureChatCompletion(
    service_id="chat-gpt",
    deployment_name=deployment,
    api_key=api_key,
    endpoint=endpoint,
    api_version="2023-12-01-preview",
    use_extensions=True,
)
kernel.add_service(chat_service)

prompt_template_config = PromptTemplateConfig(
    template="{{$user_input}}",
    name="chat",
    template_format="semantic-kernel",
    input_variables=[
        InputVariable(name="chat", description="The history of the conversation", is_required=True, default=""),
        InputVariable(name="request", description="The user input", is_required=True),
    ],
    execution_settings={"default": req_settings},
)

chat = ChatHistory()

chat.add_user_message("Hi there, who are you?")
chat.add_assistant_message("I am an AI assistant here to answer your questions.")

arguments = KernelArguments()

chat_function = kernel.create_function_from_prompt(
    plugin_name="ChatBot", function_name="Chat", prompt_template_config=prompt_template_config
)


async def chat() -> bool:
    try:
        user_input = input("User:> ")
    except KeyboardInterrupt:
        print("\n\nExiting chat...")
        return False
    except EOFError:
        print("\n\nExiting chat...")
        return False

    if user_input == "exit":
        print("\n\nExiting chat...")
        return False

    arguments = KernelArguments(user_input=user_input, execution_settings=req_settings)
    # Non streaming
    # answer = await kernel.invoke(chat_function, input_vars=context_vars)
    # print(f"Assistant:> {answer}")
    arguments = KernelArguments(user_input=user_input, execution_settings=req_settings)

    full_message = None
    print("Assistant:> ", end="")
    async for message in kernel.invoke_stream(chat_function, arguments=arguments):
        print(str(message[0]), end="")
        full_message = message[0] if not full_message else full_message + message[0]
    chat.add_assistant_message(str(full_message))
    print("\n")
    # The tool message containing cited sources is available in the context
    if isinstance(full_message, AzureStreamingChatMessageContent):
        tool_call = ToolCall(full_message.tool_message)
        chat.add_message(
            role=ChatRole.TOOL,
            content=full_message,
            metadata={OpenAIChatMessageContent.ToolIdProperty: tool_call.function.name},
        )
        print(f"Tool:> {full_message.tool_message}")
    return True


async def main() -> None:
    chatting = True
    while chatting:
        chatting = await chat()


if __name__ == "__main__":
    asyncio.run(main())
