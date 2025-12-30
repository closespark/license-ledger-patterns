# License Ledger Patterns

Analyze city business license data to surface structural risk patterns—address clustering, naming repetition, temporal spikes, and network overlap. Built for journalists, auditors, and civic investigators to follow signals before allegations.

## Overview

This tool performs neutral, data-driven analysis of municipal business license data to identify structural patterns that may warrant further investigation. It surfaces anomalies without making accusations, explains why they matter, and suggests next steps for validation.

## Features

### Pattern Detection

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

## Data Format

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

## Testing

Run the tool with sample data:

```bash
python cli.py sample_data.csv
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
