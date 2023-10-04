# message_generation.py
import openai  # Import the OpenAI library


from gmcapp.models import OpenAIAPI, MessageTemplate


def generate_unique_message(username):
    # Define the prompt for OpenAI
    # Define your OpenAI API key
    openai_api_key = OpenAIAPI.objects.first()

    # Check if an API key is available
    if openai_api_key:
        open_api_key = openai_api_key.openai_api_key
    else:
        open_api_key = ""  #

    message_template = MessageTemplate.objects.all()

    additional_info = ''
    message = ''

    # Iterate over the queryset to access individual objects
    for template in message_template:
        default_message = template.message_text
        additional_info = template.additional_info

        # Replace {username} with the actual username
        default_message = default_message.replace('{username}', username)

        # Process each template as needed
        message = f"{default_message}"

    prompt = f"Please act as a professional person and rewrite the message provided below. Write the message in a human touch with a friendly and natural American tone. Avoid using robotic words. Always maintain honesty in the rewrite and refrain from adding any additional information. Always write concise and short messages. Please never use such kind of phrases: 'I hope this message finds you well. \n Message: {message}"

    # Initialize OpenAI API
    openai.api_key = open_api_key

    # Call the OpenAI API to generate the message
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=256,  # Adjust the max tokens as needed
        temperature=0.05,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Extract the generated message from the API response
    generated_message = response.choices[0].text.strip()

    final_message = generated_message + "\n" + additional_info

    return final_message
