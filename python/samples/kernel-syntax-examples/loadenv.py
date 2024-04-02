from dotenv import load_dotenv
import semantic_kernel as sk

settings = sk.azure_openai_settings_from_dot_env()
azure_ai_search_settings = sk.azure_aisearch_settings_from_dot_env_as_dict()

print(azure_ai_search_settings)
