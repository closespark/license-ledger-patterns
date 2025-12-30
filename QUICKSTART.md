# Quick Start Guide

Get up and running with License Ledger Patterns in 5 minutes.

## Installation

```bash
pip install pandas numpy python-Levenshtein
```

## Basic Usage

### 1. Prepare Your Data

Create or obtain a CSV file with license data. Minimum required columns:
- `license_id`
- `business_name`
- `address`

Recommended additional columns:
- `dba_name`, `city`, `state`, `zip_code`, `issue_date`, `license_type`, `owner_name`

### 2. Run Analysis

```bash
python cli.py your_licenses.csv
```

### 3. Review Results

The tool will display:
- **Executive Summary**: Overview of all findings
- **Address Density**: Multiple licenses at same address
- **Name Similarity**: Related business names
- **DBA Patterns**: Unusual DBA usage
- **Temporal Clustering**: Time-based patterns
- **Geographic Concentration**: ZIP code density

### 4. Save Output

```bash
# Save text report
python cli.py your_licenses.csv --output report.txt

# Save JSON for further analysis
python cli.py your_licenses.csv --json findings.json
```

## Try It Now

Test with included sample data:

```bash
python cli.py sample_data.csv
```

This demonstrates all features with realistic patterns:
- 5 addresses with multiple licenses
- 3 clusters of similar business names
- DBA patterns
- Temporal spikes in license issuance
- Geographic concentration

## Adjust Thresholds

Fine-tune sensitivity:

```bash
python cli.py your_licenses.csv \
  --address-threshold 5      # More licenses needed to flag address
  --name-similarity 0.9      # Higher similarity required for matches
  --temporal-window 14       # Wider time window for clustering
  --zip-threshold 20         # More licenses needed to flag ZIP
```

## Next Steps

1. **Review Findings**: Each pattern includes "why it matters" context
2. **Validate**: Follow suggested validation steps in the report
3. **Investigate**: Cross-reference with public records
4. **Document**: Keep neutral, data-driven notes

## Common Data Formats

### From Excel
```bash
# Export your Excel file as CSV, then:
python cli.py exported_licenses.csv
```

### From Database
```python
import pandas as pd
from analyzer import LicenseAnalyzer
from reporter import Reporter

# Load from database
df = pd.read_sql("SELECT * FROM licenses", connection)

# Analyze
analyzer = LicenseAnalyzer(df)
summary = analyzer.generate_summary_report()
# ... etc
```

## Programmatic Usage

For custom analysis workflows:

```python
from analyzer import LicenseAnalyzer
import pandas as pd

# Load data
data = pd.read_csv('licenses.csv')

# Initialize and analyze
analyzer = LicenseAnalyzer(data)

# Get specific findings
address_density = analyzer.analyze_address_density(threshold=3)
print(f"Found {len(address_density)} flagged addresses")

# Access top finding
if len(address_density) > 0:
    top = address_density.iloc[0]
    print(f"Top: {top['license_count']} licenses at {top['address']}")
```

## Tips

- **Start broad**: Use default thresholds first
- **Refine**: Adjust based on your dataset size
- **Context matters**: Urban areas naturally have higher density
- **Validate everything**: Patterns need investigation
- **Document method**: Note thresholds used in reporting

## Troubleshooting

### "Missing required column"
Ensure your CSV has `license_id`, `business_name`, and `address` columns.

### "No patterns detected"
Try lowering thresholds or check if your data has the optional columns.

### Import errors
Install missing dependencies: `pip install -r requirements.txt`

## Support

- See full documentation in README.md
- Review example.py for programmatic usage
- Check CONTRIBUTING.md for extending functionality
- Open GitHub issue for bugs or questions

---

**Ready?** Run `python cli.py sample_data.csv` to see it in action!
