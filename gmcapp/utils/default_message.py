from gmcapp.models import MessageTemplate


def get_default_message(username):
    message_template = MessageTemplate.objects.all()

    message = ''
    additional_info = ''

    # Iterate over the queryset to access individual objects
    for template in message_template:
        message_text = template.message_text
        additional_info = template.additional_info

        message_text = message_text.replace('{username}', username)

        # Process each template as needed
        message = f"{message_text}"

    # Now you can use the values of message_text and additional_info
    full_message = message + "\n" + additional_info

    return full_message

