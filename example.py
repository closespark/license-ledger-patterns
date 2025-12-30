#!/usr/bin/env python3
"""
Example: Programmatic usage of License Ledger Patterns

This script demonstrates how to use the analyzer and reporter
programmatically instead of through the CLI.
"""

from analyzer import LicenseAnalyzer
from reporter import Reporter
import pandas as pd


def main():
    """Example analysis workflow."""
    
    # Load your data
    print("Loading sample data...")
    data = pd.read_csv('sample_data.csv')
    print(f"Loaded {len(data):,} license records\n")
    
    # Initialize analyzer
    print("Initializing analyzer...")
    analyzer = LicenseAnalyzer(data)
    
    # Run individual analyses
    print("\n1. Analyzing address density...")
    address_density = analyzer.analyze_address_density(threshold=3)
    print(f"   Found {len(address_density)} flagged addresses")
    
    print("\n2. Analyzing name similarity...")
    name_similarity = analyzer.analyze_name_similarity(threshold=0.85)
    print(f"   Found {len(name_similarity)} name clusters")
    
    print("\n3. Analyzing DBA patterns...")
    dba_patterns = analyzer.analyze_dba_patterns()
    print(f"   Found {len(dba_patterns)} DBA anomalies")
    
    print("\n4. Analyzing temporal clustering...")
    temporal = analyzer.analyze_temporal_clustering(window_days=7, threshold=5)
    print(f"   Found {len(temporal)} temporal clusters")
    
    print("\n5. Analyzing geographic concentration...")
    geographic = analyzer.analyze_geographic_concentration(zip_threshold=10)
    print(f"   Found {len(geographic)} concentrated ZIP codes")
    
    # Generate summary
    print("\n6. Generating summary report...")
    summary = analyzer.generate_summary_report()
    
    # Create reporter and generate full report
    print("\nGenerating formatted report...")
    reporter = Reporter(summary)
    
    full_report = reporter.generate_full_report(
        address_density=address_density,
        name_similarity=name_similarity,
        dba_patterns=dba_patterns,
        temporal=temporal,
        geographic=geographic,
        summary=summary
    )
    
    # Print report
    print(full_report)
    
    # Export to JSON
    print("\nExporting to JSON...")
    reporter.export_to_json(
        output_path='example_output.json',
        address_density=address_density,
        name_similarity=name_similarity,
        dba_patterns=dba_patterns,
        temporal=temporal,
        geographic=geographic,
        summary=summary
    )
    print("✓ Exported to example_output.json")
    
    # Access specific findings programmatically
    print("\n" + "="*80)
    print("PROGRAMMATIC ACCESS EXAMPLES")
    print("="*80)
    
    # Example: Get top 3 addresses with most licenses
    if len(address_density) > 0:
        print("\nTop 3 addresses by license count:")
        for i, row in address_density.head(3).iterrows():
            print(f"  {row['license_count']} licenses at {row['address']}")
            print(f"    Risk score: {row['risk_score']:.3f}")
    
    # Example: Get largest name similarity cluster
    if name_similarity:
        largest_cluster = name_similarity[0]
        print(f"\nLargest name cluster has {largest_cluster['cluster_size']} similar names:")
        for name in largest_cluster['names']:
            print(f"  - {name}")
    
    # Example: Check summary statistics
    print(f"\nDataset statistics:")
    print(f"  Total licenses analyzed: {summary['total_licenses']:,}")
    print(f"  Unique businesses: {summary['unique_businesses']:,}")
    print(f"  Unique addresses: {summary['unique_addresses']:,}")
    print(f"  Patterns detected: {len(summary['analyses'])} types")
    
    print("\n✓ Analysis complete!")


if __name__ == '__main__':
    main()
