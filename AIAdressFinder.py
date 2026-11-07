import os
import openai
import deepseek
from deepseek import DeepSeekAPI
import tiktoken

# Load the API key from an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# track how many tokens using
def num_of_token_in_string(string_to_check:str, encoding_name:str)-> int:
    """return number of token in the string"""
    encoding = tiktoken.Encoding(encoding_name)
    tokens = len(encoding.encode(string_to_check))
    return tokens
    
# Function to interact with ChatGPT
def address_with_gpt(prompt, model="gpt-4o"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an AI tool specializing in geography. When I give you an address, respond in one of the two options assuming from a United States of America perspective: Canadian, Foreign. If it's Foreign, then after a space after the previous response give the country name. If it's Canadian, after the previous response give the state name in full. Example outputs: Canadian, Ontario    Foreign, France     Foreign, Africa"},
                {"role": "user", "content": prompt}
            ]
        )
        output = response['choices'][0]['message']['content'].strip()
        address_type = output.split(", ")[0]
        extra = output.split(", ")[1]
        return str(address_type), str(extra)

    except Exception as e:
        return f"An error occurred: {e}"

# Function to interact with DeepSeek
# Configure DeepSeek API (verify endpoint if different)
deepseek.api_key = os.getenv("DEEPSEEK_API_KEY")

# Initialize DeepSeek client
client = DeepSeekAPI(
    api_key=os.getenv("DEEPSEEK_API_KEY")#,  # Your API key here
    #base_url="https://api.deepseek.com/v1"  # Verify correct API endpoint
)

def address_with_deepseek(prompt, model="deepseek-chat"):
    try:
        response = client.chat_completion(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a geography expert. Analyze addresses from a US perspective and respond with:"
                               "Canadian, <full_state_name> or Foreign, <country_name>. "
                               "Examples: Canadian, Ontario | Foreign, France | Foreign, Africa"
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        full_response = response.choices[0].message.content.strip()
        
        if ", " in full_response:
            address_type, extra_info = full_response.split(", ", 1)
            return str(address_type).strip(), str(extra_info).strip()
        return "Format Error", "Response missing comma separator"
        
    except Exception as e:
        return "API Error", str(e)

# Example usage
if __name__ == "__main__":
    # user_input = "1234 Maple Street, Toronto, ON, M5A 1A1"
    # user_input = "G04, Wilkinson Building, Darlington Campus, 148 City Road, Darlington, NSW 2006"
    user_input = "434 los Almendros, 34d, Rincon, PR 677"
    # ai_response = address_with_gpt(user_input)
    # ai_response = address_with_deepseek(user_input)
    # print( address_with_deepseek(user_input) )
    # x, y = address_with_gpt(user_input)
    # print(x, y)
    # print(f"AI: {ai_response}")
