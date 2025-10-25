"""
Date and time utilities for FinFetch.

This module provides utilities for parsing, normalizing, and working with
dates in the FinFetch system.
"""

from typing import Union, Optional, Tuple
from datetime import datetime, date, timedelta
import pandas as pd


def parse_date(date_input: Union[str, datetime, date, None]) -> Optional[datetime]:
    """
    Parse various date formats into a datetime object.
    
    Args:
        date_input: Date in various formats (string, datetime, date, or None)
        
    Returns:
        Parsed datetime object or None if input is None
        
    Raises:
        ValueError: If date format is not recognized
    """
    if date_input is None:
        return None
        
    if isinstance(date_input, datetime):
        return date_input
        
    if isinstance(date_input, date):
        return datetime.combine(date_input, datetime.min.time())
        
    if isinstance(date_input, str):
        # Try various date formats
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_input, fmt)
            except ValueError:
                continue
                
        # Try pandas date parsing as fallback
        try:
            return pd.to_datetime(date_input).to_pydatetime()
        except (ValueError, TypeError):
            pass
            
        raise ValueError(f"Unable to parse date: {date_input}")
        
    raise ValueError(f"Unsupported date type: {type(date_input)}")


def normalize_date_range(
    start_date: Union[str, datetime, date, None],
    end_date: Union[str, datetime, date, None],
    default_start_days_ago: int = 365
) -> Tuple[datetime, datetime]:
    """
    Normalize and validate a date range.
    
    Args:
        start_date: Start date (various formats)
        end_date: End date (various formats)
        default_start_days_ago: Default start date if not provided (days ago from today)
        
    Returns:
        Tuple of (start_datetime, end_datetime)
        
    Raises:
        ValueError: If date range is invalid
    """
    # Parse dates
    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)
    
    # Set defaults if not provided
    if start_dt is None:
        start_dt = datetime.now() - timedelta(days=default_start_days_ago)
        
    if end_dt is None:
        end_dt = datetime.now()
        
    # Validate date range
    if start_dt >= end_dt:
        raise ValueError("Start date must be before end date")
        
    # Ensure start date is at beginning of day
    start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Ensure end date is at end of day
    end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return start_dt, end_dt


def get_business_days_between(start_date: datetime, end_date: datetime) -> int:
    """
    Get the number of business days between two dates.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Number of business days between the dates
    """
    return pd.bdate_range(start_date, end_date).size


def is_business_day(date_input: Union[str, datetime, date]) -> bool:
    """
    Check if a date is a business day.
    
    Args:
        date_input: Date to check
        
    Returns:
        True if the date is a business day, False otherwise
    """
    dt = parse_date(date_input)
    if dt is None:
        return False
        
    return dt.weekday() < 5  # Monday = 0, Friday = 4


def get_next_business_day(date_input: Union[str, datetime, date]) -> datetime:
    """
    Get the next business day from a given date.
    
    Args:
        date_input: Starting date
        
    Returns:
        Next business day
    """
    dt = parse_date(date_input)
    if dt is None:
        raise ValueError("Invalid date input")
        
    # Add one day and keep adding until we get a business day
    next_day = dt + timedelta(days=1)
    while not is_business_day(next_day):
        next_day += timedelta(days=1)
        
    return next_day


def get_previous_business_day(date_input: Union[str, datetime, date]) -> datetime:
    """
    Get the previous business day from a given date.
    
    Args:
        date_input: Starting date
        
    Returns:
        Previous business day
    """
    dt = parse_date(date_input)
    if dt is None:
        raise ValueError("Invalid date input")
        
    # Subtract one day and keep subtracting until we get a business day
    prev_day = dt - timedelta(days=1)
    while not is_business_day(prev_day):
        prev_day -= timedelta(days=1)
        
    return prev_day


def format_date_for_api(date_input: Union[str, datetime, date], api_format: str = "iso") -> str:
    """
    Format a date for API consumption.
    
    Args:
        date_input: Date to format
        api_format: Format type ("iso", "unix", "custom")
        
    Returns:
        Formatted date string
    """
    dt = parse_date(date_input)
    if dt is None:
        raise ValueError("Invalid date input")
        
    if api_format == "iso":
        return dt.isoformat()
    elif api_format == "unix":
        return str(int(dt.timestamp()))
    else:
        return dt.strftime(api_format)
