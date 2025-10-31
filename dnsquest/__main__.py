#!/usr/bin/env python3

import sys
from .resolver import (
    DNSQuestResolver,
    DNSResolutionError,
    NXDomainError,
    TimeoutError,
    NoRecordError,
)


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m dnsquest <domain>")
        print("   or: dnsquest <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    resolver = DNSQuestResolver()

    try:
        response = resolver.resolve(domain)
        print(resolver.format_output(domain, response))
    except NXDomainError as e:
        print(f"NXDOMAIN Error: {e}")
        sys.exit(1)
    except TimeoutError as e:
        print(f"Timeout Error: {e}")
        sys.exit(1)
    except NoRecordError as e:
        print(f"No Record Error: {e}")
        sys.exit(1)
    except DNSResolutionError as e:
        print(f"DNS Resolution Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
