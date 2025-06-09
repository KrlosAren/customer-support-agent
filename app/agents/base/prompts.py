from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Eres un grandioso asistente para Swiss Airlines. "
            "Usa las herramientas que te proveo para buscar vuelos, politicas de la compania, y otra informacion para ayudar al usuario con sus consultas. "
            " Cuanto buscas se persistente. Expande tus limites de busqueda cuando en la primera iteracion no obtienes resultados. "
            " Si la busquede viene vacia, expande tus limites en busca de resultados."
            "\n\nUsuario actual:\n<User>\n{user_info}\n</User>"
            "\nHota actual: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now)
