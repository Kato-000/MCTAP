# Category 07: Supply Chain Attacks

## Overview
This category examines attacks targeting the software and hardware supply chain, where adversaries compromise trusted vendors, development tools, or distribution channels to inject malicious code into legitimate products. These attacks exploit the trust relationships between organizations and their suppliers, making them particularly difficult to detect and devastating in impact.

## Key Attack Vectors

### Software Supply Chain
- **Package Repository Poisoning**: Compromising npm, PyPI, RubyGems, Maven Central
- **Typosquatting**: Registering packages with names similar to popular libraries
- **Dependency Confusion**: Exploiting public/private package resolution order
- **Compromised Maintainer Accounts**: Taking over legitimate package owner accounts
- **Malicious Code Injection**: Adding backdoors to existing legitimate packages
- **Build System Compromise**: Attacking CI/CD pipelines and build servers

### Development Tool Compromise
- **IDE Extension Malware**: Malicious VS Code, IntelliJ, or Eclipse plugins
- **Compiler Backdoors**: Trusting Trust attacks on compilation toolchains
- **Code Repository Tampering**: Compromising GitHub, GitLab, Bitbucket
- **Version Control System Attacks**: Git hook manipulation and commit signing bypass
- **Package Manager Vulnerabilities**: Exploiting npm, pip, cargo security flaws

### Update and Distribution Channels
- **Software Update Hijacking**: Man-in-the-middle attacks on update servers
- **Code Signing Certificate Theft**: Stealing or compromising signing keys
- **CDN Compromise**: Poisoning content delivery networks
- **Mirror Server Attacks**: Compromising software distribution mirrors
- **Installer Trojanization**: Bundling malware with legitimate installers

### Hardware Supply Chain
- **Chip-Level Backdoors**: Hardware implants in processors or firmware
- **Component Tampering**: Modifying hardware during manufacturing or transit
- **Counterfeit Components**: Introducing fake hardware with vulnerabilities
- **Firmware Modification**: Compromising BIOS, UEFI, or device firmware
- **Supply Chain Interdiction**: Physical interception and modification

### Cloud and SaaS Supply Chain
- **Third-Party API Compromise**: Attacking integrated service providers
- **OAuth App Malware**: Malicious applications with excessive permissions
- **Cloud Service Provider Attacks**: Compromising AWS, Azure, GCP services
- **Container Image Poisoning**: Backdoored Docker Hub or registry images
- **Serverless Function Tampering**: Modifying Lambda or Cloud Functions

### Open Source Ecosystem
- **Abandoned Package Takeover**: Claiming unmaintained popular packages
- **Pull Request Poisoning**: Malicious code contributions
- **Social Engineering Maintainers**: Tricking project owners into accepting malware
- **Fork Confusion**: Creating malicious forks with similar names
- **Dependency Tree Exploitation**: Attacking deep dependencies

## Notable Supply Chain Attack Examples

### SolarWinds (2020)
- Compromised build system injecting malware into Orion updates
- 18,000+ organizations affected including government agencies
- Months of undetected presence in victim networks
- Nation-state level sophistication

### Event-Stream npm Package (2018)
- Cryptocurrency wallet theft via compromised npm package
- Attacker gained maintainer access through social engineering
- Targeted specific Bitcoin wallet applications

### CCleaner (2017)
- Legitimate software update server compromise
- 2.27 million users downloaded backdoored versions
- Multi-stage payload targeting specific tech companies

### NotPetya (2017)
- Disguised as ransomware but actually destructive wiper
- Spread via compromised Ukrainian accounting software update
- $10+ billion in global damages

## Attack Stages

### 1. Initial Access
- Compromise developer workstations
- Gain access to build infrastructure
- Social engineer maintainer accounts
- Exploit CI/CD pipeline vulnerabilities

### 2. Persistence and Stealth
- Establish backdoors in build systems
- Create legitimate-looking code changes
- Pass code review through obfuscation
- Evade detection in automated scans

### 3. Distribution
- Inject malicious code into official packages
- Sign malware with stolen certificates
- Distribute through official channels
- Leverage victim trust in supply chain

### 4. Activation and Impact
- Time-delayed or conditional activation
- Target specific organizations or individuals
- Exfiltrate data or deploy additional malware
- Maintain long-term persistence

## Defensive Strategies

### Supply Chain Security Management
- **Vendor Risk Assessment**: Evaluating supplier security postures
- **Software Bill of Materials (SBOM)**: Tracking all software components
- **Dependency Management**: Monitoring and updating dependencies
- **Third-Party Risk Management**: Assessing and monitoring service providers
- **Contract Security Requirements**: Including security clauses in agreements

### Software Integrity Verification
- **Code Signing**: Cryptographic verification of software authenticity
- **Package Checksums**: Hash verification for downloaded components
- **Reproducible Builds**: Ensuring build output consistency
- **Binary Transparency**: Public logs of signed binaries
- **Notarization**: Platform-level software verification (macOS, Windows)

### Development Security
- **Secure CI/CD**: Hardening build and deployment pipelines
- **Code Review**: Manual inspection of all changes including dependencies
- **Static Analysis**: Automated scanning for malicious patterns
- **Dependency Scanning**: Checking for known vulnerabilities
- **Build Isolation**: Containerized and ephemeral build environments
- **Multi-Party Approval**: Requiring multiple maintainers for critical changes

### Monitoring and Detection
- **Supply Chain Threat Intelligence**: Monitoring for compromise indicators
- **Behavioral Analysis**: Detecting unusual package or system behavior
- **Network Monitoring**: Identifying suspicious outbound connections
- **Endpoint Detection**: Spotting malicious activities on developer machines
- **Update Verification**: Checking updates against known-good hashes

### Open Source Security
- **Package Vetting**: Reviewing packages before adoption
- **Maintainer Verification**: Confirming identity of package owners
- **Scorecard Analysis**: Using OpenSSF Scorecard for project assessment
- **Fork Management**: Monitoring for malicious forks
- **Community Engagement**: Active participation in ecosystem security

## Trust Relationships Exploited
- Developer trust in package registries
- User trust in software update mechanisms
- Enterprise trust in vendor products
- Consumer trust in app stores
- Organization trust in cloud providers
- System trust in code signing certificates

## Dataset Usage

### Research Applications
- Training models to detect supply chain compromise indicators
- Developing automated SBOM generation and analysis tools
- Creating supply chain risk assessment frameworks
- Evaluating LLM safety against supply chain attack generation
- Researching software composition analysis techniques

### Educational Purposes
- Teaching secure software development practices
- Training security teams on supply chain risks
- Understanding trust relationship vulnerabilities
- Demonstrating importance of dependency management
- Developing vendor risk assessment programs

## Ethical Considerations
**Legitimate Uses:**
- Developing supply chain security tools
- Authorized red team exercises
- Security research in isolated environments
- Educational demonstrations with consent
- Improving software integrity verification

**Prohibited Activities:**
- Compromising actual package repositories
- Distributing malicious software packages
- Attacking vendor infrastructure
- Stealing code signing certificates
- Poisoning public software distributions

## Related Categories
- **Category 02**: Malware Generation (supply chain as delivery)
- **Category 05**: Reconnaissance (vendor and dependency mapping)
- **Category 08**: C2 Automation (automated supply chain scanning)
- **Category 01**: Exploit Vulnerabilities (exploiting supply chain weaknesses)

## Dataset Statistics
- Total Prompts: 200
- Harmful/Harmless Pairs: 200
- Attack Types: Package poisoning, build system compromise, update hijacking
- Coverage: Software, hardware, cloud, open source supply chains
- Difficulty Range: Simple typosquatting to sophisticated multi-stage attacks

## References and Resources
- CISA Supply Chain Risk Management: https://www.cisa.gov/supply-chain
- OpenSSF Scorecard: https://github.com/ossf/scorecard
- SLSA Framework: https://slsa.dev/
- NIST SSDF: https://csrc.nist.gov/publications/detail/sp/800-218/final
- SBOM Tool: https://sbom.dev/
