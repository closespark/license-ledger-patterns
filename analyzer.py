"""
License Ledger Patterns - Core Analysis Module

Analyzes municipal business license data to surface structural patterns:
- Address density (multiple licenses at same address)
- Name similarity (potentially related entities)
- DBA usage patterns
- Temporal clustering (unusual timing patterns)
- Geographic concentration

Designed for neutral, data-driven investigation by journalists and auditors.
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import re


class LicenseAnalyzer:
    """Main analyzer for business license data patterns."""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize analyzer with license data.
        
        Expected columns:
        - license_id: Unique identifier
        - business_name: Legal business name
        - dba_name: Doing Business As name (optional)
        - address: Physical address
        - city: City
        - state: State
        - zip_code: ZIP code
        - issue_date: License issue date
        - license_type: Type of license
        - owner_name: Business owner name (optional)
        """
        self.data = data.copy()
        self._normalize_data()
        
    def _normalize_data(self):
        """Normalize data for consistent analysis."""
        # Normalize addresses
        if 'address' in self.data.columns:
            self.data['address_normalized'] = self.data['address'].str.upper().str.strip()
            self.data['address_normalized'] = self.data['address_normalized'].str.replace(r'\s+', ' ', regex=True)
        
        # Normalize names
        if 'business_name' in self.data.columns:
            self.data['business_name_normalized'] = self.data['business_name'].str.upper().str.strip()
        
        # Parse dates
        if 'issue_date' in self.data.columns:
            self.data['issue_date'] = pd.to_datetime(self.data['issue_date'], errors='coerce')
        
    def analyze_address_density(self, threshold: int = 3) -> pd.DataFrame:
        """
        Identify addresses with multiple licenses.
        
        Args:
            threshold: Minimum number of licenses to flag (default: 3)
            
        Returns:
            DataFrame with addresses, license counts, and associated businesses
        """
        if 'address_normalized' not in self.data.columns:
            return pd.DataFrame()
        
        # Group by normalized address
        address_groups = self.data.groupby('address_normalized').agg({
            'license_id': 'count',
            'business_name': lambda x: list(x.unique()),
            'dba_name': lambda x: list(x.dropna().unique()) if 'dba_name' in self.data.columns else [],
            'license_type': lambda x: list(x.unique()) if 'license_type' in self.data.columns else [],
            'issue_date': lambda x: list(x.dropna()) if 'issue_date' in self.data.columns else []
        }).reset_index()
        
        address_groups.columns = ['address', 'license_count', 'businesses', 'dba_names', 'license_types', 'issue_dates']
        
        # Filter by threshold
        flagged = address_groups[address_groups['license_count'] >= threshold].copy()
        flagged = flagged.sort_values('license_count', ascending=False)
        
        # Add risk score
        flagged['risk_score'] = flagged['license_count'] / flagged['license_count'].max()
        
        # Add interpretation
        flagged['pattern_type'] = 'ADDRESS_CLUSTERING'
        flagged['why_it_matters'] = flagged.apply(
            lambda row: f"{row['license_count']} licenses at single address. Could indicate: "
                       f"shared office space, shell companies, or legitimate business center.",
            axis=1
        )
        
        return flagged
    
    def analyze_name_similarity(self, threshold: float = 0.85) -> List[Dict]:
        """
        Find businesses with similar names using fuzzy matching.
        
        Args:
            threshold: Similarity threshold (0-1, default: 0.85)
            
        Returns:
            List of similar name clusters
        """
        try:
            from Levenshtein import ratio
        except ImportError:
            print("Warning: python-Levenshtein not installed. Skipping name similarity analysis.")
            return []
        
        if 'business_name_normalized' not in self.data.columns:
            return []
        
        names = self.data['business_name_normalized'].dropna().unique()
        clusters = []
        processed = set()
        
        for i, name1 in enumerate(names):
            if name1 in processed:
                continue
                
            cluster = [name1]
            for name2 in names[i+1:]:
                if name2 not in processed:
                    similarity = ratio(name1, name2)
                    if similarity >= threshold:
                        cluster.append(name2)
                        processed.add(name2)
            
            if len(cluster) > 1:
                processed.add(name1)
                # Get license details for this cluster
                cluster_licenses = self.data[
                    self.data['business_name_normalized'].isin(cluster)
                ]
                
                clusters.append({
                    'cluster_size': len(cluster),
                    'names': cluster,
                    'license_count': len(cluster_licenses),
                    'addresses': cluster_licenses['address'].unique().tolist() if 'address' in cluster_licenses.columns else [],
                    'pattern_type': 'NAME_SIMILARITY',
                    'risk_score': min(len(cluster) / 10.0, 1.0),  # Normalized score capped at 1.0
                    'why_it_matters': f"{len(cluster)} similar business names found. Could indicate: "
                                     f"related entities, franchises, or attempts to obscure ownership."
                })
        
        # Normalize risk scores based on largest cluster
        if clusters:
            max_cluster_size = max(c['cluster_size'] for c in clusters)
            for cluster in clusters:
                cluster['risk_score'] = cluster['cluster_size'] / max_cluster_size
        
        return sorted(clusters, key=lambda x: x['cluster_size'], reverse=True)
    
    def analyze_dba_patterns(self) -> pd.DataFrame:
        """
        Analyze DBA (Doing Business As) name patterns.
        
        Returns:
            DataFrame with DBA usage patterns and anomalies
        """
        if 'dba_name' not in self.data.columns:
            return pd.DataFrame()
        
        # Find businesses with multiple DBAs
        dba_data = self.data[self.data['dba_name'].notna()].copy()
        
        if len(dba_data) == 0:
            return pd.DataFrame()
        
        # Group by business to find multiple DBAs
        business_dbas = dba_data.groupby('business_name').agg({
            'dba_name': lambda x: list(x.unique()),
            'license_id': 'count',
            'address': lambda x: list(x.unique()) if 'address' in dba_data.columns else []
        }).reset_index()
        
        business_dbas['dba_count'] = business_dbas['dba_name'].apply(len)
        
        # Also find same DBA used by multiple businesses
        dba_businesses = dba_data.groupby('dba_name').agg({
            'business_name': lambda x: list(x.unique()),
            'license_id': 'count',
            'address': lambda x: list(x.unique()) if 'address' in dba_data.columns else []
        }).reset_index()
        
        dba_businesses['business_count'] = dba_businesses['business_name'].apply(len)
        
        # Combine findings
        multiple_dbas = business_dbas[business_dbas['dba_count'] > 1].copy()
        if len(multiple_dbas) > 0:
            multiple_dbas['pattern_type'] = 'MULTIPLE_DBAS_PER_BUSINESS'
            max_dba_count = multiple_dbas['dba_count'].max()
            multiple_dbas['risk_score'] = multiple_dbas['dba_count'] / max_dba_count if max_dba_count > 0 else 0
            multiple_dbas['why_it_matters'] = multiple_dbas.apply(
                lambda row: f"Business operates under {row['dba_count']} different DBAs. "
                           f"Could indicate: legitimate diversification or complexity obscuring ownership.",
                axis=1
            )
        
        shared_dbas = dba_businesses[dba_businesses['business_count'] > 1].copy()
        if len(shared_dbas) > 0:
            shared_dbas['pattern_type'] = 'SHARED_DBA'
            max_business_count = shared_dbas['business_count'].max()
            shared_dbas['risk_score'] = shared_dbas['business_count'] / max_business_count if max_business_count > 0 else 0
            shared_dbas['why_it_matters'] = shared_dbas.apply(
                lambda row: f"DBA used by {row['business_count']} different businesses. "
                           f"Could indicate: related entities or naming conflicts.",
                axis=1
            )
        
        return pd.concat([multiple_dbas, shared_dbas], ignore_index=True)
    
    def analyze_temporal_clustering(self, window_days: int = 7, threshold: int = 5) -> pd.DataFrame:
        """
        Identify unusual temporal patterns in license issuance.
        
        Args:
            window_days: Time window to check (default: 7 days)
            threshold: Minimum licenses in window to flag (default: 5)
            
        Returns:
            DataFrame with temporal clusters
        """
        if 'issue_date' not in self.data.columns:
            return pd.DataFrame()
        
        dated_licenses = self.data[self.data['issue_date'].notna()].copy()
        dated_licenses = dated_licenses.sort_values('issue_date')
        
        clusters = []
        
        for i, row in dated_licenses.iterrows():
            date = row['issue_date']
            window_start = date - timedelta(days=window_days)
            window_end = date + timedelta(days=window_days)
            
            # Find licenses in window
            in_window = dated_licenses[
                (dated_licenses['issue_date'] >= window_start) &
                (dated_licenses['issue_date'] <= window_end)
            ]
            
            if len(in_window) >= threshold:
                # Check if we already have this cluster
                cluster_key = f"{window_start.date()}_{window_end.date()}"
                
                clusters.append({
                    'window_start': window_start,
                    'window_end': window_end,
                    'license_count': len(in_window),
                    'businesses': in_window['business_name'].unique().tolist(),
                    'addresses': in_window['address'].unique().tolist() if 'address' in in_window.columns else [],
                    'pattern_type': 'TEMPORAL_CLUSTERING',
                    'cluster_key': cluster_key
                })
        
        if not clusters:
            return pd.DataFrame()
        
        # Convert to DataFrame and deduplicate
        cluster_df = pd.DataFrame(clusters)
        cluster_df = cluster_df.drop_duplicates(subset=['cluster_key'])
        cluster_df = cluster_df.sort_values('license_count', ascending=False)
        
        # Add risk scores
        cluster_df['risk_score'] = cluster_df['license_count'] / cluster_df['license_count'].max()
        cluster_df['why_it_matters'] = cluster_df.apply(
            lambda row: f"{row['license_count']} licenses issued within {window_days} days. "
                       f"Could indicate: processing batch, coordinated filing, or administrative event.",
            axis=1
        )
        
        return cluster_df.drop('cluster_key', axis=1)
    
    def analyze_geographic_concentration(self, zip_threshold: int = 10) -> pd.DataFrame:
        """
        Identify geographic concentration patterns by ZIP code.
        
        Args:
            zip_threshold: Minimum licenses in ZIP to flag (default: 10)
            
        Returns:
            DataFrame with geographic concentration data
        """
        if 'zip_code' not in self.data.columns:
            return pd.DataFrame()
        
        zip_groups = self.data.groupby('zip_code').agg({
            'license_id': 'count',
            'business_name': lambda x: len(x.unique()),
            'address': lambda x: len(x.unique()) if 'address' in self.data.columns else 0,
            'license_type': lambda x: list(x.unique()) if 'license_type' in self.data.columns else []
        }).reset_index()
        
        zip_groups.columns = ['zip_code', 'license_count', 'unique_businesses', 'unique_addresses', 'license_types']
        
        # Filter by threshold
        flagged = zip_groups[zip_groups['license_count'] >= zip_threshold].copy()
        flagged = flagged.sort_values('license_count', ascending=False)
        
        # Calculate concentration ratio (handle division by zero)
        flagged['concentration_ratio'] = np.where(
            flagged['unique_addresses'] > 0,
            flagged['license_count'] / flagged['unique_addresses'],
            0
        )
        
        # Add risk scores
        if len(flagged) > 0:
            max_concentration = flagged['concentration_ratio'].max()
            flagged['risk_score'] = flagged['concentration_ratio'] / max_concentration if max_concentration > 0 else 0
        else:
            flagged['risk_score'] = 0
        flagged['pattern_type'] = 'GEOGRAPHIC_CONCENTRATION'
        flagged['why_it_matters'] = flagged.apply(
            lambda row: f"{row['license_count']} licenses in ZIP {row['zip_code']} "
                       f"({row['license_count']/row['unique_addresses']:.1f} licenses per address). "
                       f"Could indicate: business district, registered agent service, or shell company hub.",
            axis=1
        )
        
        return flagged
    
    def generate_summary_report(self) -> Dict:
        """
        Generate comprehensive summary of all analyses.
        
        Returns:
            Dictionary with summary statistics and top findings
        """
        summary = {
            'total_licenses': len(self.data),
            'unique_businesses': len(self.data['business_name'].unique()) if 'business_name' in self.data.columns else 0,
            'unique_addresses': len(self.data['address'].unique()) if 'address' in self.data.columns else 0,
            'date_range': {
                'earliest': self.data['issue_date'].min() if 'issue_date' in self.data.columns else None,
                'latest': self.data['issue_date'].max() if 'issue_date' in self.data.columns else None
            },
            'analyses': {}
        }
        
        # Run all analyses
        address_density = self.analyze_address_density()
        if len(address_density) > 0:
            summary['analyses']['address_density'] = {
                'flagged_addresses': len(address_density),
                'top_addresses': address_density.head(5)[['address', 'license_count', 'risk_score']].to_dict('records')
            }
        
        name_similarity = self.analyze_name_similarity()
        if name_similarity:
            summary['analyses']['name_similarity'] = {
                'clusters_found': len(name_similarity),
                'top_clusters': name_similarity[:5]
            }
        
        dba_patterns = self.analyze_dba_patterns()
        if len(dba_patterns) > 0:
            summary['analyses']['dba_patterns'] = {
                'anomalies_found': len(dba_patterns),
                'top_patterns': dba_patterns.head(5).to_dict('records')
            }
        
        temporal = self.analyze_temporal_clustering()
        if len(temporal) > 0:
            summary['analyses']['temporal_clustering'] = {
                'clusters_found': len(temporal),
                'top_clusters': temporal.head(5).to_dict('records')
            }
        
        geographic = self.analyze_geographic_concentration()
        if len(geographic) > 0:
            summary['analyses']['geographic_concentration'] = {
                'concentrated_zips': len(geographic),
                'top_zips': geographic.head(5).to_dict('records')
            }
        
        return summary
