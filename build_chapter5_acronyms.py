#!/usr/bin/env python3
"""Build Chapter 5 acronym study guide and practice quiz."""

import html
import json
from pathlib import Path

from build_chapter2_quiz import quiz_page_html

ROOT = Path(__file__).resolve().parent

# (acronym, expansion, purpose) — expansions as provided for CompTIA A+
ACRONYMS = [
    ("AAA", "Authentication, Authorization, and Accounting", "Security framework that verifies who you are, what you can access, and logs what you did on a network or system."),
    ("ACL", "Access Control List", "Ruleset that specifies which users or systems are allowed or denied access to a resource such as a file, folder, or network."),
    ("ADF", "Automatic Document Feeder", "Printer/scanner tray that feeds multipage documents automatically so you do not have to place each sheet on the glass."),
    ("AES", "Advanced Encryption Standard", "Widely used symmetric encryption algorithm that protects data at rest and in transit with strong, standardized ciphers."),
    ("AMD", "Advanced Micro Devices, Inc.", "CPU and GPU manufacturer whose processors and graphics chips compete with Intel and NVIDIA in PCs and servers."),
    ("AP", "Access Point", "Wireless network device that lets Wi-Fi clients connect to a wired LAN or the internet."),
    ("APFS", "Apple File System", "Modern Apple disk file system optimized for SSDs, with strong encryption, snapshots, and space sharing on macOS and iOS."),
    ("APIPA", "Automatic Private Internet Protocol Addressing", "Windows feature that assigns a 169.254.x.x address when DHCP fails so the host can still talk on the local link."),
    ("ARM", "Advanced RISC (Reduced Instruction Set Computer) Machine", "CPU architecture used in phones, tablets, and many laptops that emphasizes efficiency with a reduced instruction set."),
    ("ATX", "Advanced Technology Extended", "Common PC motherboard and power-supply form factor that defines board size, mounting holes, and connector layout."),
    ("AUP", "Acceptable Use Policy", "Organizational rules describing allowed and prohibited uses of company computers, networks, and internet access."),
    ("BEC", "Business Email Compromise", "Social-engineering fraud where attackers impersonate executives or vendors by email to steal money or data."),
    ("BIOS", "Basic Input/Output System", "Legacy firmware that initializes hardware at power-on and starts the boot process before the OS loads."),
    ("BNC", "Bayonet Neill-Concelman", "Coaxial connector with a twist-lock bayonet coupling, historically used on older network and video cabling."),
    ("BSOD", "Blue Screen of Death", "Windows stop-error screen shown when the OS encounters a critical fault it cannot recover from safely."),
    ("BYOD", "Bring Your Own Device", "Policy that lets employees use personal phones or laptops for work, usually managed with MDM and security controls."),
    ("CAC", "Calling-card Authorization Computer", "Smart-card style credential used to authenticate users for secure access in government and enterprise environments."),
    ("CAS", "Column Address Strobe", "Memory timing signal related to how DRAM columns are addressed; often discussed with RAM latency (CAS latency)."),
    ("CIFS", "Common Internet File System", "Microsoft file-sharing dialect of SMB that lets clients access networked files and printers over TCP/IP."),
    ("CMDB", "Configuration Management Database", "Central inventory of IT assets and their relationships used for change, incident, and asset management."),
    ("CMOS", "Complementary Metal-Oxide Semiconductor", "Low-power chip technology; in PCs it often refers to the battery-backed chip storing BIOS/UEFI settings."),
    ("CNAME", "Canonical Name", "DNS record that aliases one hostname to another canonical hostname."),
    ("CPU", "Central Processing Unit", "Primary processor that executes program instructions and performs most computing work in a device."),
    ("DB-9", "Serial Communications D-Shell Connector, 9 pins", "Nine-pin D-sub serial connector historically used for RS-232 devices, consoles, and older peripherals."),
    ("DDoS", "Distributed Denial of Service", "Attack that floods a target from many compromised systems to overwhelm availability of a service."),
    ("DDR", "Double Data Rate", "Memory technology that transfers data on both clock edges, used in successive generations of RAM modules."),
    ("DHCP", "Dynamic Host Configuration Protocol", "Network service that automatically assigns IP addresses and related settings to clients."),
    ("DIMM", "Dual In-line Memory Module", "Standard stick form factor for desktop and server RAM with contacts on both sides of the module."),
    ("DKIM", "DomainKeys Identified Mail", "Email authentication method that signs outbound messages so receivers can verify the sending domain."),
    ("DLP", "Data Loss Prevention", "Security controls that detect and block unauthorized transfer or leakage of sensitive data."),
    ("DMARC", "Domain-based Message Authentication, Reporting, and Conformance", "Email policy framework that builds on SPF/DKIM and tells receivers how to handle failed authentication."),
    ("DNS", "Domain Name System", "Internet directory that resolves human-readable names to IP addresses and related records."),
    ("DoS", "Denial of Service", "Attack that makes a system or network unavailable by exhausting resources or crashing a service."),
    ("DRM", "Digital Rights Management", "Technology that restricts how digital media or software can be copied, shared, or used."),
    ("DSL", "Digital Subscriber Line", "Broadband internet technology that delivers data over telephone copper lines."),
    ("DVI", "Digital Visual Interface", "Video connector standard used to link computers to monitors, supporting digital (and sometimes analog) signals."),
    ("ECC", "Error-correcting Code", "Memory feature that detects and corrects bit errors, common in servers for higher reliability."),
    ("EDR", "Endpoint Detection and Response", "Security platform that monitors endpoints for threats and supports investigation and remediation."),
    ("EFS", "Encrypting File System", "Windows feature that encrypts individual files and folders with user-tied keys."),
    ("EOL", "End-of-life", "Point when a product no longer receives updates or vendor support and should be replaced or mitigated."),
    ("eSATA", "External Serial Advanced Technology Attachment", "External SATA interface for connecting outside hard drives at SATA speeds."),
    ("ESD", "Electrostatic Discharge", "Sudden static electricity surge that can damage sensitive electronic components during handling."),
    ("eSIM", "Embedded SIM", "Software-based SIM built into a device that can be provisioned without a physical SIM card."),
    ("EULA", "End-user License Agreement", "Legal contract defining the terms under which a user may install and use software."),
    ("exFAT", "Extended File Allocation Table", "Microsoft file system designed for flash media with large file support across Windows, macOS, and more."),
    ("FaaS", "Function As A Service", "Cloud model that runs event-triggered code functions without managing servers (serverless)."),
    ("FAT32", "32-bit File Allocation Table", "Older widely compatible file system with a 4 GB per-file size limit, still used on USB drives."),
    ("FRT", "Facial Recognition Technology", "Biometric method that identifies or unlocks devices by analyzing facial features."),
    ("FTP", "File Transfer Protocol", "Classic protocol for uploading and downloading files; often replaced by SFTP for security."),
    ("GFS", "Grandfather-Father-Son", "Backup rotation scheme that keeps daily, weekly, and monthly copies on a staggered schedule."),
    ("GPS", "Global Positioning System", "Satellite navigation system that provides location and time data to GPS receivers."),
    ("GPT", "GUID (Globally Unique Identifier) Partition Table", "Modern disk partitioning scheme that supports large disks and many partitions, replacing MBR limits."),
    ("GPU", "Graphics Processing Unit", "Processor specialized for rendering graphics and accelerating parallel workloads like video and AI."),
    ("GUI", "Graphical User Interface", "Visual interface of windows, icons, and menus that users interact with instead of pure text commands."),
    ("GUID", "Globally Unique Identifier", "128-bit unique ID used to identify software objects, partitions, and other entities without collision."),
    ("HD", "High Definition", "Video quality standard with higher resolution than standard definition (commonly 720p or 1080p)."),
    ("HDD", "Hard Disk Drive", "Magnetic spinning-disk storage device used for bulk data storage at lower cost per gigabyte."),
    ("HDMI", "High-definition Media Interface", "Digital audio/video connector that carries uncompressed video and multi-channel audio to displays."),
    ("HSM", "Hardware Security Module", "Tamper-resistant device that generates and stores cryptographic keys for high-security operations."),
    ("HTTP", "Hypertext Transfer Protocol", "Application protocol that transfers web pages and API data between browsers and servers (unencrypted)."),
    ("HTTPS", "Hypertext Transfer Protocol Secure", "HTTP wrapped in TLS encryption to protect web traffic confidentiality and integrity."),
    ("IaaS", "Infrastructure as a Service", "Cloud model that rents virtual servers, storage, and networking for customers to configure."),
    ("IAM", "Identity Access Management", "Policies and tools that control user identities, authentication, and access rights across systems."),
    ("IMAP", "Internet Mail Access Protocol", "Email protocol that keeps messages on the server and syncs mailboxes across multiple devices."),
    ("IOPS", "Input/Output Operations Per Second", "Performance metric measuring how many read/write operations a storage device can handle per second."),
    ("IoT", "Internet of Things", "Network of everyday devices (sensors, appliances, cameras) connected to the internet for data and control."),
    ("IP", "Internet Protocol", "Core network protocol that addresses and routes packets between hosts on an IP network."),
    ("IPS", "In-plane Switching", "LCD panel technology known for wide viewing angles and accurate colors compared with TN panels."),
    ("IR", "Infrared", "Wireless line-of-sight communication or sensing using infrared light, used in remotes and some sensors."),
    ("ISO", "International Organization for Standardization", "Standards body; also casually used for disk image files (.iso) that mirror optical media."),
    ("ISP", "Internet Service Provider", "Company that provides customers with internet connectivity and related services."),
    ("ITX", "Information Technology eXtended", "Smaller motherboard form-factor family (such as Mini-ITX) for compact PCs."),
    ("KVM", "Keyboard-Video-Mouse", "Switch or device that lets one keyboard, mouse, and monitor control multiple computers."),
    ("LAN", "Local Area Network", "Network covering a limited area such as a home, office, or building."),
    ("LC", "Lucent Connector", "Small form-factor fiber-optic connector commonly used in high-density network installations."),
    ("LCD", "Liquid Crystal Display", "Flat-panel display technology that uses liquid crystals and a backlight to form images."),
    ("LDAP", "Lightweight Directory Access Protocol", "Protocol for querying and managing directory services such as user accounts and groups."),
    ("LED", "Light-emitting Diode", "Semiconductor light source used for indicators, lighting, and modern display backlights."),
    ("LTE", "Long-Term Evolution", "High-speed cellular wireless standard commonly known as 4G LTE mobile data."),
    ("MAC", "Media Access Control", "Hardware address uniquely identifying a network interface on a local network segment."),
    ("MAN", "Metropolitan Area Network", "Network spanning a city or campus, larger than a LAN but smaller than a WAN."),
    ("MBR", "Master Boot Record", "Legacy disk boot sector and partitioning scheme limited to four primary partitions and 2 TB disks."),
    ("MDM", "Mobile Device Management", "Enterprise software that configures, secures, and remotely manages smartphones and tablets."),
    ("MDR", "Managed Detection and Response", "Outsourced security service that monitors for threats and helps respond to incidents."),
    ("MFA", "Multifactor Authentication", "Login requirement that combines two or more factors (something you know, have, or are)."),
    ("MFP", "Multifunction Printer", "Office device that combines printing, scanning, copying, and often faxing in one unit."),
    ("MMC", "Microsoft Management Console", "Windows shell that hosts administrative snap-ins such as Device Manager and Event Viewer tools."),
    ("MNDA", "Mutual Non-Disclosure Agreement", "Contract where both parties agree to keep shared confidential information secret."),
    ("mSATA", "Mini-serial Advanced Technology Attachment", "Compact SATA connector/form factor used for small SSDs in laptops and embedded systems."),
    ("MX", "Mail Exchange", "DNS record that tells senders which mail servers accept email for a domain."),
    ("NAC", "Network Access Control", "Security approach that authenticates and checks devices before granting network access."),
    ("NAS", "Network Access Server", "Device or service that authenticates remote users and grants them access to network resources."),
    ("NAT", "Network Address Translation", "Router technique that maps private internal IPs to public addresses for internet access."),
    ("NDA", "Non-Disclosure Agreement", "Legal contract requiring one or more parties not to reveal confidential information."),
    ("NetBIOS", "Network Basic Input/Output System", "Legacy Windows networking API/name service used historically for local name resolution and shares."),
    ("NFC", "Near-field Communication", "Short-range wireless tech for payments, pairing, and data exchange within a few centimeters."),
    ("NIC", "Network Interface Card", "Hardware adapter that connects a computer to a wired or wireless network."),
    ("NTFS", "New Technology File System", "Default Windows file system supporting permissions, encryption, compression, and large volumes."),
    ("NTP", "Network Time Protocol", "Protocol that synchronizes device clocks with authoritative time servers."),
    ("NVMe", "Non-volatile Memory Express", "High-speed SSD interface protocol designed for PCIe flash storage with low latency."),
    ("OEM", "Original Equipment Manufacturer", "Company that builds hardware or software sold under another brand or bundled with systems."),
    ("OLED", "Organic Light-emitting Diode", "Display technology where each pixel emits its own light, enabling deep blacks and high contrast."),
    ("ONT", "Optical Network Terminal", "Fiber-to-the-premises device that converts optical signals to Ethernet for home or business use."),
    ("OS", "Operating System", "Core software that manages hardware, processes, memory, and provides services for applications."),
    ("OTP", "One-time Password/Passcode", "Single-use code used for authentication, often delivered by app, SMS, or hardware token."),
    ("PaaS", "Platform as a Service", "Cloud model that provides a managed runtime platform so developers deploy apps without managing OS infrastructure."),
    ("PAM", "Privileged Access Management", "Controls that secure, monitor, and limit use of powerful admin accounts and credentials."),
    ("PAN", "Personal Area Network", "Very short-range network around a person, such as Bluetooth between phone and headset."),
    ("PC", "Personal Computer", "General-purpose computer designed for individual use, such as a desktop or laptop."),
    ("PCI", "Peripheral Component Interconnect", "Older parallel expansion-bus standard for adding cards to a motherboard."),
    ("PCIe", "Peripheral Component Interconnect Express", "Modern high-speed serial expansion bus used for GPUs, NVMe SSDs, and add-in cards."),
    ("PCL", "Printer Command Language", "HP page-description language that tells printers how to render text and graphics."),
    ("PII", "Personally Identifiable Information", "Data that can identify an individual, such as name, SSN, or email, requiring careful protection."),
    ("PIN", "Personal Identification Number", "Numeric secret used to authenticate a user, often with a card, phone unlock, or smart card."),
    ("PIV", "Personal Identity Verification", "U.S. federal smart-card standard for employee identity and strong authentication."),
    ("PoE", "Power over Ethernet", "Technology that delivers electrical power and data over the same Ethernet cable to devices like APs and cameras."),
    ("POP", "Post Office Protocol", "Email retrieval protocol that typically downloads messages to a client and may remove them from the server."),
    ("POST", "Power-on Self-test", "Firmware diagnostic sequence that checks critical hardware before the OS boots."),
    ("PSU", "Power Supply Unit", "Component that converts wall AC power into the DC voltages a computer needs."),
    ("PUP", "Potentially Unwanted Program", "Software that is not outright malware but is undesirable (adware, toolbars, bundled junk)."),
    ("PXE", "Preboot eXecution Environment", "Network boot technology that lets a PC load an OS installer or image from a server."),
    ("QoS", "Quality of Service", "Networking techniques that prioritize certain traffic (voice, video) for better performance."),
    ("RADIUS", "Remote Authentication Dial-in User Server", "Centralized AAA protocol commonly used for VPN, Wi-Fi, and network device authentication."),
    ("RAID", "Redundant Array of Independent Disks", "Disk configuration that combines drives for performance, capacity, and/or fault tolerance."),
    ("RAM", "Random-access Memory", "Volatile working memory the CPU uses to store running programs and data."),
    ("RDP", "Remote Desktop Protocol", "Microsoft protocol that provides remote graphical desktop access to Windows systems."),
    ("ReFS", "Resilient File System", "Microsoft file system focused on integrity and resilience for large volumes and storage spaces."),
    ("RFID", "Radio-frequency Identification", "Wireless ID technology using tags and readers for access control, inventory, and tracking."),
    ("RGB", "Red-Green-Blue", "Additive color model used by displays and lighting where colors are mixed from red, green, and blue."),
    ("RISC", "Reduced Instruction Set Computer", "CPU design philosophy using a smaller, simpler instruction set for efficiency (as in ARM)."),
    ("RJ11", "Registered Jack Function 11", "Telephone connector typically used for landline/DSL with fewer contacts than RJ45."),
    ("RJ45", "Registered Jack Function 45", "Eight-position modular connector used for Ethernet networking cables."),
    ("RMM", "Remote Monitoring and Management", "MSP platform used to monitor, patch, and manage many client endpoints from one console."),
    ("RPM", "Revolutions Per Minute", "Speed measurement for spinning devices such as HDD platters or cooling fans."),
    ("RSR", "Rapid Security Response", "Fast security update mechanism (notably Apple) that delivers urgent fixes outside major OS releases."),
    ("SaaS", "Software as a Service", "Cloud model delivering applications over the internet (e.g., Microsoft 365, Google Workspace)."),
    ("SAML", "Security Assertions Markup Language", "XML-based standard for exchanging authentication/authorization data, often used for SSO."),
    ("SAN", "Storage Area Network", "High-speed dedicated network that provides block-level storage to servers."),
    ("SAS", "Serial Attached SCSI (Small Computer System Interface)", "Enterprise disk interface that connects servers to high-reliability SAS drives."),
    ("SATA", "Serial Advanced Technology Attachment", "Common interface for connecting internal HDDs and SSDs to a motherboard."),
    ("SC", "Subscriber Connector", "Square push-pull fiber-optic connector used in networking and telecom."),
    ("SCADA", "Supervisory Control and Data Acquisition", "Industrial control system used to monitor and operate infrastructure like plants and utilities."),
    ("SCSI", "Small Computer System Interface", "Legacy/enterprise peripheral interface for disks and other devices; ancestor concepts live on in SAS."),
    ("SD", "Secure Digital", "Removable flash memory card format used in cameras, phones, and embedded devices."),
    ("SDS", "Safety Data Sheet", "Document listing hazards, handling, and disposal guidance for a chemical or material (formerly MSDS)."),
    ("SFTP", "Secure File Transfer Protocol", "Encrypted file transfer method that runs over SSH instead of plaintext FTP."),
    ("SIM", "Subscriber Identity Module", "Card that stores mobile subscriber identity and authentication data for cellular service."),
    ("SLA", "Service-level Agreement", "Contract defining expected service performance, uptime, and response times between provider and customer."),
    ("S.M.A.R.T", "Self-monitoring Analysis and Reporting Technology", "Drive self-diagnostics that report health metrics to warn of impending disk failure."),
    ("SMB", "Server Message Block", "Windows file-and-printer sharing protocol used for networked resources."),
    ("SMS", "Short Message Service", "Cellular text messaging service used for communication and sometimes OTP delivery."),
    ("SMTP", "Simple Mail Transfer Protocol", "Protocol that sends email between mail clients and mail servers."),
    ("SNMP", "Simple Network Management Protocol", "Protocol for monitoring and managing network devices such as switches, routers, and printers."),
    ("SODIMM", "Small Outline Dual In-line Memory Module", "Compact RAM module form factor used in laptops and small-form-factor systems."),
    ("SOHO", "Small Office/Home Office", "Small business/home work environment with simpler networking and fewer users than enterprise."),
    ("SOP", "Standard Operating Procedure", "Documented step-by-step process for performing a routine IT or business task consistently."),
    ("SPF", "Sender Policy Framework", "Email DNS record that lists servers authorized to send mail for a domain."),
    ("SPICE", "Simple Protocol for Independent Computing Environments", "Remote-display protocol optimized for accessing virtual machines with graphics and clipboard sharing."),
    ("SQL", "Structured Query Language", "Standard language for querying and managing relational databases."),
    ("SSD", "Solid-state Drive", "Flash-based storage with no moving parts, offering higher speed and durability than HDDs."),
    ("SSH", "Secure Shell", "Encrypted remote command-line protocol that replaced insecure Telnet for administration."),
    ("SSID", "Service Set Identifier", "Human-readable name of a Wi-Fi network that clients see when scanning for wireless networks."),
    ("SSO", "Single Sign-on", "Authentication approach where one login grants access to multiple related applications."),
    ("ST", "Straight Tip", "Bayonet-style fiber-optic connector with a round ferrule, used in older fiber installations."),
    ("TACACS", "Terminal Access Controller Access-control System", "Cisco-oriented AAA protocol for authenticating administrators to network devices."),
    ("TCP", "Transmission Control Protocol", "Reliable, connection-oriented transport protocol that delivers ordered, acknowledged data streams."),
    ("TKIP", "Temporal Key Integrity Protocol", "Legacy WPA encryption/integrity mechanism superseded by stronger AES-based Wi-Fi security."),
    ("TN", "Twisted Nematic", "Fast, inexpensive LCD panel type with narrower viewing angles than IPS or VA."),
    ("TOTP", "Time-based One-time Password", "OTP algorithm that generates rotating codes based on the current time and a shared secret."),
    ("TPM", "Trusted Platform Module", "Secure cryptoprocessor chip that stores keys and supports features like BitLocker and measured boot."),
    ("TXT", "Text", "DNS record type that stores arbitrary text, often used for SPF, DKIM, and domain verification."),
    ("UAC", "User Account Control", "Windows security prompt that asks for elevation before allowing administrative actions."),
    ("UDP", "User Datagram Protocol", "Connectionless transport protocol used for fast, lightweight traffic such as DNS and streaming."),
    ("UEFI", "Unified Extensible Firmware Interface", "Modern firmware interface that replaces legacy BIOS with faster boot, GUI setup, and Secure Boot."),
    ("UPnP", "Universal Plug and Play", "Protocol that lets devices automatically open router ports; convenient but often a security risk."),
    ("UPS", "Uninterruptible Power Supply", "Battery-backed power device that keeps equipment running during outages and smooths power issues."),
    ("USB", "Universal Serial Bus", "Hot-pluggable interface for connecting peripherals, storage, and chargers to computers."),
    ("USB-C", "Universal Serial Bus Type C", "Reversible USB connector supporting data, video, and high-wattage power delivery."),
    ("UTM", "Unified Threat Management", "Security appliance that combines firewall, IDS/IPS, antivirus, and related protections in one box."),
    ("VA", "Vertical Alignment", "LCD panel technology with strong contrast, sitting between TN and IPS in viewing-angle performance."),
    ("VDI", "Virtual Desktop Infrastructure", "Architecture that hosts user desktops as VMs in a data center and streams them to thin clients."),
    ("VGA", "Video Graphics Array", "Legacy analog video connector and resolution standard historically used for PC monitors."),
    ("VLAN", "Virtual LAN (Local Area Network)", "Logical network segment created on switches to isolate broadcast domains without separate physical cabling."),
    ("VM", "Virtual Machine", "Software-emulated computer running an OS and apps on a hypervisor alongside other VMs."),
    ("VNC", "Virtual Network Computer", "Cross-platform remote desktop technology that shares a graphical desktop over the RFB protocol."),
    ("VoIP", "Voice over Internet Protocol", "Technology that carries voice calls as data packets over IP networks instead of traditional phone lines."),
    ("VPN", "Virtual Private Network", "Encrypted tunnel that securely connects a remote client or site to a private network over the internet."),
    ("VRAM", "Video Random-access Memory", "Memory used by a GPU to store textures, framebuffers, and other graphics data."),
    ("WAN", "Wide Area Network", "Network spanning large geographic areas, typically connecting multiple sites over ISP links."),
    ("WAP", "Wireless Access Point", "Device that bridges wireless clients onto a wired network (often used interchangeably with AP)."),
    ("WEP", "Wired Equivalent Privacy", "Obsolete Wi-Fi security protocol that is easily cracked and must not be used."),
    ("WinRM", "Windows Remote Management", "Microsoft service that enables remote PowerShell and management commands without a full desktop session."),
    ("WISP", "Written Internet Service Provider", "Provider of internet service (exam acronym expansion); in practice often refers to wireless ISPs serving rural areas."),
    ("WLAN", "Wireless LAN (Local Area Network)", "Local network that uses Wi-Fi radio instead of (or in addition to) Ethernet cabling."),
    ("WPA", "Wi-Fi Protected Access", "Family of Wi-Fi security standards (WPA/WPA2/WPA3) that encrypt and authenticate wireless traffic."),
    ("WWAN", "Wireless Wide Area Network", "Wide-area wireless connectivity such as cellular (LTE/5G) for mobile internet access."),
    ("XaaS", "Anything As A Service", "Broad term for delivering almost any IT capability as a cloud subscription service."),
    ("XDR", "Extended Detection and Response", "Security approach that correlates threat data across endpoints, email, cloud, and network for detection."),
    ("XFS", "Extended File System", "High-performance journaling file system commonly used on Linux for large volumes."),
    ("XSS", "Cross-site Scripting", "Web attack that injects malicious scripts into pages viewed by other users to steal data or hijack sessions."),
]

# Prefer dedicated files in 5.1/; fall back to clear matches from other folders.
BORROWED_IMAGES = {
    "AAA": "2.3/RADIUS.png",
    "ACL": "2.1/Access control lists (ACLs).png",
    "AES": "2.3/AES.png",
    "AP": "3.2/Connectivity issues Wi-Fi.jfif",
    "APFS": "1.1/apfs-logo.jpg",
    "AUP": "4.6/Acceptable Use Policy (AUP).png",
    "BEC": "2.5/Business email compromise (BEC).webp",
    "BIOS": "2.10/Firmware updates.jpg",
    "BSOD": "3.1/Blue screen of death (BSOD).png",
    "BYOD": "2.5/Bring Your Own Device (BYOD).png",
    "CAC": "2.1/Smart cards.png",
    "DDoS": "2.5/Distributed Denial of Service (DDoS).png",
    "DKIM": "2.1/Email auth.png",
    "DLP": "2.1/Data loss prevention (DLP).png",
    "DMARC": "2.1/Email auth.png",
    "DNS": "2.11/Secure DNS.jpg",
    "DoS": "2.5/Denial of Service (DoS).jpg",
    "EDR": "2.4/Endpoint Detection & Response (EDR).jpg",
    "EFS": "2.7/File system encryption.webp",
    "EOL": "2.5/End-of-life (EOL).jfif",
    "ESD": "4.4/ESD straps.jfif",
    "EULA": "4.6/Valid licenses.jfif",
    "FAT32": "1.1/fat32.webp",
    "FRT": "2.1/Facial recognition technology (FRT).png",
    "GFS": "4.3/Grandfather-Father-Son (GFS).jfif",
    "GPS": "2.8/Locator applications.png",
    "GPT": "1.2/gpt-partition-table.webp",
    "GUID": "1.2/GUID.png",
    "HDD": "1.2/Internal hard drive (partition).png",
    "HSM": "2.1/Hardware token.png",
    "IAM": "2.1/Identity access management (IAM).png",
    "LDAP": "2.1/Directory services.png",
    "MBR": "1.2/mbr.webp",
    "MDM": "2.8/MDM (Mobile Device Management).jpg",
    "MDR": "2.4/Managed Detection & Response (MDR).jpg",
    "MFA": "2.1/Multifactor authentication (MFA).png",
    "MNDA": "4.6/NDA  MNDA.png",
    "NAT": "2.10/Port forwarding  mapping.jfif",
    "NDA": "4.6/NDA  MNDA.png",
    "NFC": "3.2/Connectivity issues Near-field communication (NFC).webp",
    "NTFS": "1.1/NTFS.jpg",
    "NTP": "3.1/Time drift.png",
    "OS": "1.1/Operating System.jfif",
    "OTP": "2.1/One-time password  passcode (OTP).png",
    "PAM": "2.1/Privileged access management (PAM).png",
    "PAN": "3.2/Connectivity issues Bluetooth.jfif",
    "PII": "4.6/PII Personally Identifiable Information.png",
    "PIV": "2.1/Smart cards.png",
    "PUP": "2.4/Potentially Unwanted Program (PUP).jpeg",
    "PXE": "1.2/PXE_diagram.png",
    "RADIUS": "2.3/RADIUS.png",
    "RAM": "1.3/RAM limitations.jfif",
    "RDP": "4.9/RDP.jpeg",
    "ReFS": "1.1/refs.png",
    "RFID": "2.1/Key fobs.png",
    "RMM": "4.9/RMM.png",
    "SAML": "2.1/Security Assertions Markup Language (SAML).png",
    "SAN": "1.2/IBM_TotalStorage_Exp400.jpg",
    "SDS": "4.5/MSDS  SDS documentation.jfif",
    "SLA": "4.1/Service-level agreements (SLAs).png",
    "SMS": "2.1/Short Message Service (SMS).png",
    "SOP": "4.1/Standard operating procedures (SOPs).webp",
    "SPF": "2.1/Email auth.png",
    "SPICE": "4.9/SPICE.jpg",
    "SQL": "2.5/SQL injection (SQLi).jpg",
    "SSD": "1.2/Solid-state  flash drives.jfif",
    "SSH": "4.9/SSH.png",
    "SSID": "2.10/Changing the service set identifier (SSID).jpg",
    "SSO": "2.1/Single sign-on (SSO).png",
    "TACACS": "2.3/TACACS+.png",
    "TKIP": "2.3/TKIP.png",
    "TOTP": "2.1/Time-based one-time password (TOTP).png",
    "TPM": "1.3/TPM.png",
    "UEFI": "1.3/UEFI.webp",
    "UPnP": "2.10/Universal Plug and Play (UPnP).jfif",
    "UPS": "4.5/Uninterruptible Power Supply (UPS).jfif",
    "USB": "1.2/ktc-usb-flash-drives-differences-usb-2-gen1-gen2-og.jpg",
    "VNC": "4.9/VNC.webp",
    "VoIP": "2.1/Voice call.png",
    "VPN": "4.9/VPN.jfif",
    "WAP": "3.2/Connectivity issues Wi-Fi.jfif",
    "WinRM": "4.9/WinRM.jfif",
    "WLAN": "3.2/Connectivity issues Wi-Fi.jfif",
    "WPA": "2.3/WPA2.png",
    "XDR": "2.4/Extended Detection & Response (XDR).jpg",
    "XFS": "1.1/xfs_linux.webp",
    "XSS": "2.5/Cross-site scripting (XSS).jpg",
}

_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".jfif", ".gif", ".svg"}
_ACRONYM_FILE_ALIASES = {
    "DB-9": ("DB9",),
    "USB-C": ("USBC",),
    "S.M.A.R.T": ("SMART", "S.M.A.R.T"),
}


def _norm_key(value: str) -> str:
    return "".join(ch for ch in value.upper() if ch.isalnum())


def build_image_map() -> dict[str, str]:
    """Map acronyms to images: 5.1/ first, then borrowed fallbacks."""
    folder = ROOT / "5.1"
    by_key: dict[str, str] = {}
    if folder.is_dir():
        # Prefer sharper formats when duplicates exist (e.g. SMB.webp over SMB.jfif).
        rank = {".svg": 0, ".png": 1, ".webp": 2, ".jpg": 3, ".jpeg": 3, ".gif": 4, ".jfif": 5}
        for path in folder.iterdir():
            if not path.is_file() or path.suffix.lower() not in _IMAGE_EXTS:
                continue
            key = _norm_key(path.stem.strip())
            rel = path.relative_to(ROOT).as_posix()
            prev = by_key.get(key)
            if prev is None:
                by_key[key] = rel
                continue
            prev_ext = Path(prev).suffix.lower()
            if rank.get(path.suffix.lower(), 9) < rank.get(prev_ext, 9):
                by_key[key] = rel

    image_map: dict[str, str] = {}
    for acronym, _, _ in ACRONYMS:
        keys = [_norm_key(acronym), *[ _norm_key(a) for a in _ACRONYM_FILE_ALIASES.get(acronym, ()) ]]
        local = next((by_key[k] for k in keys if k in by_key), None)
        if local:
            image_map[acronym] = local
        elif acronym in BORROWED_IMAGES:
            image_map[acronym] = BORROWED_IMAGES[acronym]
    return image_map


IMAGE_MAP = build_image_map()


def letter_group(acronym: str) -> str:
    first = acronym[0].upper()
    if first in "ABC":
        return "A–C"
    if first in "DEF":
        return "D–F"
    if first in "GHI":
        return "G–I"
    if first in "JKLM":
        return "J–M"
    if first in "NOP":
        return "N–P"
    if first in "QR":
        return "Q–R"
    if first in "ST":
        return "S–T"
    return "U–Z"


def group_id(label: str) -> str:
    return "group-" + label.replace("–", "-").lower()


def term_title(acronym: str, expansion: str) -> str:
    return f"{acronym} ({expansion})"


def build_study_guide(image_map: dict[str, str] | None = None) -> str:
    image_map = image_map or IMAGE_MAP
    groups: dict[str, list[tuple[str, str, str]]] = {}
    order = ["A–C", "D–F", "G–I", "J–M", "N–P", "Q–R", "S–T", "U–Z"]
    for label in order:
        groups[label] = []
    for acronym, expansion, purpose in ACRONYMS:
        groups[letter_group(acronym)].append((acronym, expansion, purpose))

    toc_links = "\n".join(
        f'    <a href="#{group_id(label)}">{html.escape(label)}</a>' for label in order
    )
    hero_parts = []
    for i, label in enumerate(order):
        cls = ' class="ghost"' if i else ""
        hero_parts.append(f'      <a{cls} href="#{group_id(label)}">{html.escape(label)}</a>')
    hero_cta = "\n".join(hero_parts)

    sections = []
    for i, label in enumerate(order):
        items = groups[label]
        articles = []
        for acronym, expansion, purpose in items:
            aid = (
                acronym.lower()
                .replace(".", "")
                .replace("/", "-")
                .replace(" ", "-")
            )
            title = term_title(acronym, expansion)
            img = image_map.get(acronym)
            if img:
                visual = (
                    f'<div class="visual photo">'
                    f'<img src="{html.escape(img)}" alt="{html.escape(title)}" loading="lazy">'
                    f"</div>"
                )
            else:
                visual = (
                    f'<div class="visual acronym" aria-hidden="true">'
                    f"{html.escape(acronym)}</div>"
                )
            articles.append(
                f"""
      <article class="term" id="{html.escape(aid)}">
        {visual}
        <div class="body">
          <h3>{html.escape(title)}</h3>
          <p>{html.escape(purpose)}</p>
        </div>
      </article>"""
            )
        sections.append(
            f"""
  <section id="{group_id(label)}">
    <div class="wrap">
      <div class="section-head">
        <span class="eyebrow">Part {chr(65 + i)}</span>
        <h2>Acronyms {html.escape(label)}</h2>
        <p>{len(items)} exam acronyms starting with letters {html.escape(label)}.</p>
      </div>
{''.join(articles)}
    </div>
  </section>"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>5.1 CompTIA A+ Acronyms</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,550;9..144,700&family=Sora:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{{
    --ink:#101820;
    --muted:#4b5563;
    --paper:#f4f1ea;
    --line:rgba(16,24,32,0.12);
    --accent:#0f766e;
    --accent-soft:#ccfbf1;
    --sky:#0e4d7b;
    --highlight:#0d9488;
  }}
  *{{ box-sizing:border-box; }}
  html{{ scroll-behavior:smooth; }}
  body{{
    margin:0;
    color:var(--ink);
    font-family:"Sora",sans-serif;
    background:
      radial-gradient(900px 500px at 90% -10%, rgba(15,118,110,0.12), transparent 55%),
      radial-gradient(700px 420px at -10% 20%, rgba(14,77,123,0.06), transparent 50%),
      linear-gradient(180deg, #ebe8e0 0%, var(--paper) 40%, #f0ece4 100%);
    line-height:1.55;
  }}
  a{{ color:var(--highlight); }}
  .wrap{{ width:min(1080px, calc(100% - 2.4rem)); margin:0 auto; }}

  .hero{{
    position:relative;
    min-height:100vh;
    display:flex;
    align-items:flex-end;
    color:#f0fdfa;
    overflow:hidden;
  }}
  .hero::before{{
    content:"";
    position:absolute; inset:0;
    background:
      linear-gradient(180deg, rgba(8,28,26,0.55) 0%, rgba(8,28,26,0.78) 52%, rgba(8,28,26,0.94) 100%),
      url("https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1600&q=80") center/cover no-repeat;
  }}
  .hero-inner{{
    position:relative;
    z-index:1;
    width:min(1080px, calc(100% - 2.4rem));
    margin:0 auto 4.2rem;
  }}
  .brand{{
    font-family:"Fraunces",serif;
    font-size:clamp(3.4rem, 10vw, 6.6rem);
    font-weight:700;
    line-height:0.92;
    letter-spacing:-0.03em;
    margin:0 0 0.85rem;
  }}
  .hero h1{{
    margin:0 0 0.65rem;
    font-size:clamp(1.05rem, 2.1vw, 1.35rem);
    font-weight:500;
    max-width:40ch;
    color:#ccfbf1;
  }}
  .hero > .hero-inner > p{{
    margin:0 0 1.5rem;
    max-width:52ch;
    color:#94a3b8;
  }}
  .hero-cta{{ display:flex; flex-wrap:wrap; gap:0.7rem; }}
  .hero-cta a{{
    text-decoration:none;
    font-weight:600;
    font-size:0.92rem;
    padding:0.7rem 1.15rem;
    border-radius:999px;
    background:#ccfbf1;
    color:#134e4a;
  }}
  .hero-cta a.ghost{{
    background:transparent;
    color:#ccfbf1;
    border:1px solid rgba(204,251,241,0.4);
  }}

  .toc{{
    position:sticky; top:0; z-index:30;
    backdrop-filter:blur(12px);
    background:rgba(244,241,234,0.92);
    border-bottom:1px solid var(--line);
  }}
  .toc .wrap{{
    display:flex; gap:0.3rem; overflow-x:auto;
    padding:0.7rem 0; scrollbar-width:thin;
  }}
  .toc a{{
    flex:0 0 auto;
    text-decoration:none;
    color:var(--muted);
    font-size:0.78rem;
    font-weight:600;
    padding:0.42rem 0.75rem;
    border-radius:999px;
  }}
  .toc a:hover{{ background:var(--accent-soft); color:var(--accent); }}

  section{{ padding:3.1rem 0 0.5rem; }}
  .section-head{{ margin-bottom:1.4rem; max-width:46rem; }}
  .eyebrow{{
    display:inline-block;
    font-size:0.72rem;
    font-weight:700;
    letter-spacing:0.08em;
    text-transform:uppercase;
    color:var(--accent);
    margin-bottom:0.5rem;
  }}
  .section-head h2{{
    font-family:"Fraunces",serif;
    font-size:clamp(1.75rem, 3.4vw, 2.5rem);
    margin:0 0 0.5rem;
    letter-spacing:-0.02em;
    line-height:1.12;
  }}
  .section-head p{{ margin:0; color:var(--muted); }}

  .term{{
    display:grid;
    grid-template-columns:minmax(120px, 180px) 1fr;
    gap:1.35rem 1.7rem;
    align-items:start;
    padding:1.2rem 0;
    border-top:1px solid var(--line);
  }}
  .term:last-of-type{{ border-bottom:1px solid var(--line); }}
  .visual{{
    border:1px solid var(--line);
    border-radius:18px;
    min-height:110px;
    display:flex;
    align-items:center;
    justify-content:center;
    overflow:hidden;
    background:linear-gradient(160deg, #fff, var(--accent-soft));
  }}
  .visual.acronym{{
    font-family:"Fraunces",serif;
    font-size:clamp(1.15rem, 2.4vw, 1.55rem);
    font-weight:700;
    color:var(--accent);
    letter-spacing:-0.02em;
    padding:0.75rem;
    text-align:center;
    line-height:1.15;
    word-break:break-word;
  }}
  .visual.photo{{ padding:0; cursor:zoom-in; }}
  .visual.photo img{{
    width:100%;
    height:140px;
    object-fit:cover;
    display:block;
  }}

  .body h3{{
    font-family:"Fraunces",serif;
    font-size:1.25rem;
    margin:0 0 0.45rem;
    letter-spacing:-0.01em;
  }}
  .body p{{ margin:0; color:var(--ink); }}

  footer{{
    padding:2.4rem 0 3.2rem;
    color:var(--muted);
    font-size:0.84rem;
  }}
  footer .wrap{{
    border-top:1px solid var(--line);
    padding-top:1.2rem;
  }}

  @media (max-width:780px){{
    .term{{ grid-template-columns:1fr; }}
    .hero-inner{{ margin-bottom:3rem; }}
  }}
</style>
</head>
<body>

<header class="hero">
  <div class="hero-inner">
    <p class="brand">5.1</p>
    <h1>CompTIA A+ Acronyms</h1>
    <p>{len(ACRONYMS)} exam acronyms with full expansions and what each one is used for.</p>
    <div class="hero-cta">
{hero_cta}
    </div>
  </div>
</header>

<nav class="toc" aria-label="On this page">
  <div class="wrap">
{toc_links}
  </div>
</nav>

<main>
{''.join(sections)}
</main>

<footer>
  <div class="wrap">
    Study notes for Core 2 Chapter 5 — CompTIA A+ Acronyms ({len(ACRONYMS)} terms).
    <a href="Chapter 5 Practice Quiz.html?start=1">Practice quiz</a> ·
    <a href="index.html">All guides</a>
  </div>
</footer>

<script src="study-lightbox.js"></script>
</body>
</html>
"""


def section_meta(acronym: str) -> tuple[str, str]:
    """Return (section_id, display_label) for letter-range quiz filters."""
    label = letter_group(acronym)
    return label.replace("–", "-"), label


def main():
    global IMAGE_MAP
    IMAGE_MAP = build_image_map()
    guide_path = ROOT / "5.1 CompTIA A+ Acronyms.html"
    guide_html = build_study_guide(IMAGE_MAP)
    guide_html = guide_html.replace(
        'href="Chapter 5 Practice Quiz.html?start=1"',
        'href="Chapter 5 Practice Quiz.html"',
    )
    guide_path.write_text(guide_html, encoding="utf-8")
    imaged = sum(1 for a, _, _ in ACRONYMS if a in IMAGE_MAP)
    missing = [a for a, _, _ in ACRONYMS if a not in IMAGE_MAP]
    print(f"Wrote {guide_path.name} ({len(ACRONYMS)} acronyms, {imaged} with images)")
    if missing:
        print(f"Still letter-only: {', '.join(missing)}")

    order = ["A–C", "D–F", "G–I", "J–M", "N–P", "Q–R", "S–T", "U–Z"]
    sections = []
    terms = []
    counts = {label: 0 for label in order}

    for i, (acronym, expansion, purpose) in enumerate(ACRONYMS):
        label = letter_group(acronym)
        section_id = label.replace("–", "-")
        counts[label] += 1
        terms.append(
            {
                "id": f"5.1-{i}",
                "section": section_id,
                "sectionTitle": f"Acronyms {label}",
                "category": f"Acronyms {label}",
                "name": term_title(acronym, expansion),
                "definition": purpose,
            }
        )

    for label in order:
        section_id = label.replace("–", "-")
        sections.append(
            {
                "id": section_id,
                "title": f"Acronyms {label}",
                "file": "5.1 CompTIA A+ Acronyms.html",
                "count": counts[label],
            }
        )
        print(f"{section_id}: {counts[label]} terms")

    data = {
        "chapter": 5,
        "title": "Chapter 5 — Acronyms",
        "sections": sections,
        "terms": terms,
        "total": len(terms),
    }

    json_path = ROOT / "chapter5-quiz-data.json"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {json_path.name}")

    page = quiz_page_html(
        chapter=5,
        title=data["title"],
        range_label="5.1 letter ranges",
        accent="#0f766e",
        accent_soft="#ccfbf1",
    )
    page = page.replace(
        "study guides and interactive simulators.",
        "acronym expansions and purposes — pick a letter range to start.",
    )
    page = page.replace("Start a section", "Start a letter range")
    page = page.replace("Quiz all sections", "Quiz all letter ranges")
    page = page.replace("Or combine sections", "Or combine letter ranges")
    page = page.replace(
        "Click a section to start instantly.",
        "Click a letter range to start instantly.",
    )
    quiz_path = ROOT / "Chapter 5 Practice Quiz.html"
    quiz_path.write_text(
        page.replace("/*__QUIZ_DATA__*/", json.dumps(data, ensure_ascii=False)),
        encoding="utf-8",
    )
    print(f"Wrote {quiz_path.name}")


if __name__ == "__main__":
    main()
