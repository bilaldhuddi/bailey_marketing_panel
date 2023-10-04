import re

from gmcapp.models import MessangerPrimary


def create_messenger_contact(title, page_link, default_message,message_status, source):
    link = page_link
    new_link = link.replace("profile.php?id=", "").replace("groups/", "").replace("pages/", "").replace("pg/", "").replace("about/", "").replace("p/", "")

    match = re.search(r'https://(?:www\.|m\.|web\.)?facebook\.com/([^/?]+)', new_link)
    if match:
        username = match.group(1)

        # Create the Messenger link
        messenger_link = f"https://m.me/{username}"

        # Check if the link already exists in the database
        if not MessangerPrimary.objects.filter(messenger_link=messenger_link).exists():
            # Create a new record if it doesn't exist
            messanger_primary = MessangerPrimary(
                title=title,
                messenger_link=messenger_link,
                source=source,
                message=default_message,
                message_status=message_status

            )
            messanger_primary.save()
            return "success"
        else:
            return "Contact already exists in the database."
    else:
        return "Invalid Facebook page link."
