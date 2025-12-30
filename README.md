# License Ledger Patterns

Analyze city business license data to surface structural risk patterns—address clustering, naming repetition, temporal spikes, and network overlap. Built for journalists, auditors, and civic investigators to follow signals before allegations.

## Overview

This tool performs neutral, data-driven analysis of municipal business license data to identify structural patterns that may warrant further investigation. It surfaces anomalies without making accusations, explains why they matter, and suggests next steps for validation.

## Features

### Single-Dataset Pattern Detection

1. **Address Density Analysis**
   - Identifies addresses with multiple business licenses
   - Flags potential shell companies or shared office arrangements
   - Ranks by concentration and risk score

2. **Name Similarity Detection**
   - Uses fuzzy matching to find related business names
   - Detects variations like "Acme Corp", "ACME Corporation", "Acme Co."
   - Clusters potentially related entities

3. **DBA Pattern Analysis**
   - Analyzes "Doing Business As" name usage
   - Finds businesses with multiple DBAs
   - Identifies DBAs shared by multiple businesses

4. **Temporal Clustering**
   - Detects unusual spikes in license issuance
   - Identifies coordinated filing patterns
   - Flags administrative batches vs. suspicious clustering

5. **Geographic Concentration**
   - Maps license density by ZIP code
   - Calculates licenses per address ratios
   - Identifies potential registered agent hubs

### Cross-Dataset Analysis

The tool also supports comprehensive analysis across multiple municipal datasets:

1. **Address Clustering**
   - Identifies addresses appearing in both business licenses and tax-delinquent records
   - Detects high-density business addresses
   - Flags properties with potential financial distress indicators

2. **Name/Entity Matching**
   - Fuzzy matching between license holders and contract suppliers
   - Identifies license holders with tax-delinquent property connections
   - Links related entities across datasets

3. **License Age vs Contract Timing**
   - Correlates business license issuance with contract awards
   - Identifies temporal spikes in contract activity
   - Flags same-day contract awards and short-duration contracts

4. **Procurement Type Analysis**
   - Analyzes distribution of procurement methods
   - Identifies non-competitive award patterns
   - Flags suppliers with high non-competitive contract concentrations

5. **Agency Concentration**
   - Measures supplier concentration by agency
   - Identifies suppliers working across multiple agencies
   - Flags agencies with high supplier concentration

6. **Tax Delinquency Overlaps**
   - Cross-references contractors with tax-delinquent property owners
   - Identifies high-value and long-term delinquencies
   - Flags potential enforcement gaps

### Output Formats

- **Text Reports**: Human-readable formatted reports with tables and ranked lists
- **JSON Export**: Machine-readable data for further analysis
- **Risk Scores**: Normalized 0-1 scores for each finding
- **Contextual Explanations**: "Why it matters" for each pattern

## Installation

```bash
# Clone the repository
git clone https://github.com/closespark/license-ledger-patterns.git
cd license-ledger-patterns

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Analysis

```bash
python cli.py your_license_data.csv
```

### Save Report to File

```bash
python cli.py your_license_data.csv --output report.txt
```

### Export to JSON

```bash
python cli.py your_license_data.csv --json findings.json
```

### Adjust Analysis Thresholds

```bash
python cli.py your_license_data.csv \
  --address-threshold 5 \
  --name-similarity 0.9 \
  --temporal-window 7 \
  --temporal-threshold 5 \
  --zip-threshold 10
```

### Cross-Dataset Analysis

Analyze patterns across multiple municipal datasets:

```bash
# Run cross-dataset analysis with default data files
python analyze_datasets.py

# Specify custom data paths
python analyze_datasets.py \
  --licenses data/Business_Licenses.csv \
  --contracts data/City_Contracts.csv \
  --taxes data/Delinquent_Taxes.csv

# Save reports
python analyze_datasets.py --output report.txt --json results.json
```

## Data Format

### Single-Dataset Analysis (cli.py)

The tool expects CSV or Excel files with the following structure:

### Required Columns

- `license_id`: Unique identifier for each license
- `business_name`: Legal business name
- `address`: Physical address

### Optional Columns (Recommended)

- `dba_name`: "Doing Business As" name
- `city`: City name
- `state`: State abbreviation
- `zip_code`: ZIP code
- `issue_date`: License issue date (YYYY-MM-DD format)
- `license_type`: Type/category of license
- `owner_name`: Business owner name

### Example Data

See `sample_data.csv` for a complete example dataset.

### Cross-Dataset Analysis (analyze_datasets.py)

For cross-dataset analysis, three CSV files are expected:

**Business Licenses:**
- `Business Name`: Legal business name
- `Doing Business As`: DBA name (optional)
- `Business Address`: Physical address
- `Business Geo Location`: Geographic coordinates (optional)

**City Contracts:**
- `Agency/Department`: City agency or department
- `Contract Number`: Unique contract identifier
- `Contract Value`: Contract dollar value
- `Supplier`: Contractor/vendor name
- `Procurement Type`: Method of procurement
- `Description`: Contract description
- `Type of Solicitation`: Solicitation category
- `Effective From`: Contract start date
- `Effective To`: Contract end date

**Delinquent Property Taxes:**
- `Property Code`: Property identifier
- `Current Owner Name 1`: Primary owner name
- `Current Owner Name 2`: Secondary owner (optional)
- `Physical Address`: Property address
- `Total Due`: Amount owed
- `Total Years Delinquent`: Duration of delinquency
- `GIS Location`: Geographic coordinates (optional)

## Example Output

### Executive Summary
```
EXECUTIVE SUMMARY - License Ledger Pattern Analysis
================================================================================

Dataset Overview:
  Total Licenses: 30
  Unique Businesses: 28
  Unique Addresses: 15
  Date Range: 2024-01-10 to 2024-06-03

Key Findings:
--------------------------------------------------------------------------------

✓ ADDRESS CLUSTERING: 4 addresses flagged
  Highest: 6 licenses at single address

✓ NAME SIMILARITY: 3 clusters of similar names
  Largest cluster: 4 similar names

✓ TEMPORAL CLUSTERING: 5 time-based clusters
  Largest spike: 8 licenses in short period
```

### Detailed Findings

Each pattern includes:
- Specific instances ranked by risk score
- Context explaining why the pattern matters
- Suggested validation steps
- Sample data for review

## Use Cases

### For Journalists
- Investigate business license mills
- Track shell company networks
- Identify coordinated business activities
- Validate tips with data

### For Auditors
- Review compliance patterns
- Identify high-risk addresses
- Flag potential fraud indicators
- Generate audit candidate lists

### For Civic Investigators
- Monitor business registration trends
- Track development patterns
- Analyze economic activity
- Support transparency initiatives

## Methodology

This tool uses statistical and algorithmic approaches to identify patterns:

- **Fuzzy String Matching**: Levenshtein distance for name similarity
- **Temporal Analysis**: Rolling window clustering
- **Geographic Analysis**: Density mapping and concentration ratios
- **Risk Scoring**: Normalized metrics for comparative analysis

All findings are presented neutrally as signals requiring validation, not as definitive evidence of wrongdoing.

## Next Steps for Investigation

The tool suggests specific validation steps for each finding:

1. Cross-reference flagged addresses with business registries
2. Investigate ownership networks for similar business names
3. Review temporal clusters for administrative explanations
4. Map geographic concentrations against known business districts
5. Interview businesses with unusual DBA patterns
6. Check public records for additional ownership information

## Programmatic Usage

```python
from analyzer import LicenseAnalyzer
from reporter import Reporter
import pandas as pd

# Load data
data = pd.read_csv('licenses.csv')

# Analyze
analyzer = LicenseAnalyzer(data)
address_density = analyzer.analyze_address_density()
name_similarity = analyzer.analyze_name_similarity()
dba_patterns = analyzer.analyze_dba_patterns()
temporal = analyzer.analyze_temporal_clustering()
geographic = analyzer.analyze_geographic_concentration()
summary = analyzer.generate_summary_report()

# Generate report
reporter = Reporter(summary)
report = reporter.generate_full_report(
    address_density, name_similarity, dba_patterns,
    temporal, geographic, summary
)
print(report)
```

### Cross-Dataset Analysis

```python
from cross_dataset_analyzer import CrossDatasetAnalyzer, format_report
import json

# Initialize with all three datasets
analyzer = CrossDatasetAnalyzer(
    licenses_path='data/Business_Licenses.csv',
    contracts_path='data/City_Contracts.csv',
    taxes_path='data/Delinquent_Taxes.csv'
)

# Run comprehensive analysis
results = analyzer.generate_comprehensive_report()

# Generate formatted text report
report = format_report(results)
print(report)

# Access specific analysis results
address_findings = results['analyses']['address_clustering']
name_matches = results['analyses']['name_similarity']
contract_timing = results['analyses']['contract_timing']
procurement = results['analyses']['procurement_types']
agency_data = results['analyses']['agency_concentration']
tax_overlaps = results['analyses']['tax_delinquent_overlaps']

# Get key findings and recommendations
key_findings = results['key_findings']
recommendations = results['follow_up_recommendations']

# Export to JSON
with open('results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
```

## Testing

Run the tool with sample data:

```bash
# Single-dataset analysis
python cli.py sample_data.csv

# Cross-dataset analysis
python analyze_datasets.py
```

This demonstrates all pattern detection capabilities with realistic test data.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Focus on neutral pattern detection
2. Avoid accusatory language
3. Include contextual explanations
4. Add tests for new patterns
5. Document methodology

## Disclaimer

This tool identifies structural patterns in data. Patterns may have legitimate explanations. Always validate findings through additional research and investigation before drawing conclusions. This tool is for investigative purposes only and does not constitute evidence of wrongdoing.

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.
