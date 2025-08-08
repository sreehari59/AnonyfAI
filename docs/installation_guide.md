# Installation Guide for PII Detection System

Since you're using VS Code with the SQL Server extension, here are the installation options and links:

## Option 1: Use VS Code SQL Server Extension (Recommended for You)

Since you already have the VS Code SQL Server extension working, this is the easiest path:

1. **Keep your existing VS Code SQL Server extension setup**
2. **Install Python packages only:**
   ```powershell
   pip install pyodbc pandas streamlit plotly
   ```
3. **Run the application:**
   ```powershell
   streamlit run app.py
   ```

The application will automatically detect your VS Code SQL extension and use compatibility mode.

## Option 2: Install ODBC Drivers (For Direct Database Access)

If you want direct ODBC access (better performance), install these drivers:

### Microsoft ODBC Driver for SQL Server
- **Download Link**: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
- **Recommended Version**: ODBC Driver 18 for SQL Server
- **Direct Download**: https://go.microsoft.com/fwlink/?linkid=2187214

### Alternative Drivers (try in this order):
1. **ODBC Driver 18 for SQL Server** (Latest)
2. **ODBC Driver 17 for SQL Server**: https://www.microsoft.com/en-us/download/details.aspx?id=56567
3. **ODBC Driver 13.1 for SQL Server**: https://www.microsoft.com/en-us/download/details.aspx?id=53339

## Option 3: Use Demo Mode

For testing without database connections:
1. Install Python packages (same as above)
2. Switch to "Demo Mode" in the application
3. Uses synthetic data with realistic PII patterns

## Installation Steps

### 1. Python Packages
```powershell
# Core packages
pip install pyodbc pandas streamlit plotly

# Optional for enhanced NLP
pip install spacy
python -m spacy download en_core_web_sm
```

### 2. ODBC Driver Installation
1. Download from the Microsoft link above
2. Run the installer as Administrator
3. Choose "Typical" installation
4. Restart VS Code after installation

### 3. Test Your Setup
```powershell
cd "d:\Github Stuff\Hackathon-2025-Jivs"
python test_connections.py
```

## Current Error Solutions

### Error 1: "Connection is busy with results for another command"
- **Solution**: Application now includes connection management fixes
- **Automatic handling**: The app will retry connections and clear busy states

### Error 2: "ODBC SQL type -151 is not yet supported"
- **Solution**: Application now converts problematic data types automatically  
- **Fallback**: If ODBC fails, switches to VS Code extension mode

## Quick Start Commands

```powershell
# Install dependencies
pip install pyodbc pandas streamlit plotly

# Test connections (optional)
python test_connections.py

# Run the application
streamlit run app.py
```

## Troubleshooting

### If ODBC still fails:
1. Use the application's "VS Code SQL Extension Mode"
2. Switch to "Demo Mode" for testing
3. Check Windows ODBC Data Source Administrator

### If VS Code extension doesn't work:
1. Reinstall SQL Server (mssql) extension in VS Code
2. Check your existing database connections in VS Code
3. Use Demo Mode as fallback

## Your Current Setup

Based on your setup:
- ✅ VS Code with SQL Server extension (working)
- ⚠️ ODBC drivers (needs fixing or use compatibility mode)
- ✅ Database credentials (provided)
- ✅ Python environment

**Recommended**: Just install the Python packages and run `streamlit run app.py`. The application will automatically use your VS Code SQL extension setup!
