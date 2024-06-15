from pathlib import Path

from aiogram.types import Message

MESSAGES_TEMPLATES_DIRECTORY_PATH = Path(__file__).parent.joinpath("templates")


TEMPLATES = dict[str, str]()
for template_file_path in filter(lambda path: path.is_file(), MESSAGES_TEMPLATES_DIRECTORY_PATH.rglob("*")):
    template_name = str(template_file_path.relative_to(MESSAGES_TEMPLATES_DIRECTORY_PATH))
    with open(template_file_path,encoding="utf8") as template_file:
        template = template_file.read()
        TEMPLATES[template_name] = template


def get_formatted_message(template_name: str, context_message: Message, context: dict[str, str] | None = None) -> str:
    template = TEMPLATES.get(template_name)

    formatting_data_dict: dict[str, str] = {
        "full_user_name": context_message.from_user.full_name,
        "first_user_name": context_message.from_user.first_name,
        "last_user_name": context_message.from_user.last_name,
    }

    if context is not None:
        formatting_data_dict |= context

    return template.format_map(formatting_data_dict)
