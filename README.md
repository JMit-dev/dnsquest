# DNSQuest

A lightweight, iterative DNS resolver built in Python that mimics the functionality of the `dig` command. DNSQuest performs DNS resolution by querying root servers, TLD servers, and authoritative nameservers step-by-step, giving you complete visibility into the DNS resolution process.

## Build Status

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/build-passing-brightgreen)

## Code Style

This project follows Python's PEP 8 style guidelines.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Tech/Framework Used

**Built with:**
- Python 3.8+
- dnspython library

**Key Technologies:**
- DNS Protocol (RFC 1035)
- Iterative DNS Resolution
- UDP Socket Communication

## Features

What makes DNSQuest stand out:

- **Iterative Resolution**: Performs complete iterative DNS resolution starting from root servers
- **CNAME Following**: Automatically follows CNAME records to resolve final IP addresses
- **Comprehensive Error Handling**: Differentiates between NXDOMAIN, timeouts, and missing records
- **Performance Metrics**: Shows query time in milliseconds
- **Multiple Root Servers**: Supports all 13 root DNS servers with automatic fallback
- **Clean Output**: Provides dig-like formatted output for easy readability
- **Educational**: Clear code structure for learning DNS resolution internals

## Examples

Example output for successful DNS resolution:

```
QUESTION SECTION:
www.google.com.                  IN      A

ANSWER SECTION:
www.google.com.           300    IN      A       142.250.80.36

Query time: 245 msec
WHEN: Fri Oct 31 14:23:45 2025
```

Example error handling:

```
NXDOMAIN Error: Domain thisdoesnotexist12345.com. does not exist (NXDOMAIN)
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Step-by-step Installation

1. **Clone or download the repository:**
   ```bash
   git clone <repository-url>
   cd dnsquest
   ```

2. **Install required dependencies:**
   ```bash
   pip install dnspython
   ```

3. **Verify installation:**
   ```bash
   python -m dnsquest www.google.com
   ```

### Using a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install dnspython

# Run the program
python -m dnsquest www.example.com
```

## How to Use

### Basic Usage

Resolve a domain name:

```bash
python -m dnsquest www.google.com
```

Or install the package and use as a command:

```bash
pip install -e .
dnsquest www.google.com
```

### Example Queries

1. **Simple domain:**
   ```bash
   python -m dnsquest www.cnn.com
   ```

2. **Domain with CNAME:**
   ```bash
   python -m dnsquest google.co.jp
   ```

3. **Subdomain:**
   ```bash
   python -m dnsquest mail.google.com
   ```

### Understanding the Output

```
QUESTION SECTION:
www.example.com.                 IN      A
```
- Shows the query being made (A record for www.example.com)

```
ANSWER SECTION:
www.example.com.          300    IN      A       93.184.216.34
```
- Shows the resolved IP address (93.184.216.34)
- TTL value (300 seconds)

```
Query time: 245 msec
WHEN: Fri Oct 31 14:23:45 2025
```
- Performance metrics and timestamp

### Error Scenarios

**Non-existent domain:**
```bash
python -m dnsquest thisdoesnotexist12345.com
# Output: NXDOMAIN Error: Domain thisdoesnotexist12345.com. does not exist (NXDOMAIN)
```

**Timeout (unreachable DNS server):**
```bash
# Output: Timeout Error: DNS query timed out for example.com. at server 198.41.0.4
```

**No A record:**
```bash
# Output: No Record Error: No A record found for example.com.
```

## Tests

### Manual Testing

Test with known working domains:

```bash
# Test basic resolution
python -m dnsquest www.google.com

# Test CNAME following
python -m dnsquest google.co.jp

# Test NXDOMAIN
python -m dnsquest thisdoesnotexist12345.com

# Test various TLDs
python -m dnsquest www.bbc.co.uk
python -m dnsquest www.tokyo.jp
```

### Expected Results

| Domain | Expected Result |
|--------|----------------|
| www.google.com | Valid IP address |
| google.co.jp | CNAME → IP resolution |
| thisdoesnotexist12345.com | NXDOMAIN Error |
| www.github.com | Valid IP address |

### Performance Testing

Compare DNSQuest with system dig:

```bash
# DNSQuest
time python -m dnsquest www.example.com

# System dig (for comparison)
dig www.example.com
```

## Network Requirements

### Firewall Considerations

DNSQuest requires outbound UDP access on port 53 to DNS servers. If running on a university or corporate network:

- Ensure UDP port 53 is not blocked
- You may need to use a VPN if the network blocks root server access
- Some VPNs (like Tunnel Bear) may interfere with iterative resolution

### Root Servers

DNSQuest uses the following root DNS servers:
- a.root-servers.net (198.41.0.4)
- b.root-servers.net (170.247.170.2)
- c.root-servers.net (192.33.4.12)
- And 10 more root servers for redundancy

## Contribute

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes and commit:**
   ```bash
   git commit -m "Add amazing feature"
   ```
4. **Push to your branch:**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Contribution Ideas

- Add support for other record types (AAAA, MX, TXT, etc.)
- Implement DNS caching
- Add verbose/debug mode
- Create unit tests
- Add IPv6 support
- Implement DNSSEC validation
- Add JSON output format

## Credits

- **dnspython library**: [rthalley/dnspython](https://github.com/rthalley/dnspython) - DNS toolkit for Python
- **RFC 1035**: [Domain Names - Implementation and Specification](https://www.ietf.org/rfc/rfc1035.txt)
- **IANA Root Servers**: [Root Server Technical Operations](https://www.iana.org/domains/root/servers)

Inspired by the classic UNIX `dig` tool and the need for a simple, educational DNS resolver.

## License

GPL 3.0
