PacketVision - Real tcpdump Educational Framework
Author: SYLHETYHACKVENGER (THE-ERROR808)
ONLY FOR EDUCATIONAL PURPOSES AND RESEARCH
"""

import sys
import time
import subprocess
import shlex
import shutil
import logging
from enum import Enum
from typing import List, Dict, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, IntPrompt
    from rich.text import Text
    from rich.align import Align
    from rich import box
except ImportError:
    print("Rich library not installed. Please run: pip install rich")
    sys.exit(1)

# ------------------------------
# Logging setup (optional)
# ------------------------------
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# ------------------------------
# ASCII Banner - Monster from asciiart.website
# ------------------------------
BANNER = r"""
 ________________________________________________
 |  __ \         | |      | \ \    / (_)
 | |__) |_ _  ___| | _____| |\ \  / / _ ___  ___  _ __
 |  ___/ _` |/ __| |/ / _ \ __\ \/ / | / __|/ _ \| '_ \
 | |  | (_| | (__|   <  __/ |_ \  /  | \__ \ (_) | | | |
 |_|   \__,_|\___|_|\_\___|\__| \/   |_|___/\___/|_| |_|
    PacketVision - Real tcpdump Educational Framework
    Author: SYLHETYHACKVENGER (THE-ERROR808)
    ONLY FOR EDUCATIONAL PURPOSES AND RESEARCH
                                                         """

# ------------------------------
# Enums for categories
# ------------------------------
class Category(Enum):
    INTERFACE = "Interface"
    OUTPUT = "Output"
    ADDRESSING = "Addressing"
    PORT_FILTER = "Port Filter"
    PROTOCOL = "Protocol"
    TCP_FLAGS = "TCP Flags"
    SIZE = "Size"
    LOGIC = "Logic"
    PAYLOAD = "Payload"
    OFFENSIVE = "Offensive"
    DEFENSIVE = "Defensive"
    CAPTURE = "Capture"
    PERFORMANCE = "Performance"
    INFO = "Info"
    MISC = "Misc"

    @classmethod
    def list_names(cls):
        return [cat.value for cat in cls]

# ------------------------------
# TTS (Text-to-Speech) with adjustable speed
# ------------------------------
class TTS:
    @staticmethod
    def speak(text: str, speed: int = 120):
        """
        Speak text using espeak.
        Speed: words per minute (default 120 – slower than the default 175).
        Adjust this value to your preference.
        """
        try:
            subprocess.run(
                ['espeak', '-s', str(speed), text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
                timeout=5
            )
        except FileNotFoundError:
            logging.error("espeak not found. Please install espeak.")
        except subprocess.TimeoutExpired:
            logging.error("espeak timed out.")
        except subprocess.CalledProcessError as e:
            logging.error(f"espeak returned error: {e.returncode}")

# ------------------------------
# Database (filter definitions)
# ------------------------------
class TCPDumpDatabase:
    def __init__(self):
        self.items = self._generate_items()

    @staticmethod
    def _category_consequences(category: Category) -> str:
        """Return the consequences string for a given category."""
        base = "**Causes & Consequences**: "
        mapping = {
            Category.OFFENSIVE: "This filter can capture sensitive information (passwords, tokens, exploits). Running it against a target may expose credentials, reveal vulnerabilities, and violate privacy laws if unauthorized. Only use on systems you own or have explicit permission to test.",
            Category.DEFENSIVE: "This filter helps detect attacks and anomalies. It generates detailed logs, may increase CPU/disk usage, and can alert to threats like ARP spoofing or SMB exploits. No direct harm, but false positives may occur.",
            Category.TCP_FLAGS: "This filter isolates specific TCP control packets, revealing scanning techniques (NULL, FIN, XMAS). Running it may trigger IDS alerts on the target network. Use only with authorization.",
            Category.PORT_FILTER: "Focuses on traffic for a specific service. This can expose application-level data (HTTP requests, SQL queries). If unencrypted, credentials may be captured. May impact performance on high-volume ports.",
            Category.PAYLOAD: "Deep packet inspection – looks for strings or byte patterns (e.g., SQL injection, directory traversal). This is intrusive and may be considered wiretapping; always have written authorization.",
            Category.ADDRESSING: "Filters by IP/MAC addresses. Reveals communication patterns of specific hosts. May expose network topology. Use responsibly to avoid violating user privacy.",
            Category.INTERFACE: "Selects the network interface for capture. Without this, the default interface is used. No inherent risk, but captures all traffic on that interface.",
            Category.OUTPUT: "Controls how packets are displayed or saved. This affects verbosity, timestamps, and file storage. No direct impact on targets, but can produce large files.",
            Category.PROTOCOL: "Filters by protocol (TCP/UDP/ICMP/etc.). Useful for analyzing specific network layers. May reveal protocol-specific vulnerabilities.",
            Category.SIZE: "Filters based on packet length or TTL. Helps detect anomalies (large packets = exfiltration, low TTL = traceroute). Can indicate scanning or tunneling.",
            Category.LOGIC: "Combines multiple filters with AND/OR/NOT. Allows complex rules; can be used to build custom IDS signatures. Overly complex filters may slow down capture.",
            Category.CAPTURE: "Controls capture limits (count, snaplen). Useful for reducing file size or focusing on a number of packets. No inherent risk.",
            Category.PERFORMANCE: "Options that affect performance (buffer size, checksum offload). May improve or degrade capture speed.",
            Category.INFO: "Informational commands (list interfaces, link types). No risk.",
            Category.MISC: "General network visibility. May reveal active hosts, services, and network structure. Use ethically and with proper authorization.",
        }
        return base + mapping.get(category, "General network visibility. May reveal active hosts, services, and network structure. Use ethically and with proper authorization.")

    @staticmethod
    def _category_purpose(category: Category) -> str:
        mapping = {
            Category.OFFENSIVE: "To demonstrate how attackers can intercept sensitive data and identify attack surfaces during authorized penetration tests.",
            Category.DEFENSIVE: "To provide network visibility for blue teams, enabling detection of threats, anomalies, and policy violations.",
            Category.TCP_FLAGS: "To analyze TCP connection states and detect stealth scanning techniques used by attackers.",
            Category.PORT_FILTER: "To isolate traffic for a specific application or service for troubleshooting, monitoring, or security auditing.",
            Category.PAYLOAD: "To inspect application-layer data for specific patterns, such as credentials, injection attempts, or known exploit strings.",
            Category.ADDRESSING: "To focus on traffic to/from particular hosts or networks, reducing noise and targeting specific communication.",
            Category.INTERFACE: "To select the correct network interface for capture, essential when multiple network adapters exist.",
            Category.OUTPUT: "To control the presentation and storage of captured data, making analysis easier or saving evidence.",
            Category.PROTOCOL: "To study the behavior of specific network protocols, debug protocol implementations, or detect protocol abuse.",
            Category.SIZE: "To filter packets based on size or TTL, helping identify anomalies like ping sweeps, OS fingerprinting, or data exfiltration.",
            Category.LOGIC: "To create sophisticated capture rules that match complex traffic patterns for advanced analysis.",
            Category.CAPTURE: "To limit the amount of captured data or adjust capture parameters.",
            Category.PERFORMANCE: "To tune tcpdump for performance in high-traffic environments.",
            Category.INFO: "To obtain information about available interfaces or link-layer types.",
            Category.MISC: "To provide general insight into network traffic.",
        }
        return mapping.get(category, "To provide general insight into network traffic.")

    @staticmethod
    def _category_explanation(category: Category, filt: str) -> str:
        base = f"**What it does**: "
        if category == Category.INTERFACE:
            return base + f"Selects the network interface `{filt}` for capturing packets. Without this, tcpdump picks the first available interface."
        elif category == Category.OUTPUT:
            return base + f"Modifies output behavior: `{filt}`. This can change verbosity, timestamps, hex/ASCII dump, file rotation, etc."
        elif category == Category.ADDRESSING:
            return base + f"Filters packets based on address criteria: `{filt}`. This includes IP, MAC, netmask, broadcast, multicast, and IPv6."
        elif category == Category.PORT_FILTER:
            return base + f"Captures packets with source or destination port `{filt}`. This isolates traffic for a specific application."
        elif category == Category.PROTOCOL:
            return base + f"Selects packets by protocol: `{filt}`. Can also inspect protocol-specific fields like ICMP type."
        elif category == Category.TCP_FLAGS:
            return base + f"Inspects the TCP flags byte. `{filt}` matches specific flag combinations to detect connection establishment, teardown, or scanning."
        elif category == Category.SIZE:
            return base + f"Filters by packet length, TTL, or fragmentation: `{filt}`. Useful for detecting anomalies."
        elif category == Category.LOGIC:
            return base + f"Combines multiple filters using logical operators: `{filt}`. Enables complex expressions."
        elif category == Category.PAYLOAD:
            return base + f"Looks at the actual payload data for hex patterns or strings: `{filt}`. Used for deep packet inspection."
        elif category == Category.OFFENSIVE:
            return base + f"Designed for penetration testing: `{filt}` captures sensitive data or detects attack patterns."
        elif category == Category.DEFENSIVE:
            return base + f"Designed for security monitoring: `{filt}` detects attacks, anomalies, and policy violations."
        else:
            return base + f"General filter: `{filt}` provides specific packet capture capability."

    def _generate_items(self) -> List[Dict]:
        """Build the list of 255 filters with full metadata."""
        items = []
        item_id = 1

        # Helper to create an item dict
        def make_item(filt: str, desc: str, cat: Category):
            nonlocal item_id
            item = {
                "id": item_id,
                "filter": filt,
                "description": desc,
                "category": cat.value,
                "explanation": self._category_explanation(cat, filt),
                "purpose": self._category_purpose(cat),
                "consequences": self._category_consequences(cat)
            }
            items.append(item)
            item_id += 1

        # 1-20: Core switches
        core = [
            ("-i wlan0", "Capture on Wi-Fi", Category.INTERFACE),
            ("-i eth0", "Capture on Ethernet", Category.INTERFACE),
            ("-i lo", "Capture on loopback", Category.INTERFACE),
            ("-w dump.pcap", "Save to file", Category.OUTPUT),
            ("-r dump.pcap", "Read from file", Category.OUTPUT),
            ("-v", "Verbose (level 1)", Category.OUTPUT),
            ("-vv", "Verbose (level 2)", Category.OUTPUT),
            ("-vvv", "Verbose (level 3)", Category.OUTPUT),
            ("-n", "No hostname resolution", Category.OUTPUT),
            ("-nn", "No host/port resolution", Category.OUTPUT),
            ("-N", "Suppress domain qual", Category.OUTPUT),
            ("-t", "Disable timestamps", Category.OUTPUT),
            ("-tt", "Epoch timestamps", Category.OUTPUT),
            ("-ttt", "Delta timestamps", Category.OUTPUT),
            ("-tttt", "Human timestamps", Category.OUTPUT),
            ("-e", "Show MAC headers", Category.OUTPUT),
            ("-X", "Hex + ASCII dump", Category.OUTPUT),
            ("-A", "ASCII dump", Category.OUTPUT),
            ("-c 100", "Stop after 100", Category.CAPTURE),
            ("-s 0", "Full packet capture", Category.CAPTURE),
        ]
        for filt, desc, cat in core:
            make_item(filt, desc, cat)

        # 21-40: Addressing
        addressing = [
            ("host 192.168.1.10", "Filter by IP", Category.ADDRESSING),
            ("host google.com", "Filter by domain", Category.ADDRESSING),
            ("src host 10.0.0.5", "Source IP filter", Category.ADDRESSING),
            ("dst host 10.0.0.5", "Dest IP filter", Category.ADDRESSING),
            ("net 192.168.0.0/24", "Filter by subnet", Category.ADDRESSING),
            ("src net 172.16.0.0/16", "Source subnet", Category.ADDRESSING),
            ("dst net 10.0.0.0/8", "Dest subnet", Category.ADDRESSING),
            ("broadcast", "Broadcast packets", Category.ADDRESSING),
            ("multicast", "Multicast packets", Category.ADDRESSING),
            ("ip multicast", "IPv4 multicast", Category.ADDRESSING),
            ("ip6", "IPv6 traffic", Category.ADDRESSING),
            ("ip6 host ::1", "IPv6 loopback", Category.ADDRESSING),
            ("arp", "ARP packets", Category.ADDRESSING),
            ("rarp", "RARP packets", Category.ADDRESSING),
            ("atalk", "AppleTalk", Category.ADDRESSING),
            ("decnet", "DECnet", Category.ADDRESSING),
            ("iso", "ISO/OSI", Category.ADDRESSING),
            ("stp", "Spanning Tree", Category.ADDRESSING),
            ("vlan", "VLAN tags", Category.ADDRESSING),
            ("mpls", "MPLS labels", Category.ADDRESSING),
        ]
        for filt, desc, cat in addressing:
            make_item(filt, desc, cat)

        # 41-80: Port filters
        ports = [
            (21, "FTP"), (22, "SSH"), (23, "Telnet"), (25, "SMTP"),
            (53, "DNS"), (67, "DHCP server"), (68, "DHCP client"), (69, "TFTP"),
            (80, "HTTP"), (110, "POP3"), (123, "NTP"), (135, "MS RPC"),
            (137, "NetBIOS NS"), (138, "NetBIOS datagram"), (139, "NetBIOS session"),
            (143, "IMAP"), (161, "SNMP"), (162, "SNMP trap"), (179, "BGP"),
            (389, "LDAP"), (443, "HTTPS"), (445, "SMB"), (465, "SMTPS"),
            (514, "Syslog"), (587, "SMTP submission"), (631, "CUPS IPP"),
            (636, "LDAPS"), (993, "IMAPS"), (995, "POP3S"), (3306, "MySQL"),
            (3389, "RDP"), (5432, "PostgreSQL"), (5900, "VNC"), (6379, "Redis"),
            (8080, "HTTP-alt"), (8443, "HTTPS-alt"), (27017, "MongoDB"),
            (1194, "OpenVPN"), (1812, "RADIUS auth")
        ]
        for port, desc in ports:
            make_item(f"port {port}", f"{desc} (port {port})", Category.PORT_FILTER)

        # 81-100: Protocol specifics
        proto = [
            ("tcp", "TCP packets", Category.PROTOCOL),
            ("udp", "UDP packets", Category.PROTOCOL),
            ("icmp", "ICMP packets", Category.PROTOCOL),
            ("icmp[icmptype]==8", "ICMP Echo Request", Category.PROTOCOL),
            ("icmp[icmptype]==0", "ICMP Echo Reply", Category.PROTOCOL),
            ("icmp[icmptype]==3", "ICMP Unreachable", Category.PROTOCOL),
            ("icmp[icmptype]==11", "ICMP Time Exceeded", Category.PROTOCOL),
            ("esp", "ESP (IPsec)", Category.PROTOCOL),
            ("ah", "AH (IPsec)", Category.PROTOCOL),
            ("gre", "GRE tunnels", Category.PROTOCOL),
            ("udp[8:2]", "UDP payload length", Category.PROTOCOL),
            ("tcp[13]", "TCP flags byte", Category.PROTOCOL),
            ("ether host aa:bb:cc:dd:ee:ff", "MAC address filter", Category.PROTOCOL),
            ("ether src 00:11:22:33:44:55", "Source MAC filter", Category.PROTOCOL),
            ("ether dst 66:77:88:99:aa:bb", "Dest MAC filter", Category.PROTOCOL),
            ("vlan 100", "Specific VLAN ID", Category.PROTOCOL),
            ("mpls.label 1024", "MPLS label filter", Category.PROTOCOL),
            ("pppoe", "PPP over Ethernet", Category.PROTOCOL),
            ("arp[6:2] == 1", "ARP Request", Category.PROTOCOL),
            ("arp[6:2] == 2", "ARP Reply", Category.PROTOCOL),
        ]
        for filt, desc, cat in proto:
            make_item(filt, desc, cat)

        # 101-130: TCP flags
        flags = [
            ("tcp[tcpflags] & tcp-syn != 0", "SYN flag set", Category.TCP_FLAGS),
            ("tcp[tcpflags] & tcp-ack != 0", "ACK flag set", Category.TCP_FLAGS),
            ("tcp[tcpflags] & tcp-fin != 0", "FIN flag set", Category.TCP_FLAGS),
            ("tcp[tcpflags] & tcp-rst != 0", "RST flag set", Category.TCP_FLAGS),
            ("tcp[tcpflags] & tcp-push != 0", "PSH flag set", Category.TCP_FLAGS),
            ("tcp[tcpflags] & tcp-urg != 0", "URG flag set", Category.TCP_FLAGS),
            ("tcp[tcpflags] == tcp-syn", "SYN-only packets", Category.TCP_FLAGS),
            ("tcp[tcpflags] == (tcp-syn|tcp-ack)", "SYN-ACK packets", Category.TCP_FLAGS),
            ("tcp[tcpflags] == (tcp-fin|tcp-ack)", "FIN-ACK packets", Category.TCP_FLAGS),
            ("tcp[tcpflags] == (tcp-rst|tcp-ack)", "RST-ACK packets", Category.TCP_FLAGS),
            ("tcp[tcpflags] & (tcp-syn|tcp-ack) == 0", "NULL scan", Category.TCP_FLAGS),
            ("tcp[tcpflags] & (tcp-fin|tcp-urg|tcp-psh) != 0", "XMAS scan", Category.TCP_FLAGS),
            ("tcp[tcpflags] == tcp-fin", "FIN scan", Category.TCP_FLAGS),
            ("tcp[13] == 2", "SYN (numeric)", Category.TCP_FLAGS),
            ("tcp[13] == 16", "ACK (numeric)", Category.TCP_FLAGS),
            ("tcp[13] == 18", "SYN-ACK (numeric)", Category.TCP_FLAGS),
            ("tcp[13] == 4", "RST (numeric)", Category.TCP_FLAGS),
            ("tcp[13] == 1", "FIN (numeric)", Category.TCP_FLAGS),
            ("tcp[13] == 24", "PSH-ACK (numeric)", Category.TCP_FLAGS),
            ("tcp[13] == 32", "URG (numeric)", Category.TCP_FLAGS),
            ("tcp[13] == 40", "RST-ACK (numeric)", Category.TCP_FLAGS),
            ("tcp[13] == 17", "FIN-ACK (numeric)", Category.TCP_FLAGS),
            ("tcp[13] == 3", "SYN-FIN (rare)", Category.TCP_FLAGS),
            ("tcp[13] == 41", "FIN-RST-ACK", Category.TCP_FLAGS),
            ("tcp[13] & 0x02 != 0", "SYN (bitmask)", Category.TCP_FLAGS),
            ("tcp[13] & 0x10 != 0", "ACK (bitmask)", Category.TCP_FLAGS),
            ("tcp[13] & 0x01 != 0", "FIN (bitmask)", Category.TCP_FLAGS),
            ("tcp[13] & 0x04 != 0", "RST (bitmask)", Category.TCP_FLAGS),
            ("tcp[13] & 0x08 != 0", "PSH (bitmask)", Category.TCP_FLAGS),
            ("tcp[13] & 0x20 != 0", "URG (bitmask)", Category.TCP_FLAGS),
        ]
        for filt, desc, cat in flags:
            make_item(filt, desc, cat)

        # 131-160: Size, slicing, rotation
        sizes = [
            ("greater 100", "Packets >100 bytes", Category.SIZE),
            ("less 64", "Packets <64 bytes", Category.SIZE),
            ("len == 128", "Exact 128 bytes", Category.SIZE),
            ("ip[2:2] == 1500", "IP length 1500", Category.SIZE),
            ("ip[6:1] & 0x1F == 0", "No IP options", Category.SIZE),
            ("ip[8:1] == 64", "TTL=64 (Linux)", Category.SIZE),
            ("ip[8:1] == 128", "TTL=128 (Windows)", Category.SIZE),
            ("ip[8:1] == 255", "TTL=255 (Solaris)", Category.SIZE),
            ("ip[9:1] == 6", "IP protocol=TCP", Category.SIZE),
            ("ip[9:1] == 17", "IP protocol=UDP", Category.SIZE),
            ("ip[9:1] == 1", "IP protocol=ICMP", Category.SIZE),
            ("ip[9:1] == 2", "IGMP", Category.SIZE),
            ("ip[9:1] == 50", "ESP", Category.SIZE),
            ("ip[9:1] == 51", "AH", Category.SIZE),
            ("ip[9:1] == 88", "EIGRP", Category.SIZE),
            ("ip[9:1] == 89", "OSPF", Category.SIZE),
            ("-s 64", "Snapshot 64 bytes", Category.OUTPUT),
            ("-s 128", "Snapshot 128 bytes", Category.OUTPUT),
            ("-s 256", "Snapshot 256 bytes", Category.OUTPUT),
            ("-C 10 -w dump.pcap", "Rotate 10MB", Category.OUTPUT),
            ("-G 60 -w dump.pcap", "Rotate 60s", Category.OUTPUT),
            ("-W 5 -w dump.pcap", "Keep 5 files", Category.OUTPUT),
            ("-K", "Disable checksum", Category.PERFORMANCE),
            ("-Q in", "Ingress only", Category.CAPTURE),
            ("-Q out", "Egress only", Category.CAPTURE),
            ("-Q inout", "Both dirs", Category.CAPTURE),
            ("-L", "List link types", Category.INFO),
            ("-D", "List interfaces", Category.INFO),
            ("-S", "Absolute seq", Category.OUTPUT),
            ("-B 4096", "Buffer 4096 KB", Category.PERFORMANCE),
        ]
        for filt, desc, cat in sizes:
            make_item(filt, desc, cat)

        # 161-190: Logical operators
        logic = [
            ("tcp and port 80", "HTTP TCP", Category.LOGIC),
            ("udp and port 53", "DNS UDP", Category.LOGIC),
            ("host 1.1.1.1 and port 443", "HTTPS to IP", Category.LOGIC),
            ("src 10.0.0.1 and dst 10.0.0.2", "Point-to-point", Category.LOGIC),
            ("port 80 or port 443", "HTTP or HTTPS", Category.LOGIC),
            ("port 21 or port 22 or port 23", "FTP/SSH/Telnet", Category.LOGIC),
            ("not arp", "Exclude ARP", Category.LOGIC),
            ("not broadcast", "Exclude broadcasts", Category.LOGIC),
            ("not multicast", "Exclude multicasts", Category.LOGIC),
            ("tcp and not port 22", "TCP except SSH", Category.LOGIC),
            ("(tcp port 80) or (udp port 53)", "Grouped logic", Category.LOGIC),
            ("(src net 192.168.0.0/24) and (dst port 80)", "Subnet to web", Category.LOGIC),
            ("(tcp[13] & 2 != 0) and (dst port 22)", "SYN to SSH", Category.LOGIC),
            ("icmp and (icmp[icmptype]==8 or icmp[icmptype]==0)", "Ping both ways", Category.LOGIC),
            ("(port 67 or 68) and not arp", "DHCP clean", Category.LOGIC),
            ("ip and not (tcp or udp or icmp)", "Other protocols", Category.LOGIC),
            ("vlan and arp", "ARP in VLAN", Category.LOGIC),
            ("mpls and ip", "IP in MPLS", Category.LOGIC),
            ("tcp port 3389 and tcp[13] & 0x02 != 0", "RDP SYN", Category.LOGIC),
            ("udp port 514 and len > 512", "Large syslog", Category.LOGIC),
            ("(host 8.8.8.8) and (icmp or dns)", "Google ping/DNS", Category.LOGIC),
            ("tcp[2:2] > 1024", "Source ports >1024", Category.LOGIC),
            ("tcp[4:2] == 443", "Dest port 443", Category.LOGIC),
            ("ip[16] == 0", "First fragment", Category.LOGIC),
            ("ip[6:2] & 0x3FFF != 0", "Fragmented IP", Category.LOGIC),
            ("tcp[0:2] == 22", "Source port 22", Category.LOGIC),
            ("udp[0:2] == 53", "Source port 53", Category.LOGIC),
            ("arp[0:2] == 1", "ARP over Ethernet", Category.LOGIC),
            ("ether[12:2] == 0x0800", "EtherType IPv4", Category.LOGIC),
            ("ether[12:2] == 0x86DD", "EtherType IPv6", Category.LOGIC),
        ]
        for filt, desc, cat in logic:
            make_item(filt, desc, cat)

        # 191-220: Payload inspection (fixed syntax: == instead of =)
        payload = [
            ("tcp[20:4] == 0x47455420", "HTTP GET", Category.PAYLOAD),
            ("tcp[20:5] == 0x504F5354", "HTTP POST", Category.PAYLOAD),
            ("tcp[20:4] == 0x48454144", "HTTP HEAD", Category.PAYLOAD),
            ("tcp[20:7] == 0x75736572", "'user' string", Category.PAYLOAD),
            ("tcp[20:5] == 0x70617373", "'pass' string", Category.PAYLOAD),
            ("udp[8:4] == 0x01000001", "DNS A query", Category.PAYLOAD),
            ("udp[8:4] == 0x01000002", "DNS NS query", Category.PAYLOAD),
            ("udp[8:2] & 0x8000 != 0", "DNS response", Category.PAYLOAD),
            ("tcp[20:2] == 0x1603", "TLS handshake", Category.PAYLOAD),
            ("tcp[20:2] == 0x1403", "TLS alert", Category.PAYLOAD),
            ("tcp[20:3] == 0x474554", "GET first bytes", Category.PAYLOAD),
            ("ip[16:4] == 0x0a000001", "IP src 10.0.0.1", Category.PAYLOAD),
            ("ip[20:4] == 0xc0a80101", "IP dst 192.168.1.1", Category.PAYLOAD),
            ("ether[0:4] == 0xffffffff", "Broadcast MAC", Category.PAYLOAD),
            ("ether[0:3] == 0x01005e", "IPv4 multicast MAC", Category.PAYLOAD),
            ("ether[0:3] == 0x333300", "IPv6 multicast MAC", Category.PAYLOAD),
            ("icmp[0:2] == 0x0000", "ICMP ID 0", Category.PAYLOAD),
            ("icmp[4:2] == 0x1234", "ICMP seq 0x1234", Category.PAYLOAD),
            ("udp[8:2] == 0x0014", "DNS TXID 20", Category.PAYLOAD),
            ("tcp[20:4] == 0x45515550", "FTP EQUP", Category.PAYLOAD),
            ("tcp[20:6] == 0x55534552", "FTP USER", Category.PAYLOAD),
            ("tcp[20:6] == 0x50415353", "FTP PASS", Category.PAYLOAD),
            ("tcp[20:5] == 0x51554954", "FTP QUIT", Category.PAYLOAD),
            ("tcp[20:3] == 0x444154", "MySQL DAT", Category.PAYLOAD),
            ("udp[8:3] == 0x535450", "STP (protocol)", Category.PAYLOAD),
            ("tcp[20:6] == 0x434F4E4E", "Redis CONN", Category.PAYLOAD),
            ("ip[8:1] == 128 and ip[9:1] == 1", "TTL 128 + ICMP", Category.PAYLOAD),
            ("ip[8:1] > 200", "High TTL", Category.PAYLOAD),
            ("ip[8:1] < 30", "Low TTL (traceroute)", Category.PAYLOAD),
            ("tcp[20:4] == 0x4C4F4749", "MongoDB LOGI", Category.PAYLOAD),
        ]
        for filt, desc, cat in payload:
            make_item(filt, desc, cat)

        # 221-240: Offensive
        offensive = [
            ("-A port 21", "Sniff FTP passwords", Category.OFFENSIVE),
            ("-A port 23", "Sniff Telnet sessions", Category.OFFENSIVE),
            ("-A port 110", "Sniff POP3 creds", Category.OFFENSIVE),
            ("-A 'port 80 and \"GET\"'", "Extract HTTP URIs", Category.OFFENSIVE),
            ("-A 'port 80 and \"Cookie\"'", "Steal cookies", Category.OFFENSIVE),
            ("-v udp port 53", "Detect DNS tunneling", Category.OFFENSIVE),
            ("icmp and len > 64", "Detect ICMP exfil", Category.OFFENSIVE),
            ("tcp port 22 and tcp[13]==0x02", "Map SSH scans", Category.OFFENSIVE),
            ("tcp[13] & 0x3F == 0", "Detect NULL scan", Category.OFFENSIVE),
            ("tcp[13] & 0x3F == 0x01", "Detect FIN scan", Category.OFFENSIVE),
            ("tcp[13] & 0x3F == 0x29", "Detect XMAS scan", Category.OFFENSIVE),
            ("tcp port 443 and tcp[20:2]==0x1603", "Capture TLS handshakes", Category.OFFENSIVE),
            ("-w creds.pcap -A 'port 21 or 22 or 23'", "Log plaintext logins", Category.OFFENSIVE),
            ("-c 10 udp port 161", "Grab SNMP queries", Category.OFFENSIVE),
            ("port 3389 and tcp[13]==0x02", "Detect RDP brute-force", Category.OFFENSIVE),
            ("tcp[20:4] == 0x50494E47", "TCP PING (covert)", Category.OFFENSIVE),
            ("tcp[20:6] == 0x2E2E2F2E2E", "Directory traversal", Category.OFFENSIVE),
            ("-vv udp port 123", "NTP monlist reflection", Category.OFFENSIVE),
            ("tcp port 6379 and \"auth\"", "Redis password sniff", Category.OFFENSIVE),
            ("tcp port 5432 and \"password\"", "Postgres password sniff", Category.OFFENSIVE),
        ]
        for filt, desc, cat in offensive:
            make_item(filt, desc, cat)

        # 241-255: Defensive
        defensive = [
            ("-e arp", "Monitor ARP poisoning", Category.DEFENSIVE),
            ("arp[6:2] == 1 and arp[7:4] == 0x0a000001", "ARP who-has 10.0.0.1", Category.DEFENSIVE),
            ("-e 'udp port 67 or 68'", "Detect rogue DHCP", Category.DEFENSIVE),
            ("tcp port 80 and \"SELECT\"", "Detect SQL injection", Category.DEFENSIVE),
            ("tcp port 80 and \"UNION\"", "Detect UNION SQLi", Category.DEFENSIVE),
            ("tcp port 80 and \"%2e%2e\"", "Detect path traversal", Category.DEFENSIVE),
            ("tcp port 443 and tcp[20:2]==0x1603 and len > 200", "Heartbleed detection", Category.DEFENSIVE),
            ("icmp[icmptype]==8 and icmp[0:2] != 0x0000", "Custom ICMP payloads", Category.DEFENSIVE),
            ("not port 22 and not port 443 and tcp[13]==0x02", "Unexpected SYNs (scan)", Category.DEFENSIVE),
            ("udp port 53 and len > 512", "DNS amplification", Category.DEFENSIVE),
            ("tcp[13] == 0x12", "Nmap OS detection", Category.DEFENSIVE),
            ("-c 100 -nn -r dump.pcap", "Forensic triage", Category.DEFENSIVE),
            ("-e -r dump.pcap", "Reconstruct MAC/IP maps", Category.DEFENSIVE),
            ("-ttt -r dump.pcap", "C2 beacon timing", Category.DEFENSIVE),
            ("tcp port 445 and \"SMB\"", "EternalBlue probe", Category.DEFENSIVE),
        ]
        for filt, desc, cat in defensive:
            make_item(filt, desc, cat)

        # Ensure exactly 255 (we have 255 exactly)
        return items

    def get_by_id(self, item_id: int) -> Optional[Dict]:
        for item in self.items:
            if item["id"] == item_id:
                return item
        return None

# ------------------------------
# UI Class
# ------------------------------
class PacketVisionUI:
    def __init__(self):
        self.console = Console()
        self.db = TCPDumpDatabase()
        self.categories = ["All"] + Category.list_names()
        self.current_category = "All"
        self.search_query = ""
        self.page = 0
        self.page_size = 20

    def show_title(self):
        self.console.clear()
        banner_text = Text(BANNER, style="bold cyan")
        self.console.print(Align.center(banner_text))
        warning = Text(
            "ONLY FOR EDUCATIONAL PURPOSES AND RESEARCH\n"
            "Never misuse this tool. Perform security testing only on networks you own or where you have explicit authorization.\n\n"
            "Created by: SYLHETYHACKVENGER (THE-ERROR808)",
            style="bold magenta"
        )
        self.console.print(Align.center(warning))
        time.sleep(1)

    def show_dashboard(self):
        self.console.clear()
        title = Text("PacketVision Control Center", style="bold cyan")
        self.console.print(Align.center(title))
        self.console.print(Align.center("─" * 60, style="dim"))

        # Category selector
        cat_table = Table(show_header=False, box=box.SIMPLE, style="cyan")
        cat_table.add_column("Categories", style="cyan")
        row = []
        for i, cat in enumerate(self.categories):
            if cat == self.current_category:
                row.append(f"[bold magenta]{cat}[/bold magenta]")
            else:
                row.append(cat)
            if (i + 1) % 4 == 0:
                cat_table.add_row(" | ".join(row))
                row = []
        if row:
            cat_table.add_row(" | ".join(row))
        self.console.print(cat_table)

        search_text = f"Search: {self.search_query}" if self.search_query else "Press 's' to search"
        self.console.print(Align.center(search_text, style="italic yellow"))

        # Filter items
        items = self.db.items
        if self.current_category != "All":
            items = [i for i in items if i["category"] == self.current_category]
        if self.search_query:
            q = self.search_query.lower()
            items = [i for i in items if q in i["filter"].lower() or q in i["description"].lower()]

        total = len(items)
        max_page = max(0, (total - 1) // self.page_size)
        if self.page > max_page:
            self.page = max_page
        if self.page < 0:
            self.page = 0

        start = self.page * self.page_size
        end = min(start + self.page_size, total)
        page_items = items[start:end]

        table = Table(
            title=f"Items {start+1}-{end} of {total} (Page {self.page+1}/{max_page+1})",
            box=box.HEAVY_EDGE,
            style="cyan"
        )
        table.add_column("ID", style="dim", width=4)
        table.add_column("Filter", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("Category", style="blue")
        for item in page_items:
            table.add_row(str(item["id"]), item["filter"], item["description"], item["category"])
        self.console.print(table)

        self.console.print(Align.center(
            "[bold]Select an ID to view details, or use commands: q=quit, s=search, c=category, n=next page, p=previous page.[/bold]"
        ))

    def run(self):
        self.show_title()
        while True:
            self.show_dashboard()
            choice = Prompt.ask("Selected option", default="q")
            if choice.lower() == "q":
                self.console.print("[bold red]Exiting PacketVision. Stay ethical![/bold red]")
                break
            elif choice.lower() == "s":
                self.search_query = Prompt.ask("Enter search term")
                self.page = 0
                continue
            elif choice.lower() == "c":
                self.console.print("Available categories:", style="bold")
                for i, cat in enumerate(self.categories):
                    self.console.print(f"{i+1}. {cat}")
                cat_choice = IntPrompt.ask(
                    "Select category number",
                    choices=[str(i+1) for i in range(len(self.categories))]
                )
                self.current_category = self.categories[cat_choice-1]
                self.search_query = ""
                self.page = 0
                continue
            elif choice.lower() == "n":
                self.page += 1
                continue
            elif choice.lower() == "p":
                self.page -= 1
                continue
            else:
                try:
                    item_id = int(choice)
                except ValueError:
                    self.console.print("[red]Invalid input. Enter a number or a command.[/red]")
                    time.sleep(1)
                    continue
                item = self.db.get_by_id(item_id)
                if not item:
                    self.console.print("[red]Invalid ID.[/red]")
                    time.sleep(1)
                    continue
                self.show_item_details(item)
                self.run_real_capture(item)

    def show_item_details(self, item: Dict):
        self.console.clear()
        detail = (
            f"[bold cyan]Feature ID: {item['id']}[/bold cyan]\n\n"
            f"[bold magenta]Filter:[/bold magenta] {item['filter']}\n\n"
            f"[bold green]Description:[/bold green] {item['description']}\n\n"
            f"[bold blue]Category:[/bold blue] {item['category']}\n\n"
            f"[bold yellow]What it does:[/bold yellow]\n{item['explanation']}\n\n"
            f"[bold cyan]Why it exists:[/bold cyan]\n{item['purpose']}\n\n"
            f"[bold red]Causes & Consequences:[/bold red]\n{item['consequences']}\n\n"
            f"[bold green]Example command:[/bold green]\n`sudo tcpdump -i <interface> {item['filter']}`"
        )
        panel = Panel(
            detail,
            title="PacketVision - Detailed Analysis",
            border_style="magenta",
            box=box.DOUBLE_EDGE
        )
        self.console.print(panel)

        # Speak the FULL "Causes & Consequences" text (including the heading) at a slower speed
        TTS.speak(item['consequences'])

    def run_real_capture(self, item: Dict):
        """Execute sudo tcpdump with the selected filter on the target interface."""
        self.console.print("\n[bold yellow]Enter the target interface (e.g., wlan0, eth0):[/bold yellow]")
        target = Prompt.ask("Interface", default="wlan0")
        if not target:
            target = "wlan0"

        # Check if tcpdump exists
        if not shutil.which("tcpdump"):
            self.console.print("[red]Error: tcpdump not found in PATH. Please install it.[/red]")
            input("\nPress Enter to return to dashboard...")
            return

        # Build command: sudo tcpdump -i <target> <filter>
        # Use shlex.split to handle quotes properly
        try:
            filter_parts = shlex.split(item["filter"])
        except ValueError as e:
            self.console.print(f"[red]Invalid filter syntax: {e}[/red]")
            input("\nPress Enter to return to dashboard...")
            return

        cmd = ["sudo", "tcpdump", "-i", target] + filter_parts

        self.console.print(f"\n[bold green]Executing:[/bold green] {' '.join(cmd)}")
        self.console.print("[bold yellow]Press Ctrl+C to stop capture.[/bold yellow]")

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in process.stdout:
                self.console.print(line, end="")
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            self.console.print("\n[bold red]Capture stopped by user.[/bold red]")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
        finally:
            input("\nPress Enter to return to dashboard...")

# ------------------------------
# Main entry point
# ------------------------------
def main():
    try:
        # Verify sudo availability (optional)
        if not shutil.which("sudo"):
            logging.warning("sudo not found; tcpdump may fail without root privileges.")
        ui = PacketVisionUI()
        ui.run()
    except KeyboardInterrupt:
        print("\n[bold red]Session terminated.[/bold red]")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
