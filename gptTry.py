from openai import OpenAI
client = OpenAI(api_key='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')

response = client.responses.create(
    model="gpt-4.1",
    input="Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)