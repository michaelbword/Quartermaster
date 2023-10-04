import aiohttp
from bs4 import BeautifulSoup

def capitalize_each_word(s):
    return ' '.join(word.capitalize() for word in s.split())

def format_attachment_info(gun_name, attachments):
    if attachments:
        formatted_attachments = "\n".join(capitalize_each_word(attachment) for attachment in attachments)
        formatted_gun_name = capitalize_each_word(gun_name)
        return f"{formatted_attachments}"
    else:
        return f"Gun information for {gun_name} not found."

async def get_attachment_names(gun_name):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://wzhub.gg/mw2-loadouts') as response:
                response.raise_for_status()
                content = await response.read()

        soup = BeautifulSoup(content, 'html.parser')

        # Find the gun names and their respective parent elements
        gun_info = {}
        gun_elements = soup.select('.gun-badge__text')
        for element in gun_elements:
            gun_text = element.get_text(strip=True)
            gun_info[gun_text.lower()] = (gun_text, element.find_parent('div', class_='wrap-card__content'))

        # Check if the provided gun_name matches a full or shorthand gun name
        gun_name_lower = gun_name.lower()
        matched_gun_name = None
        if gun_name_lower in gun_info:
            matched_gun_name = gun_info[gun_name_lower][0]
        else:
            # Check for a shorthand match (e.g., !TAQ to TAQ-56)
            for full_name, (display_name, _) in gun_info.items():
                if full_name.startswith(gun_name_lower):
                    matched_gun_name = display_name
                    break

        if matched_gun_name:
            _, parent = gun_info[matched_gun_name.lower()]

            if parent:
                # Extract attachment names and their respective values
                attachment_elements = parent.select('.attachment-card-content__name')
                attachment_values = parent.select('.attachment-card-content__counts span')

                # Format the attachment names and values
                formatted_attachment_info = [
                    f"{att_name.text.strip()} - {att_value.text.strip()}"
                    for att_name, att_value in zip(attachment_elements, attachment_values)
                ]

                # Return the formatted attachment info for the matched gun
                return [format_attachment_info(matched_gun_name, formatted_attachment_info)]

        print(f"Gun information for {gun_name} not found.")
        return None

    except aiohttp.ClientError as e:
        print(f"An error occurred with the request: {str(e)}")
    except Exception as e:
        print(f"An error occurred while fetching attachment names: {str(e)}")

    return None
