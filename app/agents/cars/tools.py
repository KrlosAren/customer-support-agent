from datetime import date, datetime
from typing import Callable, Optional, Union
import sqlite3
from langchain_core.tools import tool
from app.utils.logger import get_logger

logger = get_logger(name=__name__)


def create_cars_booking_tools(db_path: str) -> list[Callable]:
    """Create a tool to manage car rentals."""

    @tool
    def search_car_rentals(
        location: Optional[str] = None,
        name: Optional[str] = None,
        price_tier: Optional[str] = None,
        start_date: Optional[Union[datetime, date]] = None,
        end_date: Optional[Union[datetime, date]] = None,
    ) -> list[dict]:
        """
        Search for car rentals based on location, name, price tier, start date, and end date.

        Args:
            location (Optional[str]): The location of the car rental. Defaults to None.
            name (Optional[str]): The name of the car rental company. Defaults to None.
            price_tier (Optional[str]): The price tier of the car rental. Defaults to None.
            start_date (Optional[Union[datetime, date]]): The start date of the car rental. Defaults to None.
            end_date (Optional[Union[datetime, date]]): The end date of the car rental. Defaults to None.

        Returns:
            list[dict]: A list of car rental dictionaries matching the search criteria.
        """
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM car_rentals WHERE 1=1"
                params = []

                if location:
                    query += " AND location LIKE ?"
                    params.append(f"%{location}%")
                if name:
                    query += " AND name LIKE ?"
                    params.append(f"%{name}%")
                if price_tier:
                    query += " AND price_tier LIKE ?"
                    params.append(f"%{price_tier}%")
                if start_date:
                    query += " AND start_date >= ?"
                    params.append(start_date)
                if end_date:
                    query += " AND end_date <= ?"
                    params.append(end_date)

                cursor.execute(query, params)
                results = cursor.fetchall()

                return [
                    dict(zip([column[0] for column in cursor.description], row))
                    for row in results
                ]
        except sqlite3.Error as e:
            logger.error(f"Database error in search_car_rentals: {e}")
            return []

    @tool
    def book_car_rental(rental_id: int) -> str:
        """
        Book a car rental by its ID.

        Args:
            rental_id (int): The ID of the car rental to book.

        Returns:
            str: A message indicating whether the car rental was successfully booked or not.
        """
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "UPDATE car_rentals SET booked = 1 WHERE id = ?", (rental_id,)
                )
                conn.commit()

                if cursor.rowcount > 0:
                    return f"Car rental {rental_id} successfully booked."
                else:
                    return f"No car rental found with ID {rental_id}."
        except sqlite3.Error as e:
            logger.error(f"Database error in book_car_rental: {e}")
            return f"Error booking car rental: {str(e)}"

    @tool
    def update_car_rental(
        rental_id: int,
        start_date: Optional[Union[datetime, date]] = None,
        end_date: Optional[Union[datetime, date]] = None,
    ) -> str:
        """
        Update a car rental's start and end dates by its ID.

        Args:
            rental_id (int): The ID of the car rental to update.
            start_date (Optional[Union[datetime, date]]): The new start date of the car rental. Defaults to None.
            end_date (Optional[Union[datetime, date]]): The new end date of the car rental. Defaults to None.

        Returns:
            str: A message indicating whether the car rental was successfully updated or not.
        """
        if not start_date and not end_date:
            return "At least one date (start_date or end_date) must be provided for update."

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                updates = []
                params = []

                if start_date:
                    updates.append("start_date = ?")
                    params.append(start_date)
                if end_date:
                    updates.append("end_date = ?")
                    params.append(end_date)

                params.append(rental_id)

                query = f"UPDATE car_rentals SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                conn.commit()

                if cursor.rowcount > 0:
                    return f"Car rental {rental_id} successfully updated."
                else:
                    return f"No car rental found with ID {rental_id}."
        except sqlite3.Error as e:
            logger.error(f"Database error in update_car_rental: {e}")
            return f"Error updating car rental: {str(e)}"

    @tool
    def cancel_car_rental(rental_id: int) -> str:
        """
        Cancel a car rental by its ID.

        Args:
            rental_id (int): The ID of the car rental to cancel.

        Returns:
            str: A message indicating whether the car rental was successfully cancelled or not.
        """
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "UPDATE car_rentals SET booked = 0 WHERE id = ?", (rental_id,)
                )
                conn.commit()

                if cursor.rowcount > 0:
                    return f"Car rental {rental_id} successfully cancelled."
                else:
                    return f"No car rental found with ID {rental_id}."
        except sqlite3.Error as e:
            logger.error(f"Database error in cancel_car_rental: {e}")
            return f"Error cancelling car rental: {str(e)}"

    return [
        search_car_rentals,
        book_car_rental,
        update_car_rental,
        cancel_car_rental,
    ]
