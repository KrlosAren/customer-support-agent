from langchain_core.tools import tool
import sqlite3
from datetime import date, datetime
from typing import Callable, Optional
import pytz
from langchain_core.runnables import RunnableConfig
from app.utils.logger import get_logger

logger = get_logger(name=__name__)


def create_flight_booking_tools(db_path: str) -> list[Callable]:

    @tool
    def fetch_user_flight_information(config: RunnableConfig) -> list[dict]:
        """Fetch all tickets for the user along with corresponding
        flight information and seat assignments.

        Returns:
            A list of dictionaries where each dictionary contains
            the ticket details,
            associated flight details, and the seat assignments
            for each ticket belonging to the user.
        """
        logger.info("Fetching user flight information from the database.")

        configuration = config.get("configurable", {})
        passenger_id = configuration.get("passenger_id", None)
        logger.info(
            f"Fetching user flight information for passenger_id: {passenger_id}"
        )

        if not passenger_id:
            raise ValueError("No passenger ID configured.")

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                query = """
                    select
                        t.ticket_no,
                        t.book_ref,
                        f.flight_id,
                        f.flight_no,
                        f.departure_airport,
                        f.arrival_airport,
                        f.scheduled_departure,
                        f.scheduled_arrival,
                        bp.seat_no,
                        tf.fare_conditions
                    from
                        boarding_passes bp
                    join flights f on
                        (f.flight_id = bp.flight_id )
                    join ticket_flights tf on
                        (tf.flight_id = f.flight_id )
                    join tickets t on
                        (t.ticket_no = tf.ticket_no )
                    where
                        t.passenger_id = ?
                    ;
                """
                cursor.execute(query, (passenger_id,))
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]
                # No necesitas cerrar cursor manualmente con 'with' statement
                logger.info(
                    f"Found {len(results)} tickets for passenger_id: {passenger_id}"
                )
                return results
        except sqlite3.Error as e:
            breakpoint()
            logger.error(f"Database error in fetch_user_flight_information: {e}")
            return []

    @tool
    def search_flights(
        departure_airport: Optional[str] = None,
        arrival_airport: Optional[str] = None,
        start_time: Optional[date | datetime] = None,
        end_time: Optional[date | datetime] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Search for flights based on departure airport, arrival airport, and departure time range."""

        query = "SELECT * FROM flights WHERE 1 = 1"
        params = []

        if departure_airport:
            query += " AND departure_airport = ?"
            params.append(departure_airport)

        if arrival_airport:
            query += " AND arrival_airport = ?"
            params.append(arrival_airport)

        if start_time:
            query += " AND scheduled_departure >= ?"
            params.append(start_time)

        if end_time:
            query += " AND scheduled_departure <= ?"
            params.append(end_time)

        query += " LIMIT ?"
        params.append(limit)

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                column_names = [column[0] for column in cursor.description]
                results = [dict(zip(column_names, row)) for row in rows]
                return results
        except sqlite3.Error as e:
            logger.error(f"Database error in search_flights: {e}")
            return []

    @tool
    def update_ticket_to_new_flight(
        ticket_no: str, new_flight_id: int, *, config: RunnableConfig
    ) -> str:
        """Update the user's ticket to a new valid flight."""
        configuration = config.get("configurable", {})
        passenger_id = configuration.get("passenger_id", None)
        if not passenger_id:
            raise ValueError("No passenger ID configured.")

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Check if new flight exists
                cursor.execute(
                    "SELECT departure_airport, arrival_airport, scheduled_departure FROM flights WHERE flight_id = ?",
                    (new_flight_id,),
                )
                new_flight = cursor.fetchone()
                if not new_flight:
                    return "Invalid new flight ID provided."

                column_names = [column[0] for column in cursor.description]
                new_flight_dict = dict(zip(column_names, new_flight))

                # Check timing restrictions
                timezone = pytz.timezone("Etc/GMT-3")
                current_time = datetime.now(tz=timezone)
                departure_time = datetime.strptime(
                    new_flight_dict["scheduled_departure"], "%Y-%m-%d %H:%M:%S.%f%z"
                )
                time_until = (departure_time - current_time).total_seconds()
                if time_until < (3 * 3600):
                    return f"""No se permite re agendar el vuelo con menos de 3 horas de la salida.
                            El vuelo seleccionado sale a las {departure_time}."""

                # Check if ticket exists
                cursor.execute(
                    "SELECT flight_id FROM ticket_flights WHERE ticket_no = ?",
                    (ticket_no,),
                )
                current_flight = cursor.fetchone()
                if not current_flight:
                    return "No existen tickets para el número de ticket proporcionado."

                # Check if user owns the ticket
                cursor.execute(
                    "SELECT * FROM tickets WHERE ticket_no = ? AND passenger_id = ?",
                    (ticket_no, passenger_id),
                )
                current_ticket = cursor.fetchone()
                if not current_ticket:
                    return f"El pasajero con ID {passenger_id} no es el dueño del ticket {ticket_no}"

                # Update the ticket
                cursor.execute(
                    "UPDATE ticket_flights SET flight_id = ? WHERE ticket_no = ?",
                    (new_flight_id, ticket_no),
                )
                conn.commit()

                return "Ticket actualizado exitosamente al nuevo vuelo."

        except sqlite3.Error as e:
            logger.error(f"Database error in update_ticket_to_new_flight: {e}")
            return f"Error updating ticket: {str(e)}"

    @tool
    def cancel_ticket(ticket_no: str, *, config: RunnableConfig) -> str:
        """Cancel the user's ticket and remove it from the database."""
        configuration = config.get("configurable", {})
        passenger_id = configuration.get("passenger_id", None)
        if not passenger_id:
            raise ValueError("No passenger ID configured.")

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Check if ticket exists
                cursor.execute(
                    "SELECT flight_id FROM ticket_flights WHERE ticket_no = ?",
                    (ticket_no,),
                )
                existing_ticket = cursor.fetchone()
                if not existing_ticket:
                    return "No existen tickets para el número de ticket proporcionado."

                # Check if user owns the ticket
                cursor.execute(
                    "SELECT ticket_no FROM tickets WHERE ticket_no = ? AND passenger_id = ?",
                    (ticket_no, passenger_id),
                )
                current_ticket = cursor.fetchone()
                if not current_ticket:
                    return f"El pasajero con ID {passenger_id} no es dueño del ticket numero {ticket_no}"

                # Delete the ticket
                cursor.execute(
                    "DELETE FROM ticket_flights WHERE ticket_no = ?", (ticket_no,)
                )
                conn.commit()

                return "Ticket successfully cancelled."

        except sqlite3.Error as e:
            logger.error(f"Database error in cancel_ticket: {e}")
            return f"Error cancelling ticket: {str(e)}"

    return [
        fetch_user_flight_information,
        search_flights,
        update_ticket_to_new_flight,
        cancel_ticket,
    ]
