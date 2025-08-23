"""Tests for AI SDK utility functions."""

import asyncio
import json
import os
import pytest
import tempfile
from unittest.mock import patch

from src.ai_sdk.utils.api_key import load_api_key, load_optional_setting
from src.ai_sdk.utils.delay import delay
from src.ai_sdk.utils.dict_utils import remove_none_entries, merge_dicts
from src.ai_sdk.utils.headers import combine_headers, clean_headers
from src.ai_sdk.utils.id_generator import create_id_generator, generate_id
from src.ai_sdk.utils.secure_json import secure_json_parse
from src.ai_sdk.errors.base import LoadAPIKeyError


class TestIdGenerator:
    """Test ID generation utilities."""
    
    def test_generate_id_default(self):
        """Test default ID generation."""
        id1 = generate_id()
        id2 = generate_id()
        
        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert len(id1) == 16
        assert len(id2) == 16
        assert id1 != id2  # Should be different
    
    def test_create_id_generator_with_prefix(self):
        """Test ID generator with custom prefix."""
        generator = create_id_generator(prefix="test", size=8)
        
        id1 = generator()
        id2 = generator()
        
        assert id1.startswith("test-")
        assert id2.startswith("test-")
        assert len(id1) == len("test-") + 8
        assert id1 != id2
    
    def test_create_id_generator_custom_alphabet(self):
        """Test ID generator with custom alphabet."""
        generator = create_id_generator(alphabet="ABC", size=4)
        
        id1 = generator()
        
        assert len(id1) == 4
        assert all(c in "ABC" for c in id1)
    
    def test_create_id_generator_invalid_separator(self):
        """Test ID generator with separator in alphabet."""
        with pytest.raises(Exception):  # Should raise InvalidArgumentError
            create_id_generator(prefix="test", alphabet="ABC-", separator="-")


class TestApiKey:
    """Test API key loading utilities."""
    
    def test_load_api_key_direct(self):
        """Test loading API key from direct parameter."""
        api_key = load_api_key("test-key", "TEST_ENV", description="Test")
        assert api_key == "test-key"
    
    def test_load_api_key_environment(self):
        """Test loading API key from environment variable."""
        with patch.dict(os.environ, {"TEST_KEY": "env-test-key"}):
            api_key = load_api_key(None, "TEST_KEY", description="Test")
            assert api_key == "env-test-key"
    
    def test_load_api_key_missing(self):
        """Test error when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(LoadAPIKeyError) as exc_info:
                load_api_key(None, "MISSING_KEY", description="Test")
            
            assert "Test API key is missing" in str(exc_info.value)
    
    def test_load_optional_setting(self):
        """Test loading optional settings."""
        # Direct value
        assert load_optional_setting("direct", "ENV_VAR") == "direct"
        
        # Environment variable
        with patch.dict(os.environ, {"OPT_VAR": "env-value"}):
            assert load_optional_setting(None, "OPT_VAR") == "env-value"
        
        # Missing (should return None)
        with patch.dict(os.environ, {}, clear=True):
            assert load_optional_setting(None, "MISSING") is None


class TestHeaders:
    """Test header manipulation utilities."""
    
    def test_combine_headers(self):
        """Test combining multiple header dictionaries."""
        headers1 = {"Accept": "application/json", "User-Agent": "test"}
        headers2 = {"Authorization": "Bearer token", "Accept": "application/xml"}
        headers3 = None
        
        combined = combine_headers(headers1, headers2, headers3)
        
        expected = {
            "Accept": "application/xml",  # Last one wins
            "User-Agent": "test",
            "Authorization": "Bearer token",
        }
        
        assert combined == expected
    
    def test_clean_headers(self):
        """Test cleaning headers with None values."""
        headers = {
            "Accept": "application/json",
            "Authorization": None,
            "User-Agent": "test",
            "Custom": None,
        }
        
        cleaned = clean_headers(headers)
        
        expected = {
            "Accept": "application/json",
            "User-Agent": "test",
        }
        
        assert cleaned == expected


class TestDictUtils:
    """Test dictionary manipulation utilities."""
    
    def test_remove_none_entries(self):
        """Test removing None values from dictionary."""
        data = {
            "name": "test",
            "value": None,
            "count": 42,
            "optional": None,
        }
        
        cleaned = remove_none_entries(data)
        
        expected = {
            "name": "test",
            "count": 42,
        }
        
        assert cleaned == expected
    
    def test_merge_dicts(self):
        """Test merging multiple dictionaries."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        dict3 = None
        dict4 = {"d": 5}
        
        merged = merge_dicts(dict1, dict2, dict3, dict4)
        
        expected = {"a": 1, "b": 3, "c": 4, "d": 5}
        assert merged == expected


class TestSecureJson:
    """Test secure JSON parsing utilities."""
    
    def test_secure_json_parse_normal(self):
        """Test parsing normal JSON."""
        data = {"name": "test", "count": 42}
        json_str = json.dumps(data)
        
        parsed = secure_json_parse(json_str)
        assert parsed == data
    
    def test_secure_json_parse_primitive(self):
        """Test parsing primitive values."""
        assert secure_json_parse("42") == 42
        assert secure_json_parse('"test"') == "test"
        assert secure_json_parse("null") is None
        assert secure_json_parse("true") is True
    
    def test_secure_json_parse_proto_pollution(self):
        """Test blocking prototype pollution."""
        malicious_json = '{"__proto__": {"polluted": true}}'
        
        with pytest.raises(SyntaxError) as exc_info:
            secure_json_parse(malicious_json)
        
        assert "forbidden prototype property" in str(exc_info.value)
    
    def test_secure_json_parse_constructor_pollution(self):
        """Test blocking constructor pollution."""
        malicious_json = '{"constructor": {"prototype": {"polluted": true}}}'
        
        with pytest.raises(SyntaxError) as exc_info:
            secure_json_parse(malicious_json)
        
        assert "forbidden prototype property" in str(exc_info.value)


class TestDelay:
    """Test delay utilities."""
    
    @pytest.mark.asyncio
    async def test_delay_none(self):
        """Test delay with None (should return immediately)."""
        start_time = asyncio.get_event_loop().time()
        await delay(None)
        end_time = asyncio.get_event_loop().time()
        
        # Should complete almost instantly
        assert end_time - start_time < 0.1
    
    @pytest.mark.asyncio
    async def test_delay_normal(self):
        """Test normal delay."""
        start_time = asyncio.get_event_loop().time()
        await delay(100)  # 100ms
        end_time = asyncio.get_event_loop().time()
        
        # Should take at least 0.1 seconds
        assert end_time - start_time >= 0.09
    
    @pytest.mark.asyncio
    async def test_delay_with_cancellation(self):
        """Test delay with cancellation."""
        cancel_event = asyncio.Event()
        
        # Start delay task
        delay_task = asyncio.create_task(delay(1000, cancel_event=cancel_event))
        
        # Cancel after short delay
        asyncio.create_task(self._cancel_after_delay(cancel_event, 50))
        
        start_time = asyncio.get_event_loop().time()
        
        with pytest.raises(asyncio.CancelledError):
            await delay_task
        
        end_time = asyncio.get_event_loop().time()
        
        # Should complete quickly (within ~100ms)
        assert end_time - start_time < 0.2
    
    async def _cancel_after_delay(self, cancel_event: asyncio.Event, delay_ms: int):
        """Helper to cancel event after delay."""
        await asyncio.sleep(delay_ms / 1000.0)
        cancel_event.set()


if __name__ == "__main__":
    pytest.main([__file__])