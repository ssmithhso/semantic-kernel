# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
)
from semantic_kernel.core_plugins.math_plugin import MathPlugin
from semantic_kernel.core_plugins.time_plugin import TimePlugin
from semantic_kernel.planners.function_calling_stepwise_planner.function_calling_stepwise_planner import (
    FunctionCallingStepwisePlanner,
)
from semantic_kernel.planners.function_calling_stepwise_planner.function_calling_stepwise_planner_options import (
    FunctionCallingStepwisePlannerOptions,
)
from semantic_kernel.utils.settings import azure_openai_settings_from_dot_env_as_dict


async def main():
    kernel = sk.Kernel()

    service_id = "planner"
    kernel.add_service(
        AzureChatCompletion(
            service_id="chat",
            deployment_name="gpt-4-latest",
            api_key="d6305afcade14f66890ee2f14f351ef3",
            endpoint="https://hso-sweden-latest-models.openai.azure.com/",
            api_version="2024-02-15-preview",
        ),
    )

    # cur_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
    # kernel.import_native_plugin_from_directory(cur_dir, "email_plugin")

    kernel.import_plugin_from_object(MathPlugin(), "MathPlugin")
    kernel.import_plugin_from_object(TimePlugin(), "TimePlugin")

    questions = [
        "What is the current hour number, plus 5?",
        "Write a limerick, translate it to Spanish, and send it to Jane",
    ]

    options = FunctionCallingStepwisePlannerOptions(
        max_iterations=10,
        max_tokens=4000,
    )

    planner = FunctionCallingStepwisePlanner(service_id=service_id, options=options)

    for question in questions:
        result = await planner.invoke(kernel, question)
        print(f"Q: {question}\nA: {result.final_answer}\n")

        # Uncomment the following line to view the planner's process for completing the request
        print(f"Chat history: {result.chat_history}\n")


if __name__ == "__main__":
    asyncio.run(main())
