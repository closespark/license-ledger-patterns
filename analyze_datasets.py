#!/usr/bin/env python3
"""
Cross-Dataset Pattern Analysis CLI

Analyze structural patterns across business licenses, city contracts,
and delinquent property tax records.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

from cross_dataset_analyzer import CrossDatasetAnalyzer, format_report


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze patterns across municipal datasets (licenses, contracts, taxes).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run analysis with default data files
  python analyze_datasets.py
  
  # Specify custom data paths
  python analyze_datasets.py --licenses data/licenses.csv --contracts data/contracts.csv --taxes data/taxes.csv
  
  # Save report to file
  python analyze_datasets.py --output report.txt
  
  # Export results as JSON
  python analyze_datasets.py --json results.json
        """
    )
    
    parser.add_argument(
        '--licenses', '-l',
        default='data/Business_Licenses_20251230.csv',
        help='Path to business licenses CSV file'
    )
    
    parser.add_argument(
        '--contracts', '-c',
        default='data/City_Contracts_20251230.csv',
        help='Path to city contracts CSV file'
    )
    
    parser.add_argument(
        '--taxes', '-t',
        default='data/Delinquent_Real_Estate_Taxes_(Six_Months_or_More)_20251230.csv',
        help='Path to delinquent taxes CSV file'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Path to save text report (default: print to stdout)'
    )
    
    parser.add_argument(
        '--json', '-j',
        help='Path to save JSON export of full results'
    )
    
    args = parser.parse_args()
    
    try:
        # Validate file paths
        for name, path in [('licenses', args.licenses), 
                          ('contracts', args.contracts), 
                          ('taxes', args.taxes)]:
            if not Path(path).exists():
                print(f"Error: {name} file not found: {path}", file=sys.stderr)
                sys.exit(1)
        
        # Initialize analyzer
        print("=" * 80)
        print("CROSS-DATASET PATTERN ANALYSIS")
        print("=" * 80)
        print(f"\nLoading datasets...")
        print(f"  - Business Licenses: {args.licenses}")
        print(f"  - City Contracts: {args.contracts}")
        print(f"  - Delinquent Taxes: {args.taxes}")
        
        analyzer = CrossDatasetAnalyzer(
            licenses_path=args.licenses,
            contracts_path=args.contracts,
            taxes_path=args.taxes
        )
        
        print(f"\nDatasets loaded successfully:")
        print(f"  - {len(analyzer.licenses):,} business licenses")
        print(f"  - {len(analyzer.contracts):,} city contracts")
        print(f"  - {len(analyzer.taxes):,} delinquent tax records")
        
        # Run comprehensive analysis
        print("\n" + "-" * 80)
        results = analyzer.generate_comprehensive_report()
        print("-" * 80)
        
        # Generate formatted report
        report = format_report(results)
        
        # Output report
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\n✓ Text report saved to: {args.output}")
        else:
            print(report)
        
        # Export JSON if requested
        if args.json:
            # Convert any non-serializable objects
            def json_serializer(obj):
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                elif hasattr(obj, 'tolist'):
                    return obj.tolist()
                else:
                    return str(obj)
            
            with open(args.json, 'w') as f:
                json.dump(results, f, indent=2, default=json_serializer)
            print(f"✓ JSON export saved to: {args.json}")
        
        print("\n✓ Analysis complete!")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
