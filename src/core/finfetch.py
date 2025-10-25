"""
Main FinFetch class for orchestrating financial data collection and processing.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
import pandas as pd

from .data_models import FinancialData, DataSource, ProcessingResult
from ..sources.base import BaseDataSource
from ..processors.base import BaseProcessor
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FinFetch:
    """
    Main class for orchestrating financial data collection and processing.
    
    This class provides a unified interface for:
    - Adding and managing data sources
    - Collecting data from multiple sources
    - Processing and aggregating collected data
    - Managing data validation and quality
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize FinFetch instance.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.data_sources: List[BaseDataSource] = []
        self.processors: List[BaseProcessor] = []
        self.logger = logger
        
    def add_source(self, source: BaseDataSource) -> None:
        """
        Add a data source to the collection.
        
        Args:
            source: Data source instance implementing BaseDataSource
        """
        if not isinstance(source, BaseDataSource):
            raise ValueError("Source must implement BaseDataSource interface")
        
        self.data_sources.append(source)
        self.logger.info(f"Added data source: {source.name}")
        
    def add_processor(self, processor: BaseProcessor) -> None:
        """
        Add a data processor to the pipeline.
        
        Args:
            processor: Data processor instance implementing BaseProcessor
        """
        if not isinstance(processor, BaseProcessor):
            raise ValueError("Processor must implement BaseProcessor interface")
            
        self.processors.append(processor)
        self.logger.info(f"Added data processor: {processor.name}")
        
    async def collect_data(
        self,
        symbols: List[str],
        start_date: Union[str, datetime, date],
        end_date: Union[str, datetime, date],
        **kwargs
    ) -> Dict[str, FinancialData]:
        """
        Collect data from all configured sources.
        
        Args:
            symbols: List of financial symbols to collect
            start_date: Start date for data collection
            end_date: End date for data collection
            **kwargs: Additional parameters for data sources
            
        Returns:
            Dictionary mapping symbols to FinancialData objects
        """
        if not self.data_sources:
            raise ValueError("No data sources configured")
            
        self.logger.info(f"Starting data collection for {len(symbols)} symbols")
        
        # Collect data from all sources concurrently
        collection_tasks = []
        for source in self.data_sources:
            task = self._collect_from_source(source, symbols, start_date, end_date, **kwargs)
            collection_tasks.append(task)
            
        # Wait for all collections to complete
        results = await asyncio.gather(*collection_tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        collected_data = {}
        for i, result in enumerate(results):
            source = self.data_sources[i]
            if isinstance(result, Exception):
                self.logger.error(f"Error collecting from {source.name}: {result}")
                continue
                
            # Merge data from this source
            for symbol, data in result.items():
                if symbol not in collected_data:
                    collected_data[symbol] = FinancialData(symbol=symbol)
                collected_data[symbol].merge_data(data, source.name)
                
        self.logger.info(f"Data collection completed for {len(collected_data)} symbols")
        return collected_data
        
    async def _collect_from_source(
        self,
        source: BaseDataSource,
        symbols: List[str],
        start_date: Union[str, datetime, date],
        end_date: Union[str, datetime, date],
        **kwargs
    ) -> Dict[str, FinancialData]:
        """Collect data from a single source."""
        try:
            return await source.collect_data(symbols, start_date, end_date, **kwargs)
        except Exception as e:
            self.logger.error(f"Error in {source.name}: {e}")
            raise
            
    def process_data(self, data: Dict[str, FinancialData]) -> ProcessingResult:
        """
        Process collected data using configured processors.
        
        Args:
            data: Dictionary of collected financial data
            
        Returns:
            ProcessingResult containing processed data and metadata
        """
        if not self.processors:
            self.logger.warning("No processors configured, returning raw data")
            return ProcessingResult(
                data=data,
                metadata={"processing_applied": False}
            )
            
        self.logger.info(f"Processing data with {len(self.processors)} processors")
        
        processed_data = data.copy()
        processing_metadata = {"processors_applied": []}
        
        for processor in self.processors:
            try:
                processed_data = processor.process(processed_data)
                processing_metadata["processors_applied"].append(processor.name)
                self.logger.info(f"Applied processor: {processor.name}")
            except Exception as e:
                self.logger.error(f"Error in processor {processor.name}: {e}")
                processing_metadata["errors"] = processing_metadata.get("errors", [])
                processing_metadata["errors"].append({
                    "processor": processor.name,
                    "error": str(e)
                })
                
        return ProcessingResult(
            data=processed_data,
            metadata=processing_metadata
        )
        
    def get_available_sources(self) -> List[str]:
        """Get list of available data source names."""
        return [source.name for source in self.data_sources]
        
    def get_available_processors(self) -> List[str]:
        """Get list of available processor names."""
        return [processor.name for processor in self.processors]
        
    def validate_configuration(self) -> bool:
        """
        Validate the current configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.data_sources:
            self.logger.error("No data sources configured")
            return False
            
        # Validate each data source
        for source in self.data_sources:
            if not source.validate():
                self.logger.error(f"Data source {source.name} is not valid")
                return False
                
        return True
