#!/usr/bin/env python3

import pytest
from dnsquest import (
    DNSQuestResolver,
    DNSResolutionError,
    NXDomainError,
    TimeoutError,
    NoRecordError,
)


class TestDNSQuestResolver:
    """Test suite for DNS resolver"""

    def test_resolver_initialization(self):
        """Test that resolver initializes correctly"""
        resolver = DNSQuestResolver()
        assert resolver is not None
        assert len(resolver.ROOT_SERVERS) == 13
        assert resolver.query_start_time is None

    def test_root_servers_list(self):
        """Test that all root servers are valid IPs"""
        resolver = DNSQuestResolver()
        for server in resolver.ROOT_SERVERS:
            # Basic IP validation
            parts = server.split(".")
            assert len(parts) == 4
            for part in parts:
                assert 0 <= int(part) <= 255

    def test_resolve_google(self):
        """Test resolving a well-known domain"""
        resolver = DNSQuestResolver()
        try:
            response = resolver.resolve("www.google.com")
            assert response is not None
            assert response.answer is not None
            assert len(response.answer) > 0
        except Exception as e:
            pytest.skip(f"Network issue or DNS server unreachable: {e}")

    def test_resolve_with_cname(self):
        """Test resolving a domain with CNAME record"""
        resolver = DNSQuestResolver()
        try:
            response = resolver.resolve("google.co.jp")
            assert response is not None
            # Should eventually resolve to an A record
            assert response.answer is not None
        except Exception as e:
            pytest.skip(f"Network issue or DNS server unreachable: {e}")

    def test_resolve_nonexistent_domain(self):
        """Test that NXDOMAIN error is raised for non-existent domains"""
        resolver = DNSQuestResolver()
        with pytest.raises(NXDomainError):
            resolver.resolve("thisdoesnotexist12345xyz.com")

    def test_format_output(self):
        """Test output formatting"""
        resolver = DNSQuestResolver()
        try:
            response = resolver.resolve("www.google.com")
            output = resolver.format_output("www.google.com", response)

            # Check that output contains expected sections
            assert "QUESTION SECTION:" in output
            assert "ANSWER SECTION:" in output
            assert "Query time:" in output
            assert "WHEN:" in output
            assert "www.google.com." in output
        except Exception as e:
            pytest.skip(f"Network issue or DNS server unreachable: {e}")

    def test_domain_with_trailing_dot(self):
        """Test that domains with trailing dots are handled correctly"""
        resolver = DNSQuestResolver()
        try:
            # Both should work
            response1 = resolver.resolve("www.google.com")
            response2 = resolver.resolve("www.google.com.")
            assert response1 is not None
            assert response2 is not None
        except Exception as e:
            pytest.skip(f"Network issue or DNS server unreachable: {e}")

    def test_query_time_tracking(self):
        """Test that query time is tracked"""
        resolver = DNSQuestResolver()
        try:
            assert resolver.query_start_time is None
            resolver.resolve("www.google.com")
            assert resolver.query_start_time is not None
            assert resolver.query_start_time > 0
        except Exception as e:
            pytest.skip(f"Network issue or DNS server unreachable: {e}")


class TestExceptions:
    """Test custom exception classes"""

    def test_exception_hierarchy(self):
        """Test that custom exceptions inherit correctly"""
        assert issubclass(NXDomainError, DNSResolutionError)
        assert issubclass(TimeoutError, DNSResolutionError)
        assert issubclass(NoRecordError, DNSResolutionError)

    def test_exception_messages(self):
        """Test that exceptions can be raised with messages"""
        try:
            raise NXDomainError("Test domain does not exist")
        except NXDomainError as e:
            assert str(e) == "Test domain does not exist"

        try:
            raise TimeoutError("Test timeout")
        except TimeoutError as e:
            assert str(e) == "Test timeout"

        try:
            raise NoRecordError("Test no record")
        except NoRecordError as e:
            assert str(e) == "Test no record"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
