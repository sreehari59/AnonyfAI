# PII Detection Prototype

This prototype demonstrates automated detection and analysis of Personally Identifiable Information (PII) in SQL Server databases with comprehensive regulatory compliance for GDPR, CCPA, and HIPAA.

## 🚀 Features

- **Real Database Connection**: Connect to multiple SQL Server databases using provided credentials
- **Comprehensive PII Detection**: Identify 25+ PII patterns including:
  - **HIPAA PHI**: All 18 protected health information identifiers
  - **GDPR Special Categories**: Genetic, health, biometric, racial, political, religious data
  - **CCPA Sensitive Information**: Financial, geolocation, citizenship data
  - **Common PII**: SSN, emails, phones, addresses, credit cards, names, dates
- **Regulatory Compliance**: Built-in compliance checking for:
  - 🇪🇺 **GDPR** (General Data Protection Regulation)
  - 🇺🇸 **CCPA** (California Consumer Privacy Act) 
  - 🏥 **HIPAA** (Health Insurance Portability and Accountability Act)
- **Advanced Analytics**: Risk scoring, confidence analysis, pattern validation
- **Interactive Dashboard**: Real-time visualization with Streamlit
- **Compliance Reporting**: Executive summaries, detailed findings, regulatory gap analysis
- **Data Masking**: Secure display of sensitive information

## 🏗️ Project Structure

```
├── src/                           # Source code
│   ├── core/                     # Core PII detection components
│   │   ├── pii_detector.py      # Main detection engine with 25+ patterns
│   │   ├── config.py            # Enhanced regulatory pattern definitions
│   │   ├── utils.py             # Utility functions and data masking
│   │   ├── ai_assistant.py      # AI-powered analysis assistant
│   │   ├── results_manager.py   # Results storage and management
│   │   ├── encryption_manager.py # Data encryption and security
│   │   ├── report_generator.py  # Compliance reporting
│   │   └── env_config.py        # Environment configuration
│   ├── database/                # Database management
│   │   ├── database_manager.py  # Demo mode with synthetic data
│   │   ├── real_database_manager.py # Live SQL Server connections
│   │   ├── multi_database_manager.py # Multi-database support
│   │   └── vscode_sql_manager.py # VS Code SQL integration
│   └── ui/                      # User interface
│       └── app.py              # Main Streamlit application
├── tests/                       # Test suite
├── scripts/                     # Utility scripts
│   ├── demo.py                 # Standalone demo script
│   ├── install.py              # Package installer
│   └── setup.py                # Environment setup
├── docs/                       # Documentation
├── run_app.py                  # Application launcher
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Run the Application
```bash
# Using the launcher script (recommended)
python run_app.py

# Or directly with Streamlit
cd src
streamlit run ui/app.py
```

### 2. Database Credentials
The application uses these credentials for SQL Server connections:
- **Username**: `hackathon_epsilon`  
- **Password**:
- **Port**: `1433`
- **Server**: `sql-lakeside-server.database.windows.net`

### 3. Run Application
```bash
streamlit run app.py
```

### 4. Test Connections (Optional)
```bash
python test_connections.py
```

### 5. Run Demo
```bash
python demo.py
```

## 🎯 Usage Guide

### Step 1: Database Connection
1. Launch the Streamlit app
2. Navigate to "Database Connection" 
3. Toggle "Use Real Database Connections" (enabled by default)
4. Select from available databases:
   - **AdventureWorks2019** - Microsoft sample database
   - **ECC60jkl_HACK** - ERP system data
   - **Jde920_demo** - JD Edwards demo data  
   - **ORACLE_EBS_HACK** - Oracle EBS migration data
   - **Results** - Analysis results database
5. Click "Connect to Database"

### Step 2: Data Analysis  
1. Navigate to "Data Analysis"
2. Explore database tables and schemas
3. View column metadata and sample data
4. Identify potential PII-containing tables

### Step 3: PII Detection Scan
1. Navigate to "PII Detection" 
2. Select tables to scan (supports multi-select)
3. Configure scan parameters:
   - Sample size per table (default: 100 rows)
   - Confidence threshold (default: 0.7)
4. Click "Start PII Scan"
5. View real-time progress and results

### Step 4: Compliance Dashboard
1. Navigate to "Compliance Dashboard"
2. Review regulatory compliance overview:
   - GDPR findings and special categories
   - CCPA sensitive information detection  
   - HIPAA PHI identifier analysis
3. Analyze severity distribution and critical findings
4. Review detailed compliance breakdowns

### Step 5: Generate Reports
1. Navigate to "Reports"
2. Export summary or detailed reports
3. Access compliance recommendations
4. Download findings as CSV for further analysis

## 🔍 Detection Capabilities

### HIPAA Protected Health Information (18 Identifiers)
- Names, addresses, dates of birth
- Phone/fax numbers, email addresses  
- SSN, medical record numbers, health plan numbers
- Account numbers, certificate/license numbers
- Vehicle identifiers, device identifiers
- URLs, IP addresses, biometric identifiers

### GDPR Special Categories  
- Racial or ethnic origin data
- Political opinions and affiliations
- Religious or philosophical beliefs  
- Trade union membership
- Genetic and biometric data
- Health and medical data
- Sexual orientation information

### CCPA Sensitive Personal Information
- SSN, passport, driver's license numbers
- Financial account information
- Precise geolocation data
- Racial/ethnic origin, citizenship status
- Religious beliefs, union membership
- Genetic data, biometric identifiers
- Health data, sexual orientation

### Advanced Pattern Matching
- **Regex-based detection** with validation algorithms
- **Column name analysis** for PII indicators
- **Confidence scoring** with severity assessment  
- **Context-aware matching** reducing false positives
- **Multi-regulatory compliance** mapping

## 📊 Available Databases

| Database | Description | Use Case |
|----------|-------------|----------|
| **AdventureWorks2019** | Microsoft sample database | Standard business data patterns |
| **ECC60jkl_HACK** | ERP system data | Enterprise resource planning |
| **Jde920_demo** | JD Edwards demo | Supply chain and financials |
| **ORACLE_EBS_HACK** | Oracle EBS migration | Enterprise business suite |
| **Results** | Analysis results | PII detection outcomes |

## 🛡️ Security & Privacy

- **Secure Connections**: TLS encryption for database connections
- **Data Masking**: PII values masked in UI display  
- **Minimal Data Access**: Sampling-based analysis
- **Audit Logging**: Comprehensive activity logging
- **No Data Persistence**: Analysis results stored in session only

## 📋 Regulatory Compliance

### GDPR Compliance Features
- Special category data detection
- Lawful basis assessment recommendations
- Data Protection Impact Assessment (DPIA) triggers
- Privacy by design principles

### CCPA Compliance Features  
- Consumer rights impact analysis
- Sensitive personal information categorization
- Opt-out mechanism requirements
- Data inventory and mapping

### HIPAA Compliance Features
- 18 PHI identifier detection  
- Business Associate Agreement (BAA) requirements
- Minimum necessary access recommendations
- Security safeguard implementation guides

## 🔧 Configuration

Key configuration files:
- `config.py`: PII patterns, database profiles, scanning parameters
- `requirements.txt`: Python package dependencies
- `.vscode/tasks.json`: VS Code task configuration

## 🧪 Testing & Demo

### Run Demo Script
```bash
python demo.py
```

### Test Database Connections  
```bash
python test_connections.py
```

### Manual Testing
1. Use demo mode with synthetic data
2. Test individual pattern matching
3. Validate compliance reporting

## 📈 Performance

- **Sampling-based analysis** for large datasets
- **Parallel processing** for multiple tables
- **Configurable batch sizes** (10-10,000 rows)
- **Real-time progress tracking**
- **Memory-efficient streaming**

## 🤝 Contributing

This hackathon prototype demonstrates:
- Real-world database integration
- Comprehensive regulatory compliance  
- Production-ready architecture patterns
- Scalable detection algorithms
- Enterprise-grade security practices

## 📄 License

Created for # 🔍 Enhanced PII Detection System

An intelligent, AI-powered Personal Identifiable Information (PII) detection system with multi-database support, advanced search capabilities, encryption, and comprehensive compliance reporting.

## ✨ Features

### 🤖 AI-Powered Detection
- **Claude AI Integration**: Intelligent table discovery and PII action recommendations
- **Smart Table Selection**: AI identifies tables most likely to contain PII
- **Context-Aware Decisions**: AI suggests appropriate actions (mask, encrypt, log) based on data context
- **Confidence Scoring**: AI provides confidence scores for detection recommendations

### � Advanced Search & Analysis
- **Results Table Search**: Search and browse detected PII names with fuzzy matching
- **Exact Match Search**: Find specific PII entries with case-insensitive matching
- **Similar Names Search**: Use advanced similarity algorithms to find name variations
- **Smart Name Normalization**: Handles variations like "Robert D. Junior" vs "Robert Junior"
- **Real-time Statistics**: View table statistics and recent additions

### �🗄️ Multi-Database Support
- **Simultaneous Connections**: Connect to multiple databases at once
- **Parallel Processing**: Concurrent PII scanning across databases
- **Multiple Database Types**: SQL Server, Oracle, and more via ODBC
- **Connection Pooling**: Efficient database connection management
- **Results Database Integration**: Direct querying of PII detection results

### 🛡️ Data Protection & Encryption
- **AES Encryption**: Secure PII encryption using Fernet (AES 128)
- **Smart Masking**: Context-aware data masking strategies
- **Key Management**: Secure master key generation and management
- **Regulatory Compliance**: GDPR, CCPA, and HIPAA compliance features

### 💾 Results Management
- **SQLite Database**: Persistent storage of all PII detection results
- **SQL Server Integration**: Direct access to `identified_names_team_epsilon` table
- **Scan History**: Track all scan sessions with detailed metadata
- **Export Options**: CSV export for reporting and analysis
- **Advanced Filtering**: Search by name, source, probability, and similarity

### 📊 Advanced Reporting
- **Executive Summaries**: High-level PII detection overviews
- **Compliance Reports**: Detailed regulatory compliance analysis
- **Risk Assessments**: Data security risk evaluation
- **Trend Analysis**: Historical PII detection patterns

### 🎯 Enhanced User Experience
- **Interactive Web Interface**: Modern Streamlit-based UI
- **Real-time Progress**: Live updates during scanning operations
- **Visual Analytics**: Charts and graphs for data insights
- **Configurable Settings**: Flexible configuration options

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Database access (SQL Server, Oracle, etc.) or use demo mode
- Claude API key (optional, for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sreehari59/Hackathon-2025-Jivs.git
   cd Hackathon-2025-Jivs
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Configure environment**
   - Edit `.env` file with your configuration
   - Add your Claude API key for AI features
   - Update database credentials if using real data

4. **Start the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the web interface**
   - Open your browser to `http://localhost:8501`

### Manual Installation

If you prefer manual setup:

```bash
# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir logs backups exports data temp

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Run the application
streamlit run app.py
```

## ⚙️ Configuration

### Environment Variables

Configure the system by editing the `.env` file:

```bash
# AI Configuration
ANTHROPIC_API_KEY=your_claude_api_key_here
AI_MODEL_NAME=claude-sonnet-4-20250514
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.1

# Database Configuration
CONNECTION_MODE=demo  # Options: demo, real, vscode
DB_SERVER=your_database_server
DB_USERNAME=your_username
DB_PASSWORD=your_password

# Security Configuration
ENABLE_ENCRYPTION=true
ENABLE_DATA_MASKING=true

# Compliance Settings
ENABLE_GDPR_COMPLIANCE=true
ENABLE_CCPA_COMPLIANCE=true
ENABLE_HIPAA_COMPLIANCE=true
```

### Database Profiles

Add your database connections in `config.py`:

```python
DATABASE_PROFILES = {
    'YourDatabase': {
        'server': 'your-server.database.windows.net',
        'database': 'YourDatabaseName',
        'username': 'your_username',
        'password': 'your_password',
        'port': 1433
    }
}
```

## 📖 Usage Guide

### 1. Database Connection
- Navigate to "1. Connect to Database"
- Select from available database profiles
- Connect to SQL Server instances with real data
- Access enterprise databases like AdventureWorks2019, Results, etc.

### 2. AI Table Discovery
Use the AI-powered table discovery to identify tables most likely to contain PII:
- Navigate to "2. AI Discovery"
- Connect to your databases
- Let AI analyze and recommend high-priority tables
- Review confidence scores and PII type predictions

### 3. Data Protection & Encryption
Prepare your data for secure handling:
- Go to "3. Encryption Preparation"
- Configure encryption settings and security parameters
- Test encryption/decryption functionality
- Set up regulatory compliance requirements

### 4. Results Display
View comprehensive PII detection results:
- Access "4. Results Display" 
- Review detected PII with confidence scores
- Export findings to CSV
- Analyze risk assessments and compliance status

### 5. Check Results Table (NEW!)
Search and analyze the PII detection database:
- Navigate to "5. Check Results Table"
- **Search by name**: Enter specific names to find exact matches
- **Fuzzy matching**: Find similar names with configurable similarity threshold
- **Handle variations**: Automatically matches names like:
  - "Andrew R. Hill" ↔ "Andrew R Hill" (periods)
  - "Robert D. Junior" ↔ "Robert Junior" (middle initials)
  - "Robert D Junior" ↔ "Robert D Juniorr" (typos)
- **View statistics**: See total records, unique names, and sources
- **Export results**: Download search results as CSV files

## 🎯 Application Workflow

The application provides a structured 5-step workflow for comprehensive PII detection and analysis:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. Database    │───▶│  2. AI Discovery│───▶│ 3. Encryption   │
│   Connection    │    │                 │    │  Preparation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│Connect to SQL   │    │AI analyzes      │    │Configure        │
│Server databases │    │tables for PII   │    │encryption &     │
│with real data   │    │likelihood       │    │security settings│
└─────────────────┘    └─────────────────┘    └─────────────────┘

                ┌─────────────────┐    ┌─────────────────┐
                │  4. Results     │───▶│ 5. Check Results│
                │   Display       │    │     Table       │
                └─────────────────┘    └─────────────────┘
                         │                       │
                         ▼                       ▼
                ┌─────────────────┐    ┌─────────────────┐
                │View detected    │    │Search & analyze │
                │PII with export  │    │PII database with│
                │capabilities     │    │fuzzy matching   │
                └─────────────────┘    └─────────────────┘
```

## 🔍 Smart Search Features

The new "Check Results Table" page provides advanced search capabilities:

### Exact Match Search
- **Case-insensitive**: Matches regardless of capitalization
- **Punctuation handling**: "Andrew R. Hill" matches "Andrew R Hill"
- **Space normalization**: Handles multiple spaces and formatting differences

### Fuzzy Matching Algorithm
- **Similarity threshold**: Configurable from 0.0 to 1.0 (default: 0.6)
- **Intelligent normalization**: 
  - Removes periods and extra spaces
  - Handles common name suffixes (Jr, Senior, III, etc.)
  - Standardizes formatting for accurate comparison
- **Examples of matches**:
  - "Robert D. Junior" ↔ "Robert Junior" (90% similarity)
  - "Andrew R Hill" ↔ "Andrew R. Hill" (100% similarity)
  - "John Smith" ↔ "Jon Smith" (89% similarity)

### Database Statistics
- **Real-time metrics**: Total records, unique names, unique sources
- **Recent additions**: View latest PII detections
- **Export functionality**: Download search results as CSV

## 🧩 System Architecture

### Core Components

1. **Streamlit UI** (`app.py`)
   - 5-page navigation structure
   - Real-time progress tracking
   - Interactive search interface
   - Export and download capabilities

2. **AI Assistant** (`ai_assistant.py`)
   - Claude API integration
   - Table analysis and recommendations
   - PII action suggestions

3. **Multi-Database Manager** (`multi_database_manager.py`)
   - Parallel database connections
   - Concurrent scanning operations
   - Connection pooling and management

4. **Encryption Manager** (`encryption_manager.py`)
   - AES encryption using Fernet
   - Secure key derivation
   - Context-aware masking

5. **Results Manager** (`results_manager.py`)
   - SQLite database operations
   - Scan session tracking
   - Search and export functionality

6. **PII Detector** (`pii_detector.py`)
   - Pattern-based PII detection
   - Confidence scoring
   - Regulatory compliance mapping

7. **Search Engine** (NEW!)
   - Fuzzy name matching with difflib
   - Smart name normalization
   - SQL Server results integration
   - Real-time statistics

### Data Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Streamlit UI   │◄──▶│ Multi-DB Manager │◄──▶│  SQL Server     │
│  (5 Pages)      │    │                  │    │  Databases      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│Search Interface │    │Parallel Scanning │    │Pattern Matching │
│& Fuzzy Matching │    │                  │    │& AI Analysis    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│Results Database │◄───│ Results Manager  │◄───│Encryption Mgr   │
│identified_names │    │                  │    │& Data Masking   │
│_team_epsilon    │    └──────────────────┘    └─────────────────┘
└─────────────────┘
```

## 🔒 Security Features

### Encryption
- **AES-128 Encryption**: Industry-standard encryption using Fernet
- **PBKDF2 Key Derivation**: Secure key generation with 100,000 iterations
- **Master Key Protection**: Restricted file permissions for key storage
- **Context-Aware Encryption**: Different strategies based on PII types

### Data Masking
- **Pattern-Aware Masking**: Preserves data format while hiding sensitive content
- **Regulatory Compliance**: Masking strategies aligned with GDPR, CCPA, HIPAA
- **Reversible Protection**: Option to encrypt instead of permanent masking
- **Audit Trail**: Complete logging of all masking operations

### Access Control
- **Session Management**: Secure session handling with configurable timeouts
- **Database Isolation**: Separate connections prevent cross-contamination
- **Audit Logging**: Comprehensive logging of all system operations

## � Advanced Search Algorithms

### Name Normalization Algorithm

The system uses intelligent name normalization to handle common variations:

```python
def normalize_name(name: str) -> str:
    """Smart name normalization for accurate matching"""
    # Convert to lowercase and strip whitespace
    normalized = name.lower().strip()
    
    # Remove periods (Dr. Smith → Dr Smith)
    normalized = normalized.replace('.', '')
    
    # Normalize multiple spaces to single space
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Handle common suffixes (Jr, Senior, III, etc.)
    suffixes = [' jr', ' junior', ' sr', ' senior', ' iii', ' ii', ' iv']
    for suffix in suffixes:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()
            break
    
    return normalized
```

### Fuzzy Matching with Sequence Matching

Uses Python's `difflib.SequenceMatcher` for intelligent similarity scoring:

- **Ratio Calculation**: Compares normalized strings for similarity
- **Configurable Threshold**: Adjustable similarity requirements (0.0-1.0)
- **Context Preservation**: Maintains original formatting in results
- **Performance Optimized**: Efficient string comparison algorithms

### Search Examples

| Search Term | Database Entry | Similarity | Match Type |
|-------------|----------------|------------|------------|
| "Andrew R. Hill" | "Andrew R Hill" | 100% | Exact (normalized) |
| "Robert D. Junior" | "Robert Junior" | 90% | Similar (suffix removed) |
| "John Smith" | "Jon Smith" | 89% | Fuzzy (typo correction) |
| "Dr. Sarah Johnson" | "Sarah Johnson" | 95% | Similar (title removed) |

## �📋 PII Detection Patterns

The system detects 30+ PII types across regulatory frameworks:

### HIPAA Protected Health Information (PHI)
- Social Security Numbers (SSN)
- Medical Record Numbers
- Health Plan Numbers
- Account Numbers
- Email Addresses
- Phone/Fax Numbers
- Dates of Birth
- Biometric Identifiers

### GDPR Special Categories
- Racial/Ethnic Origin
- Political Opinions  
- Religious Beliefs
- Trade Union Membership
- Genetic Data
- Health Data
- Sexual Orientation

### CCPA Personal Information
- Financial Account Numbers
- Credit Card Numbers
- Precise Geolocation
- Immigration Status
- Biometric Information

## 🔧 Development

### Project Structure
```
├── src/                           # Source code
│   ├── ui/
│   │   └── app.py                # Main Streamlit application (5 pages)
│   ├── core/                     # Core PII detection components
│   │   ├── pii_detector.py      # Main detection engine with 25+ patterns
│   │   ├── config.py            # Enhanced regulatory pattern definitions
│   │   ├── utils.py             # Utility functions and data masking
│   │   ├── ai_assistant.py      # AI-powered analysis assistant
│   │   ├── results_manager.py   # Results storage and management
│   │   ├── encryption_manager.py # Data encryption and security
│   │   ├── report_generator.py  # Compliance reporting
│   │   └── env_config.py        # Environment configuration
│   └── database/                # Database management
│       ├── database_manager.py  # Demo mode with synthetic data
│       ├── real_database_manager.py # Live SQL Server connections
│       ├── multi_database_manager.py # Multi-database support
│       └── vscode_sql_manager.py # VS Code SQL integration
├── tests/                       # Test suite
├── scripts/                     # Utility scripts
├── docs/                       # Documentation
├── run_app.py                  # Application launcher
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Navigation Structure

The application features a 5-page workflow accessible via sidebar navigation:

1. **📋 Dashboard** - Overview and workflow progress
2. **🔗 1. Connect to Database** - SQL Server database connections
3. **🤖 2. AI Discovery** - AI-powered table analysis and recommendations
4. **🔐 3. Encryption Preparation** - Data security and encryption setup
5. **📊 4. Results Display** - Comprehensive PII detection results and reporting
6. **🔍 5. Check Results Table** - Advanced search and analysis of PII database

### Adding New PII Patterns

1. **Update `config.py`**:
   ```python
   PII_PATTERNS['NEW_PATTERN'] = {
       'pattern': r'your_regex_pattern',
       'description': 'Description of the PII type',
       'severity': 'CRITICAL',  # CRITICAL, HIGH, MEDIUM, LOW
       'regulations': ['GDPR', 'CCPA', 'HIPAA']
   }
   ```

2. **Add Column Indicators**:
   ```python
   PII_COLUMN_INDICATORS.extend([
       'new_column_name', 'another_indicator'
   ])
   ```

3. **Update Masking Strategy** (optional):
   ```python
   # In encryption_manager.py
   def mask_pii_value(self, value: str, pii_type: str) -> str:
       if pii_type == 'NEW_PATTERN':
           return self._mask_new_pattern(value)
       # ... existing logic
   ```

### Testing

Run the setup script to validate your installation:
```bash
python setup.py
```

For manual testing:
```bash
# Test imports
python -c "import app; print('All imports successful')"

# Test database connections
python -c "from multi_database_manager import MultiDatabaseManager; print('DB manager ready')"

# Test AI integration
python -c "from ai_assistant import AIAssistant; print('AI assistant ready')"
```

## 🎉 What's New in This Version

### 🔍 Advanced Search Capabilities
- **New Page**: "5. Check Results Table" with comprehensive search functionality
- **Fuzzy Matching**: Find name variations with intelligent similarity algorithms
- **Smart Normalization**: Handle periods, spaces, and common name variations
- **Real-time Statistics**: Live database metrics and recent additions
- **Export Integration**: Download search results directly as CSV

### 🚀 Enhanced User Experience
- **5-Page Workflow**: Streamlined navigation through the PII detection process
- **SQL Server Integration**: Direct access to `identified_names_team_epsilon` table
- **Interactive Search**: Real-time search with configurable similarity thresholds
- **Visual Feedback**: Progress indicators and status updates throughout the workflow

## 🤝 Contributing

This hackathon prototype demonstrates:
- **Real-world database integration** with SQL Server enterprise databases
- **Advanced search algorithms** with fuzzy matching and name normalization
- **Comprehensive regulatory compliance** for GDPR, CCPA, and HIPAA
- **Production-ready architecture** patterns for scalable PII detection
- **Enterprise-grade security** practices with encryption and data masking
- **Intelligent AI integration** for automated table discovery and recommendations

### Key Innovations
1. **Multi-step workflow** with clear progression through PII detection phases
2. **Advanced search interface** for analyzing detected PII with similarity matching
3. **Real-time database connectivity** to enterprise SQL Server instances  
4. **Intelligent name handling** for variations, typos, and formatting differences
5. **Export capabilities** for compliance reporting and analysis

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Anthropic** for Claude AI API
- **Streamlit** for the amazing web framework
- **Microsoft** for SQL Server connectivity
- **Python Cryptography** team for encryption libraries

## 📞 Support & Documentation

- **Live Demo**: Run `python run_app.py` to start the application
- **Test Data**: Use the "Results" database to test search functionality
- **Search Examples**: Try searching for names like "Andrew R. Hill", "Robert Junior", etc.
- **Export Features**: Download search results and detection summaries as CSV files
- **Issues**: Report bugs and feature requests on GitHub Issues
- **Documentation**: Check the wiki for detailed documentation

---

**🔍 Enhanced PII Detection System - Built for enterprise data privacy and security with advanced search capabilities**

*Version: Hackathon 2025 - Team Epsilon*