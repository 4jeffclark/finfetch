"""
Tests for FinFetch core functionality.

This module contains tests for the core FinFetch classes and functionality.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from finfetch.core.finfetch import FinFetch
from finfetch.core.data_models import FinancialData, DataSource
from finfetch.sources.base import BaseDataSource
from finfetch.processors.base import BaseProcessor


class MockDataSource(BaseDataSource):
    """Mock data source for testing."""
    
    def __init__(self, name: str = "Mock Source"):
        config = DataSource(name=name)
        super().__init__(config)
        
    async def collect_data(self, symbols, start_date, end_date, **kwargs):
        """Mock data collection."""
        results = {}
        for symbol in symbols:
            # Create mock data
            data = Mock()
            data.symbol = symbol
            data.data = Mock()  # Mock DataFrame
            data.metadata = {"source": self.name}
            data.sources = [self.name]
            data.last_updated = datetime.now()
            results[symbol] = data
        return results
        
    def validate(self):
        return True
        
    async def test_connection(self):
        return True


class MockProcessor(BaseProcessor):
    """Mock processor for testing."""
    
    @property
    def name(self):
        return "Mock Processor"
        
    def process(self, data):
        """Mock processing."""
        return data
        
    def validate_config(self):
        return True


class TestFinFetch:
    """Test cases for FinFetch class."""
    
    def test_initialization(self):
        """Test FinFetch initialization."""
        ff = FinFetch()
        assert ff.data_sources == []
        assert ff.processors == []
        
    def test_add_source(self):
        """Test adding data sources."""
        ff = FinFetch()
        source = MockDataSource()
        
        ff.add_source(source)
        assert len(ff.data_sources) == 1
        assert ff.data_sources[0] == source
        
    def test_add_invalid_source(self):
        """Test adding invalid data source."""
        ff = FinFetch()
        
        with pytest.raises(ValueError, match="Source must implement BaseDataSource interface"):
            ff.add_source("invalid_source")
            
    def test_add_processor(self):
        """Test adding processors."""
        ff = FinFetch()
        processor = MockProcessor()
        
        ff.add_processor(processor)
        assert len(ff.processors) == 1
        assert ff.processors[0] == processor
        
    def test_add_invalid_processor(self):
        """Test adding invalid processor."""
        ff = FinFetch()
        
        with pytest.raises(ValueError, match="Processor must implement BaseProcessor interface"):
            ff.add_processor("invalid_processor")
            
    def test_get_available_sources(self):
        """Test getting available sources."""
        ff = FinFetch()
        source1 = MockDataSource("Source 1")
        source2 = MockDataSource("Source 2")
        
        ff.add_source(source1)
        ff.add_source(source2)
        
        sources = ff.get_available_sources()
        assert len(sources) == 2
        assert "Source 1" in sources
        assert "Source 2" in sources
        
    def test_get_available_processors(self):
        """Test getting available processors."""
        ff = FinFetch()
        processor1 = MockProcessor()
        processor2 = MockProcessor()
        
        ff.add_processor(processor1)
        ff.add_processor(processor2)
        
        processors = ff.get_available_processors()
        assert len(processors) == 2
        assert "Mock Processor" in processors
        
    def test_validate_configuration_no_sources(self):
        """Test configuration validation with no sources."""
        ff = FinFetch()
        assert not ff.validate_configuration()
        
    def test_validate_configuration_with_sources(self):
        """Test configuration validation with sources."""
        ff = FinFetch()
        source = MockDataSource()
        ff.add_source(source)
        
        assert ff.validate_configuration()
        
    @pytest.mark.asyncio
    async def test_collect_data_no_sources(self):
        """Test data collection with no sources."""
        ff = FinFetch()
        
        with pytest.raises(ValueError, match="No data sources configured"):
            await ff.collect_data(["AAPL"], "2023-01-01", "2023-12-31")
            
    @pytest.mark.asyncio
    async def test_collect_data_with_sources(self):
        """Test data collection with sources."""
        ff = FinFetch()
        source = MockDataSource()
        ff.add_source(source)
        
        symbols = ["AAPL", "GOOGL"]
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        data = await ff.collect_data(symbols, start_date, end_date)
        
        assert len(data) == 2
        assert "AAPL" in data
        assert "GOOGL" in data
        
    def test_process_data_no_processors(self):
        """Test data processing with no processors."""
        ff = FinFetch()
        
        # Create mock data
        mock_data = {"AAPL": Mock()}
        
        result = ff.process_data(mock_data)
        
        assert result.data == mock_data
        assert result.metadata["processing_applied"] == False
        
    def test_process_data_with_processors(self):
        """Test data processing with processors."""
        ff = FinFetch()
        processor = MockProcessor()
        ff.add_processor(processor)
        
        # Create mock data
        mock_data = {"AAPL": Mock()}
        
        result = ff.process_data(mock_data)
        
        assert result.data == mock_data
        assert "Mock Processor" in result.metadata["processors_applied"]


class TestFinancialData:
    """Test cases for FinancialData class."""
    
    def test_initialization(self):
        """Test FinancialData initialization."""
        symbol = "AAPL"
        data = Mock()  # Mock DataFrame
        metadata = {"source": "test"}
        
        fd = FinancialData(symbol=symbol, data=data, metadata=metadata)
        
        assert fd.symbol == symbol
        assert fd.data == data
        assert fd.metadata == metadata
        assert fd.sources == []
        
    def test_merge_data(self):
        """Test merging data from another source."""
        # Create initial data
        fd1 = FinancialData(symbol="AAPL", data=Mock(), metadata={"source1": "data1"})
        fd1.sources = ["source1"]
        
        # Create data to merge
        fd2 = FinancialData(symbol="AAPL", data=Mock(), metadata={"source2": "data2"})
        fd2.sources = ["source2"]
        
        # Merge data
        fd1.merge_data(fd2, "source2")
        
        assert "source2" in fd1.sources
        assert "source2" in fd1.metadata


class TestDataSource:
    """Test cases for DataSource class."""
    
    def test_initialization(self):
        """Test DataSource initialization."""
        ds = DataSource(
            name="Test Source",
            api_key="test_key",
            base_url="https://api.test.com",
            rate_limit=100,
            timeout=30,
            enabled=True
        )
        
        assert ds.name == "Test Source"
        assert ds.api_key == "test_key"
        assert ds.base_url == "https://api.test.com"
        assert ds.rate_limit == 100
        assert ds.timeout == 30
        assert ds.enabled == True
        
    def test_default_values(self):
        """Test DataSource default values."""
        ds = DataSource(name="Test Source")
        
        assert ds.api_key is None
        assert ds.base_url is None
        assert ds.rate_limit is None
        assert ds.timeout == 30
        assert ds.enabled == True
