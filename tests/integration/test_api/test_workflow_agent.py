import pytest
import websockets


@pytest.mark.asyncio
async def test_chat_sequence():

    tutorial_questions = [
        "Hi there, what time is my flight?",
        "Am i allowed to update my flight to something sooner? I want to leave later today.",
        "Update my flight to sometime next week then",
        "The next available option is great",
        "what about lodging and transportation?",
        "Yeah i think i'd like an affordable hotel for my week-long stay (7 days). And I'll want to rent a car.",
        "OK could you place a reservation for your recommended hotel? It sounds nice.",
        "yes go ahead and book anything that's moderate expense and has availability.",
        "Now for a car, what are my options?",
        "Awesome let's just get the cheapest option. Go ahead and book for 7 days",
        "Cool so now what recommendations do you have on excursions?",
        "Are they available while I'm there?",
        "interesting - i like the museums, what options are there? ",
        "OK great pick one and book it for my second day there.",
    ]
    uri = "ws://localhost:8000/chat/ws"  # Ajusta si usas otro puerto o ruta
    async with websockets.connect(uri) as websocket:
        for question in tutorial_questions:
            print(f">>> Enviando: {question}")
            await websocket.send(question)

            response = await websocket.recv()
            print(f"<<< Recibido: {response}")

            # Aquí puedes agregar asserts o validaciones si esperas algo específico
            assert response != "", "Respuesta vacía del agente"
