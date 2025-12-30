#!/usr/bin/env python3
"""
License Ledger Patterns - Command Line Interface

Analyze municipal business license data for structural patterns.
"""

import argparse
import sys
import pandas as pd
from pathlib import Path
from analyzer import LicenseAnalyzer
from reporter import Reporter


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load license data from CSV or Excel file.
    
    Args:
        file_path: Path to data file
        
    Returns:
        DataFrame with license data
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    # Determine file type and load
    if path.suffix.lower() == '.csv':
        return pd.read_csv(file_path)
    elif path.suffix.lower() in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}. Use CSV or Excel.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze municipal business license data for structural patterns.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze license data and display report
  python cli.py data/licenses.csv
  
  # Save report to file
  python cli.py data/licenses.csv --output report.txt
  
  # Export findings to JSON
  python cli.py data/licenses.csv --json findings.json
  
  # Adjust thresholds
  python cli.py data/licenses.csv --address-threshold 5 --name-similarity 0.9

Expected CSV Columns:
  Required:
    - license_id: Unique identifier
    - business_name: Legal business name
    - address: Physical address
    
  Optional (but recommended):
    - dba_name: Doing Business As name
    - city: City
    - state: State
    - zip_code: ZIP code
    - issue_date: License issue date (YYYY-MM-DD)
    - license_type: Type of license
    - owner_name: Business owner name
        """
    )
    
    parser.add_argument(
        'data_file',
        help='Path to CSV or Excel file containing license data'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Path to save text report (default: print to stdout)'
    )
    
    parser.add_argument(
        '--json', '-j',
        help='Path to save JSON export of findings'
    )
    
    parser.add_argument(
        '--address-threshold',
        type=int,
        default=3,
        help='Minimum licenses at address to flag (default: 3)'
    )
    
    parser.add_argument(
        '--name-similarity',
        type=float,
        default=0.85,
        help='Name similarity threshold 0-1 (default: 0.85)'
    )
    
    parser.add_argument(
        '--temporal-window',
        type=int,
        default=7,
        help='Days to check for temporal clustering (default: 7)'
    )
    
    parser.add_argument(
        '--temporal-threshold',
        type=int,
        default=5,
        help='Minimum licenses in window to flag (default: 5)'
    )
    
    parser.add_argument(
        '--zip-threshold',
        type=int,
        default=10,
        help='Minimum licenses in ZIP code to flag (default: 10)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load data
        print(f"Loading data from {args.data_file}...")
        data = load_data(args.data_file)
        print(f"Loaded {len(data):,} license records")
        
        # Initialize analyzer
        print("\nInitializing analyzer...")
        analyzer = LicenseAnalyzer(data)
        
        # Run analyses
        print("Running analyses...")
        print("  - Address density analysis...")
        address_density = analyzer.analyze_address_density(threshold=args.address_threshold)
        
        print("  - Name similarity analysis...")
        name_similarity = analyzer.analyze_name_similarity(threshold=args.name_similarity)
        
        print("  - DBA pattern analysis...")
        dba_patterns = analyzer.analyze_dba_patterns()
        
        print("  - Temporal clustering analysis...")
        temporal = analyzer.analyze_temporal_clustering(
            window_days=args.temporal_window,
            threshold=args.temporal_threshold
        )
        
        print("  - Geographic concentration analysis...")
        geographic = analyzer.analyze_geographic_concentration(zip_threshold=args.zip_threshold)
        
        print("  - Generating summary...")
        summary = analyzer.generate_summary_report()
        
        # Generate report
        print("\nGenerating report...")
        reporter = Reporter(summary)
        
        full_report = reporter.generate_full_report(
            address_density=address_density,
            name_similarity=name_similarity,
            dba_patterns=dba_patterns,
            temporal=temporal,
            geographic=geographic,
            summary=summary
        )
        
        # Output report
        if args.output:
            with open(args.output, 'w') as f:
                f.write(full_report)
            print(f"\nReport saved to: {args.output}")
        else:
            print(full_report)
        
        # Export JSON if requested
        if args.json:
            reporter.export_to_json(
                output_path=args.json,
                address_density=address_density,
                name_similarity=name_similarity,
                dba_patterns=dba_patterns,
                temporal=temporal,
                geographic=geographic,
                summary=summary
            )
            print(f"JSON export saved to: {args.json}")
        
        print("\n✓ Analysis complete!")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing required column in data: {e}", file=sys.stderr)
        print("\nPlease ensure your data includes the required columns.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
