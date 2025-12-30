"""
License Ledger Patterns - Reporting Module

Generates formatted reports suitable for journalists and auditors.
"""

import pandas as pd
from typing import Dict, List, Any
from datetime import datetime
import json


class Reporter:
    """Generates formatted reports from analysis results."""
    
    def __init__(self, analyzer_results: Dict):
        """
        Initialize reporter with analysis results.
        
        Args:
            analyzer_results: Dictionary of analysis results from LicenseAnalyzer
        """
        self.results = analyzer_results
    
    @staticmethod
    def format_table(df: pd.DataFrame, title: str = "", max_rows: int = 20) -> str:
        """
        Format DataFrame as readable table.
        
        Args:
            df: DataFrame to format
            title: Optional title
            max_rows: Maximum rows to display
            
        Returns:
            Formatted table string
        """
        if df is None or len(df) == 0:
            return f"\n{title}\n{'='*80}\nNo data to display.\n"
        
        output = ["\n" + "="*80]
        if title:
            output.append(title)
            output.append("="*80)
        
        # Limit rows
        display_df = df.head(max_rows)
        
        # Format based on columns present
        table_str = display_df.to_string(index=False, max_colwidth=50)
        output.append(table_str)
        
        if len(df) > max_rows:
            output.append(f"\n... and {len(df) - max_rows} more rows")
        
        output.append("="*80)
        return "\n".join(output)
    
    @staticmethod
    def format_list(items: List[Dict], title: str = "", max_items: int = 10) -> str:
        """
        Format list of dictionaries as readable output.
        
        Args:
            items: List of dictionaries
            title: Optional title
            max_items: Maximum items to display
            
        Returns:
            Formatted list string
        """
        if not items:
            return f"\n{title}\n{'='*80}\nNo items to display.\n"
        
        output = ["\n" + "="*80]
        if title:
            output.append(title)
            output.append("="*80)
        
        for i, item in enumerate(items[:max_items], 1):
            output.append(f"\n{i}. {'-'*76}")
            for key, value in item.items():
                if isinstance(value, list):
                    if len(value) > 5:
                        value = value[:5] + [f"... and {len(value)-5} more"]
                    output.append(f"   {key}: {value}")
                elif isinstance(value, float):
                    output.append(f"   {key}: {value:.3f}")
                else:
                    output.append(f"   {key}: {value}")
        
        if len(items) > max_items:
            output.append(f"\n... and {len(items) - max_items} more items")
        
        output.append("="*80)
        return "\n".join(output)
    
    def generate_address_density_report(self, df: pd.DataFrame) -> str:
        """Generate formatted report for address density analysis."""
        if df is None or len(df) == 0:
            return "\nADDRESS DENSITY ANALYSIS\nNo clustering detected.\n"
        
        report_df = df[['address', 'license_count', 'risk_score', 'why_it_matters']].copy()
        return self.format_table(
            report_df,
            title="ADDRESS DENSITY ANALYSIS - Multiple Licenses at Same Address"
        )
    
    def generate_name_similarity_report(self, clusters: List[Dict]) -> str:
        """Generate formatted report for name similarity analysis."""
        if not clusters:
            return "\nNAME SIMILARITY ANALYSIS\nNo similar names detected.\n"
        
        return self.format_list(
            clusters,
            title="NAME SIMILARITY ANALYSIS - Potentially Related Business Names"
        )
    
    def generate_dba_patterns_report(self, df: pd.DataFrame) -> str:
        """Generate formatted report for DBA patterns analysis."""
        if df is None or len(df) == 0:
            return "\nDBA PATTERN ANALYSIS\nNo anomalous DBA patterns detected.\n"
        
        # Split by pattern type for clearer reporting
        output = ["\n" + "="*80]
        output.append("DBA PATTERN ANALYSIS - Doing Business As Name Patterns")
        output.append("="*80)
        
        if 'pattern_type' in df.columns:
            for pattern_type in df['pattern_type'].unique():
                subset = df[df['pattern_type'] == pattern_type]
                output.append(f"\n{pattern_type}:")
                output.append("-"*80)
                
                for _, row in subset.head(10).iterrows():
                    output.append(f"\n{row.get('business_name', row.get('dba_name', 'Unknown'))}")
                    output.append(f"  Risk Score: {row.get('risk_score', 0):.3f}")
                    output.append(f"  {row.get('why_it_matters', '')}")
        
        output.append("="*80)
        return "\n".join(output)
    
    def generate_temporal_clustering_report(self, df: pd.DataFrame) -> str:
        """Generate formatted report for temporal clustering analysis."""
        if df is None or len(df) == 0:
            return "\nTEMPORAL CLUSTERING ANALYSIS\nNo unusual timing patterns detected.\n"
        
        output = ["\n" + "="*80]
        output.append("TEMPORAL CLUSTERING ANALYSIS - Unusual Timing Patterns")
        output.append("="*80)
        
        for i, row in df.head(15).iterrows():
            output.append(f"\nCluster {i+1}:")
            output.append(f"  Period: {row['window_start'].date()} to {row['window_end'].date()}")
            output.append(f"  Licenses: {row['license_count']}")
            output.append(f"  Risk Score: {row.get('risk_score', 0):.3f}")
            output.append(f"  {row.get('why_it_matters', '')}")
            
            if 'businesses' in row and row['businesses']:
                biz_list = row['businesses'][:5]
                if len(row['businesses']) > 5:
                    biz_list.append(f"... and {len(row['businesses'])-5} more")
                output.append(f"  Sample Businesses: {biz_list}")
        
        output.append("="*80)
        return "\n".join(output)
    
    def generate_geographic_concentration_report(self, df: pd.DataFrame) -> str:
        """Generate formatted report for geographic concentration analysis."""
        if df is None or len(df) == 0:
            return "\nGEOGRAPHIC CONCENTRATION ANALYSIS\nNo unusual concentration detected.\n"
        
        report_df = df[['zip_code', 'license_count', 'unique_addresses', 'concentration_ratio', 'risk_score']].copy()
        report_df.columns = ['ZIP Code', 'Licenses', 'Addresses', 'Licenses/Address', 'Risk Score']
        
        return self.format_table(
            report_df,
            title="GEOGRAPHIC CONCENTRATION ANALYSIS - License Density by ZIP Code"
        )
    
    def generate_executive_summary(self, summary: Dict) -> str:
        """Generate executive summary of all analyses."""
        output = ["\n" + "="*80]
        output.append("EXECUTIVE SUMMARY - License Ledger Pattern Analysis")
        output.append("="*80)
        output.append(f"\nDataset Overview:")
        output.append(f"  Total Licenses: {summary.get('total_licenses', 0):,}")
        output.append(f"  Unique Businesses: {summary.get('unique_businesses', 0):,}")
        output.append(f"  Unique Addresses: {summary.get('unique_addresses', 0):,}")
        
        if summary.get('date_range'):
            dr = summary['date_range']
            if dr.get('earliest') and dr.get('latest'):
                output.append(f"  Date Range: {dr['earliest'].date()} to {dr['latest'].date()}")
        
        output.append("\nKey Findings:")
        output.append("-"*80)
        
        analyses = summary.get('analyses', {})
        
        if 'address_density' in analyses:
            ad = analyses['address_density']
            output.append(f"\n✓ ADDRESS CLUSTERING: {ad.get('flagged_addresses', 0)} addresses flagged")
            if ad.get('top_addresses'):
                top = ad['top_addresses'][0]
                output.append(f"  Highest: {top.get('license_count', 0)} licenses at single address")
        
        if 'name_similarity' in analyses:
            ns = analyses['name_similarity']
            output.append(f"\n✓ NAME SIMILARITY: {ns.get('clusters_found', 0)} clusters of similar names")
            if ns.get('top_clusters'):
                top = ns['top_clusters'][0]
                output.append(f"  Largest cluster: {top.get('cluster_size', 0)} similar names")
        
        if 'dba_patterns' in analyses:
            dp = analyses['dba_patterns']
            output.append(f"\n✓ DBA PATTERNS: {dp.get('anomalies_found', 0)} anomalous patterns")
        
        if 'temporal_clustering' in analyses:
            tc = analyses['temporal_clustering']
            output.append(f"\n✓ TEMPORAL CLUSTERING: {tc.get('clusters_found', 0)} time-based clusters")
            if tc.get('top_clusters'):
                top = tc['top_clusters'][0]
                output.append(f"  Largest spike: {top.get('license_count', 0)} licenses in short period")
        
        if 'geographic_concentration' in analyses:
            gc = analyses['geographic_concentration']
            output.append(f"\n✓ GEOGRAPHIC CONCENTRATION: {gc.get('concentrated_zips', 0)} ZIP codes flagged")
        
        output.append("\n" + "="*80)
        output.append("\nNEXT STEPS FOR VALIDATION:")
        output.append("-"*80)
        output.append("1. Cross-reference flagged addresses with business registries")
        output.append("2. Investigate ownership networks for similar business names")
        output.append("3. Review temporal clusters for administrative explanations")
        output.append("4. Map geographic concentrations against known business districts")
        output.append("5. Interview businesses with unusual DBA patterns")
        output.append("6. Check public records for additional ownership information")
        output.append("="*80 + "\n")
        
        return "\n".join(output)
    
    def generate_full_report(self, 
                            address_density: pd.DataFrame,
                            name_similarity: List[Dict],
                            dba_patterns: pd.DataFrame,
                            temporal: pd.DataFrame,
                            geographic: pd.DataFrame,
                            summary: Dict) -> str:
        """
        Generate complete formatted report.
        
        Args:
            address_density: Address density analysis results
            name_similarity: Name similarity analysis results
            dba_patterns: DBA pattern analysis results
            temporal: Temporal clustering analysis results
            geographic: Geographic concentration analysis results
            summary: Summary statistics
            
        Returns:
            Complete formatted report string
        """
        report_parts = [
            self.generate_executive_summary(summary),
            self.generate_address_density_report(address_density),
            self.generate_name_similarity_report(name_similarity),
            self.generate_dba_patterns_report(dba_patterns),
            self.generate_temporal_clustering_report(temporal),
            self.generate_geographic_concentration_report(geographic)
        ]
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"\nLICENSE LEDGER PATTERN ANALYSIS REPORT\nGenerated: {timestamp}\n"
        
        return header + "\n".join(report_parts)
    
    def export_to_json(self, output_path: str, 
                      address_density: pd.DataFrame,
                      name_similarity: List[Dict],
                      dba_patterns: pd.DataFrame,
                      temporal: pd.DataFrame,
                      geographic: pd.DataFrame,
                      summary: Dict):
        """
        Export all results to JSON file.
        
        Args:
            output_path: Path to save JSON file
            address_density: Address density results
            name_similarity: Name similarity results
            dba_patterns: DBA pattern results
            temporal: Temporal clustering results
            geographic: Geographic concentration results
            summary: Summary statistics
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'summary': self._serialize_for_json(summary),
            'findings': {
                'address_density': address_density.to_dict('records') if address_density is not None and len(address_density) > 0 else [],
                'name_similarity': name_similarity,
                'dba_patterns': dba_patterns.to_dict('records') if dba_patterns is not None and len(dba_patterns) > 0 else [],
                'temporal_clustering': temporal.to_dict('records') if temporal is not None and len(temporal) > 0 else [],
                'geographic_concentration': geographic.to_dict('records') if geographic is not None and len(geographic) > 0 else []
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    @staticmethod
    def _serialize_for_json(obj):
        """Helper to serialize objects for JSON export."""
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: Reporter._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [Reporter._serialize_for_json(item) for item in obj]
        else:
            return obj
