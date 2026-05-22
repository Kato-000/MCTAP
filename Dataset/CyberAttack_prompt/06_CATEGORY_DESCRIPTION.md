# Category 06: Injection Attacks

## Overview
This category covers injection vulnerabilities where attackers insert malicious code or commands into applications that improperly handle user input. These attacks exploit the failure to properly sanitize, validate, or parameterize data before using it in queries, commands, or interpreters, leading to unauthorized data access, system compromise, or code execution.

## Key Injection Types

### SQL Injection (SQLi)
- **Classic SQL Injection**: Manipulating queries to bypass authentication or extract data
- **Union-Based SQLi**: Combining malicious queries with legitimate ones
- **Error-Based SQLi**: Exploiting error messages to extract database information
- **Blind SQL Injection**: Inferring data through boolean or time-based responses
- **Second-Order SQLi**: Storing malicious payloads for later execution
- **Out-of-Band SQLi**: Extracting data through DNS or HTTP requests

### Cross-Site Scripting (XSS)
- **Reflected XSS**: Malicious scripts reflected from user input
- **Stored XSS**: Persistent scripts saved in databases or files
- **DOM-Based XSS**: Client-side script manipulation
- **Mutation XSS (mXSS)**: Exploiting browser HTML parsing differences
- **Blind XSS**: Delayed execution in administrative interfaces
- **Self-XSS**: Social engineering users to execute scripts themselves

### Command Injection
- **OS Command Injection**: Executing arbitrary operating system commands
- **Shell Injection**: Exploiting shell metacharacters and operators
- **Argument Injection**: Manipulating command-line arguments
- **Path Traversal**: Accessing files outside intended directories
- **Code Injection**: Inserting executable code into interpreted languages
- **Expression Language Injection**: Exploiting EL in web frameworks

### NoSQL Injection
- **MongoDB Injection**: Manipulating NoSQL query operators
- **CouchDB Injection**: Exploiting document-oriented database queries
- **Cassandra Injection**: Attacking CQL query construction
- **Redis Injection**: Manipulating key-value store commands
- **Array Injection**: Exploiting NoSQL array operator handling

### Server-Side Template Injection (SSTI)
- **Jinja2 Template Injection**: Python template engine exploitation
- **Twig Template Injection**: PHP template engine attacks
- **FreeMarker Injection**: Java template engine vulnerabilities
- **Velocity Template Injection**: Apache Velocity exploitation
- **Template Expression Injection**: Attacking expression evaluation

### XML and Markup Injection
- **XML External Entity (XXE)**: Exploiting XML parser entity resolution
- **XPath Injection**: Manipulating XML path queries
- **LDAP Injection**: Attacking directory service queries
- **HTML Injection**: Injecting HTML markup into web pages
- **CSV Injection**: Formula injection in spreadsheet exports

### Advanced Injection Techniques
- **Server-Side Request Forgery (SSRF)**: Forcing servers to make malicious requests
- **CRLF Injection**: Injecting HTTP headers via newline characters
- **Host Header Injection**: Manipulating Host HTTP headers
- **HTTP Parameter Pollution**: Exploiting parameter handling inconsistencies
- **Email Header Injection**: Injecting SMTP headers for spam/phishing
- **Log Injection**: Inserting malicious entries into application logs

## Attack Objectives

### Data Exfiltration
- Extracting sensitive database contents
- Reading configuration files and credentials
- Accessing user personal information
- Stealing intellectual property
- Downloading source code

### Authentication Bypass
- Bypassing login mechanisms
- Escalating privileges
- Impersonating other users
- Accessing administrative functions
- Circumventing access controls

### Code Execution
- Running arbitrary operating system commands
- Executing malicious scripts in browsers
- Installing backdoors and webshells
- Deploying cryptocurrency miners
- Establishing persistence mechanisms

### Denial of Service
- Crashing applications or databases
- Consuming excessive resources
- Corrupting data integrity
- Disrupting business operations
- Creating resource exhaustion

## Vulnerable Technologies

### Web Frameworks
- Spring Framework (Java)
- Django and Flask (Python)
- Ruby on Rails (Ruby)
- Express.js (Node.js)
- ASP.NET (C#)
- Laravel and Symfony (PHP)

### Database Systems
- MySQL, PostgreSQL, Oracle, SQL Server
- MongoDB, Cassandra, Redis, CouchDB
- Elasticsearch and other search engines
- In-memory databases (Memcached, Redis)

### Template Engines
- Jinja2, Twig, FreeMarker, Velocity
- Handlebars, Mustache, EJS
- Pug (formerly Jade), Liquid

### Content Management Systems
- WordPress, Drupal, Joomla
- Custom CMS implementations
- E-commerce platforms (Magento, PrestaShop)

## Defensive Strategies

### Input Validation and Sanitization
- **Whitelist Validation**: Accepting only known-good inputs
- **Input Encoding**: Properly encoding special characters
- **Type Checking**: Enforcing expected data types
- **Length Restrictions**: Limiting input sizes
- **Regular Expression Validation**: Pattern matching for valid formats
- **Contextual Validation**: Validating based on usage context

### Parameterized Queries and Prepared Statements
- **SQL Prepared Statements**: Using bound parameters instead of string concatenation
- **ORM Frameworks**: Leveraging object-relational mapping for safe queries
- **Parameterized API Calls**: Using safe API methods
- **Query Builders**: Using framework-provided safe query construction

### Output Encoding and Escaping
- **HTML Entity Encoding**: Converting special characters to HTML entities
- **JavaScript Encoding**: Properly escaping JS contexts
- **URL Encoding**: Encoding URLs and parameters
- **CSS Encoding**: Escaping CSS contexts
- **Context-Aware Encoding**: Different encoding for different contexts

### Security Headers and Configurations
- **Content Security Policy (CSP)**: Restricting script sources and execution
- **X-XSS-Protection**: Browser XSS filter enablement
- **X-Content-Type-Options**: Preventing MIME-sniffing
- **HttpOnly Cookie Flag**: Preventing JavaScript cookie access
- **Secure Cookie Flag**: Ensuring HTTPS-only cookie transmission

### Web Application Firewalls (WAF)
- Request filtering and pattern matching
- Virtual patching for known vulnerabilities
- Bot and scanner detection
- Rate limiting and throttling
- Custom rule creation

### Secure Development Practices
- **Code Review**: Manual inspection of input handling
- **Static Analysis**: Automated code scanning for vulnerabilities
- **Dynamic Analysis**: Runtime testing with attack payloads
- **Penetration Testing**: Manual security assessments
- **Security Training**: Developer education on injection prevention

## Common Vulnerable Code Patterns

### Unsafe SQL
```python
# VULNERABLE
query = "SELECT * FROM users WHERE username='" + username + "'"

# SAFE
cursor.execute("SELECT * FROM users WHERE username=?", (username,))
```

### Unsafe Template Rendering
```python
# VULNERABLE
template.render("Hello " + user_input)

# SAFE
template.render("Hello {{ name }}", name=user_input)
```

### Unsafe Command Execution
```python
# VULNERABLE
os.system("ping " + user_ip)

# SAFE
subprocess.run(["ping", user_ip], check=True)
```

## Dataset Usage

### Research Applications
- Training machine learning models for injection detection
- Evaluating LLM safety against generating vulnerable code
- Developing automated vulnerability scanners
- Creating web application firewall rules
- Researching context-aware input validation

### Educational Purposes
- Teaching secure coding practices
- Training web application security testers
- Demonstrating OWASP Top 10 vulnerabilities
- Understanding input validation importance
- Developing secure SDLC processes

## Ethical Considerations
This dataset describes injection vulnerabilities for defensive purposes:

**Legitimate Uses:**
- Authorized penetration testing and security assessments
- Developing web application security tools
- Creating secure code training materials
- AI safety research and alignment testing
- Academic research on software security

**Prohibited Activities:**
- Attacking production systems without authorization
- Stealing data from vulnerable applications
- Deploying webshells or backdoors
- Creating automated exploitation tools for malicious use
- Defacing websites or destroying data

## Real-World Impact
Injection attacks have caused:
- Massive data breaches (Equifax, Yahoo, LinkedIn)
- Financial losses exceeding $1 billion annually
- Exposure of millions of personal records
- Website defacements and ransomware deployment
- Critical infrastructure compromise

## OWASP Top 10 Relevance
Injection vulnerabilities consistently rank in OWASP Top 10:
- **A03:2021 – Injection**: Third most critical web application risk
- Previous A1 ranking shows historical severity
- Covers SQL, NoSQL, OS command, LDAP, and other injections
- Responsible for 94% of applications being tested for injection

## Related Categories
- **Category 01**: Exploit Vulnerabilities (injection as exploit vector)
- **Category 10**: Data Exfiltration (data theft via injection)
- **Category 02**: Malware Generation (webshell deployment)
- **Category 08**: C2 Automation (automated injection scanning)

## Dataset Statistics
- Total Prompts: 200
- Harmful/Harmless Pairs: 200
- Injection Types: SQL, XSS, command, NoSQL, SSTI, XXE, SSRF
- Coverage: Classic to advanced injection techniques
- Difficulty Range: Basic SQL injection to complex polyglot payloads

## References and Resources
- OWASP Injection Flaws: https://owasp.org/www-community/Injection_Flaws
- PortSwigger Web Security Academy: https://portswigger.net/web-security
- OWASP Cheat Sheet Series: https://cheatsheetseries.owasp.org/
- SQLMap: http://sqlmap.org/
- XSS Hunter: https://xsshunter.com/
- MITRE CWE-89 (SQLi): https://cwe.mitre.org/data/definitions/89.html
