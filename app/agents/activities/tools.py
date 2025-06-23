from typing import Callable, Optional
import sqlite3
from langchain_core.tools import tool
from app.utils.logger import get_logger

logger = get_logger(name=__name__)


def create_activities_tools(db_path: str) -> list[Callable]:
    """Create a tool to manage trip recommendations."""

    @tool
    def search_trip_recommendations(
        location: Optional[str] = None,
        name: Optional[str] = None,
        keywords: Optional[str] = None,
    ) -> list[dict]:
        """
        Search for trip recommendations based on location, name, and keywords.

        Args:
            location (Optional[str]): The location of the trip recommendation. Defaults to None.
            name (Optional[str]): The name of the trip recommendation. Defaults to None.
            keywords (Optional[str]): The keywords associated with the trip recommendation. Defaults to None.

        Returns:
            list[dict]: A list of trip recommendation dictionaries matching the search criteria.
        """
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM trip_recommendations WHERE 1=1"
                params = []

                if location:
                    query += " AND location LIKE ?"
                    params.append(f"%{location}%")
                if name:
                    query += " AND name LIKE ?"
                    params.append(f"%{name}%")
                if keywords:
                    keyword_list = keywords.split(",")
                    keyword_conditions = " OR ".join(
                        ["keywords LIKE ?" for _ in keyword_list]
                    )
                    query += f" AND ({keyword_conditions})"
                    params.extend([f"%{keyword.strip()}%" for keyword in keyword_list])

                cursor.execute(query, params)
                results = cursor.fetchall()

                return [
                    dict(zip([column[0] for column in cursor.description], row))
                    for row in results
                ]
        except sqlite3.Error as e:
            logger.error(f"Database error in search_trip_recommendations: {e}")
            return []

    @tool
    def book_excursion(recommendation_id: int) -> str:
        """
        Book an excursion by its recommendation ID.

        Args:
            recommendation_id (int): The ID of the trip recommendation to book.

        Returns:
            str: A message indicating whether the trip recommendation was successfully booked or not.
        """
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "UPDATE trip_recommendations SET booked = 1 WHERE id = ?",
                    (recommendation_id,),
                )
                conn.commit()

                if cursor.rowcount > 0:
                    return (
                        f"Trip recommendation {recommendation_id} successfully booked."
                    )
                else:
                    return f"No trip recommendation found with ID {recommendation_id}."
        except sqlite3.Error as e:
            logger.error(f"Database error in book_excursion: {e}")
            return f"Error booking excursion: {str(e)}"

    @tool
    def update_excursion(recommendation_id: int, details: str) -> str:
        """
        Update a trip recommendation's details by its ID.

        Args:
            recommendation_id (int): The ID of the trip recommendation to update.
            details (str): The new details of the trip recommendation.

        Returns:
            str: A message indicating whether the trip recommendation was successfully updated or not.
        """
        if not details:
            return "Details must be provided for update."

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "UPDATE trip_recommendations SET details = ? WHERE id = ?",
                    (details, recommendation_id),
                )
                conn.commit()

                if cursor.rowcount > 0:
                    return (
                        f"Trip recommendation {recommendation_id} successfully updated."
                    )
                else:
                    return f"No trip recommendation found with ID {recommendation_id}."
        except sqlite3.Error as e:
            logger.error(f"Database error in update_excursion: {e}")
            return f"Error updating excursion: {str(e)}"

    @tool
    def cancel_excursion(recommendation_id: int) -> str:
        """
        Cancel a trip recommendation by its ID.

        Args:
            recommendation_id (int): The ID of the trip recommendation to cancel.

        Returns:
            str: A message indicating whether the trip recommendation was successfully cancelled or not.
        """
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "UPDATE trip_recommendations SET booked = 0 WHERE id = ?",
                    (recommendation_id,),
                )
                conn.commit()

                if cursor.rowcount > 0:
                    return f"Trip recommendation {recommendation_id} successfully cancelled."
                else:
                    return f"No trip recommendation found with ID {recommendation_id}."
        except sqlite3.Error as e:
            logger.error(f"Database error in cancel_excursion: {e}")
            return f"Error cancelling excursion: {str(e)}"

    return [
        search_trip_recommendations,
        book_excursion,
        update_excursion,
        cancel_excursion,
    ]
