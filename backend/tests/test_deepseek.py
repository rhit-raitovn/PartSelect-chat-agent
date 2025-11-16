import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, 'backend')

# Load environment
load_dotenv('backend/.env')

print("=" * 60)
print("Testing OpenRouter API Connection")
print("=" * 60)

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("❌ OPENROUTER_API_KEY not found in environment")
    sys.exit(1)

print(f"✓ API Key found: {api_key[:10]}...{api_key[-4:]}")

try:
    from openai import OpenAI
    print("✓ OpenAI library imported successfully")
except ImportError as e:
    print(f"❌ Failed to import OpenAI: {e}")
    sys.exit(1)

try:
    client = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1"
    )
    print("✓ OpenRouter client created successfully")
except Exception as e:
    print(f"❌ Failed to create client: {e}")
    sys.exit(1)

print("\nTesting API call...")
try:
    response = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, World!' in one short sentence."}
        ],
    )

    print("✓ API call successful!")
    print(f"\nResponse: {response.choices[0].message.content}")
    print(f"Tokens used: {response.usage.total_tokens}")

except Exception as e:
    print(f"❌ API call failed: {e}")

    if "401" in str(e):
        print("\n💡 Your OpenRouter API key is invalid.")
        print("   - Check it's correct at https://openrouter.ai/settings/keys")
        print("   - Make sure it starts with 'sk-or-'")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! Your OpenRouter API is working.")
print("=" * 60)
