# 🔍 Enhanced PII Detection System

An advanced **Personally Identifiable Information (PII) Detection System** with AI-powered analysis, multi-database support, and comprehensive search capabilities. Built for enterprise data privacy compliance with GDPR, CCPA, and HIPAA regulations.

## 🌟 Key Features

- **🔍 Advanced Search**: Fuzzy matching and name normalization for finding PII variations
- **🤖 AI-Powered Detection**: Claude AI integration for intelligent table discovery and recommendations
- **🗄️ Multi-Database Support**: Connect to multiple SQL Server, Oracle databases simultaneously
- **🛡️ Data Protection**: AES encryption, smart masking, and regulatory compliance (GDPR, CCPA, HIPAA)
- **� Results Management**: Persistent storage, export capabilities, and advanced search
- **🎯 5-Step Workflow**: Streamlined navigation from database connection to results analysis

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

### 5-Step Workflow
1. **Database Connection** - Connect to SQL Server databases
2. **AI Discovery** - AI analyzes tables for PII likelihood with confidence scores
3. **Encryption Preparation** - Configure security settings and compliance requirements
4. **Results Display** - View detected PII with export capabilities
5. **Check Results Table** - Search PII database with fuzzy matching and export results

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

**Advanced name matching capabilities:**
- **Exact Match**: Case-insensitive search with punctuation handling
- **Fuzzy Matching**: Configurable similarity threshold (0.0-1.0) with intelligent normalization
- **Name Variations**: Handles "Robert D. Junior" ↔ "Robert Junior", "Andrew R. Hill" ↔ "Andrew R Hill"
- **Real-time Statistics**: Database metrics and CSV export functionality



## 🧩 System Architecture

**Core Components:**
- **Streamlit UI** - 5-page navigation with real-time progress
- **AI Assistant** - Claude API integration for table analysis
- **Multi-Database Manager** - Parallel database connections and scanning
- **Encryption Manager** - AES encryption and secure masking
- **Results Manager** - SQLite operations and search functionality
- **PII Detector** - Pattern-based detection with compliance mapping

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

## 📈 Performance

- **Sampling-based analysis** for large datasets
- **Parallel processing** for multiple tables
- **Configurable batch sizes** (10-10,000 rows)
- **Real-time progress tracking**
- **Memory-efficient streaming**

## 🎉 What's New

- **Advanced Search**: New "Check Results Table" page with fuzzy matching and name normalization
- **5-Step Workflow**: Streamlined navigation through PII detection process  
- **SQL Server Integration**: Direct access to enterprise databases and results table
- **Enhanced Export**: Download search results and detection summaries as CSV

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
