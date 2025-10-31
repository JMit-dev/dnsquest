#!/usr/bin/env python3

import time
import datetime
import dns.query
import dns.message
import dns.rdatatype
import dns.rdataclass
import dns.name
import dns.exception


class DNSResolutionError(Exception):
    """Base exception for DNS resolution errors"""

    pass


class NXDomainError(DNSResolutionError):
    """Domain does not exist"""

    pass


class TimeoutError(DNSResolutionError):
    """DNS query timed out"""

    pass


class NoRecordError(DNSResolutionError):
    """No A or NS record found"""

    pass


class DNSQuestResolver:
    ROOT_SERVERS = [
        "198.41.0.4",  # a.root-servers.net
        "170.247.170.2",  # b.root-servers.net
        "192.33.4.12",  # c.root-servers.net
        "199.7.91.13",  # d.root-servers.net
        "192.203.230.10",  # e.root-servers.net
        "192.5.5.241",  # f.root-servers.net
        "192.112.36.4",  # g.root-servers.net
        "198.97.190.53",  # h.root-servers.net
        "192.36.148.17",  # i.root-servers.net
        "192.58.128.30",  # j.root-servers.net
        "193.0.14.129",  # k.root-servers.net
        "199.7.83.42",  # l.root-servers.net
        "202.12.27.33",  # m.root-servers.net
    ]

    def __init__(self):
        self.query_start_time = None

    def resolve(self, domain):
        self.query_start_time = time.time()

        if not domain.endswith("."):
            domain += "."

        domain_name = dns.name.from_text(domain)

        try:
            final_answer = self._iterative_resolve(
                domain_name, dns.rdatatype.A, self.ROOT_SERVERS
            )
            return final_answer
        except (NXDomainError, TimeoutError, NoRecordError) as e:
            # Re-raise specific DNS errors
            raise
        except Exception as e:
            raise DNSResolutionError(f"Failed to resolve {domain}: {str(e)}")

    def _iterative_resolve(self, qname, qtype, nameservers):
        last_timeout_error = None
        successful_responses = 0

        for ns in nameservers:
            try:
                query = dns.message.make_query(qname, qtype, dns.rdataclass.IN)
                response = dns.query.udp(query, ns, timeout=5)
                successful_responses += 1

                # Check for NXDOMAIN (domain does not exist)
                if response.rcode() == dns.rcode.NXDOMAIN:
                    raise NXDomainError(f"Domain {qname} does not exist (NXDOMAIN)")

                # Check if we got an answer
                if response.answer:
                    for rrset in response.answer:
                        if rrset.rdtype == dns.rdatatype.CNAME:
                            cname_target = rrset[0].target
                            return self._iterative_resolve(
                                cname_target, qtype, self.ROOT_SERVERS
                            )
                        elif rrset.rdtype == qtype:
                            return response

                # Try to follow additional records (glue records)
                if response.additional:
                    next_servers = []
                    for rrset in response.additional:
                        if rrset.rdtype == dns.rdatatype.A:
                            next_servers.extend([rr.address for rr in rrset])

                    if next_servers:
                        return self._iterative_resolve(qname, qtype, next_servers)

                # Try to follow authority records (NS records)
                if response.authority:
                    ns_names = []
                    ns_records_found = False

                    for rrset in response.authority:
                        if rrset.rdtype == dns.rdatatype.NS:
                            ns_records_found = True
                            ns_names.extend([str(rr.target) for rr in rrset])
                        # Check for SOA record which might indicate NXDOMAIN or no such record
                        elif rrset.rdtype == dns.rdatatype.SOA:
                            # SOA without NS could mean the name exists but no A record
                            if not ns_records_found and qtype == dns.rdatatype.A:
                                raise NoRecordError(f"No A record found for {qname}")

                    if ns_names:
                        next_servers = []
                        for ns_name in ns_names:
                            try:
                                ns_response = self._iterative_resolve(
                                    dns.name.from_text(ns_name),
                                    dns.rdatatype.A,
                                    self.ROOT_SERVERS,
                                )
                                if ns_response and ns_response.answer:
                                    for rrset in ns_response.answer:
                                        if rrset.rdtype == dns.rdatatype.A:
                                            next_servers.extend(
                                                [rr.address for rr in rrset]
                                            )
                            except (NXDomainError, TimeoutError, NoRecordError):
                                # If NS resolution fails, try next NS
                                continue
                            except Exception:
                                continue

                        if next_servers:
                            return self._iterative_resolve(qname, qtype, next_servers)
                        else:
                            # We found NS records but couldn't resolve any of them
                            raise NoRecordError(
                                f"Found NS records but could not resolve any nameserver IPs for {qname}"
                            )

                # If we got a response but no answer, additional, or authority with useful info
                # This shouldn't normally happen, try next server

            except dns.exception.Timeout:
                # Save timeout error but try other servers first
                last_timeout_error = TimeoutError(
                    f"DNS query timed out for {qname} at server {ns}"
                )
                continue
            except (NXDomainError, NoRecordError):
                # Re-raise specific DNS errors immediately
                raise
            except Exception as e:
                # Log but continue to next server for other errors
                continue

        # If we tried all servers and got timeouts
        if last_timeout_error and successful_responses == 0:
            raise last_timeout_error

        # If we got responses but no useful records
        if successful_responses > 0:
            raise NoRecordError(f"No A or NS records found for {qname}")

        # All servers failed
        raise DNSResolutionError(
            f"Unable to resolve domain {qname}: all nameservers failed"
        )

    def format_output(self, domain, response):
        if not response or not response.answer:
            return f"No answer found for {domain}"

        if not domain.endswith("."):
            domain += "."

        output = []

        output.append("QUESTION SECTION:")
        output.append(f"{domain:<32} IN      A")
        output.append("")
        output.append("ANSWER SECTION:")

        # Find the final A record IP address
        final_ip = None
        final_ttl = None
        for rrset in response.answer:
            if rrset.rdtype == dns.rdatatype.A:
                for rr in rrset:
                    final_ip = rr.address
                    final_ttl = rrset.ttl
                    break
                break

        if final_ip:
            # Calculate spacing to align IN column with question section
            ttl_str = str(final_ttl)
            spaces_needed = 32 - len(domain) - len(ttl_str) - 3
            output.append(
                f"{domain}{' ' * spaces_needed}{final_ttl}    IN      A       {final_ip}"
            )

        output.append("")
        query_time = int((time.time() - self.query_start_time) * 1000)
        output.append(f"Query time: {query_time} msec")
        current_time = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        output.append(f"WHEN: {current_time}")

        return "\n".join(output)
