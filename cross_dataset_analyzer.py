"""
Cross-Dataset Pattern Analyzer

Analyzes structural patterns across three municipal datasets:
- Business Licenses
- City Contracts  
- Delinquent Property Tax Records

Surfaces patterns including:
- Address clustering across datasets
- Name/DBA similarity between license holders and contract suppliers
- License age vs contract timing relationships
- Procurement type patterns
- Agency concentration in contracts
- Overlaps with tax-delinquent properties
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import re
import warnings

warnings.filterwarnings('ignore')


class CrossDatasetAnalyzer:
    """Analyzer for patterns across business licenses, contracts, and tax records."""
    
    def __init__(self, licenses_path: str, contracts_path: str, taxes_path: str):
        """
        Initialize analyzer with paths to all three datasets.
        
        Args:
            licenses_path: Path to business licenses CSV
            contracts_path: Path to city contracts CSV
            taxes_path: Path to delinquent taxes CSV
        """
        self.licenses = self._load_licenses(licenses_path)
        self.contracts = self._load_contracts(contracts_path)
        self.taxes = self._load_taxes(taxes_path)
        
        # Normalize all data
        self._normalize_addresses()
        self._normalize_names()
        
    def _load_licenses(self, path: str) -> pd.DataFrame:
        """Load and parse business licenses data."""
        df = pd.read_csv(path)
        df.columns = ['business_name', 'dba_name', 'address', 'geo_location']
        return df
    
    def _load_contracts(self, path: str) -> pd.DataFrame:
        """Load and parse city contracts data."""
        df = pd.read_csv(path)
        df.columns = ['agency', 'contract_number', 'contract_value', 'supplier', 
                      'procurement_type', 'description', 'solicitation_type', 
                      'effective_from', 'effective_to']
        
        # Parse contract values
        df['contract_value_numeric'] = df['contract_value'].apply(self._parse_currency)
        
        # Parse dates
        df['effective_from'] = pd.to_datetime(df['effective_from'], errors='coerce')
        df['effective_to'] = pd.to_datetime(df['effective_to'], errors='coerce')
        
        return df
    
    def _load_taxes(self, path: str) -> pd.DataFrame:
        """Load and parse delinquent taxes data."""
        df = pd.read_csv(path)
        df.columns = ['property_code', 'owner_name_1', 'owner_name_2', 'address', 
                      'total_due', 'years_delinquent', 'geo_location']
        
        # Parse numeric fields
        df['total_due'] = pd.to_numeric(df['total_due'], errors='coerce')
        df['years_delinquent'] = pd.to_numeric(df['years_delinquent'], errors='coerce')
        
        return df
    
    @staticmethod
    def _parse_currency(value: Any) -> float:
        """Parse currency string to float."""
        if pd.isna(value):
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        # Remove $, commas, and other formatting
        cleaned = re.sub(r'[^\d.-]', '', str(value))
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0
    
    def _normalize_addresses(self):
        """Normalize addresses across all datasets for matching."""
        def normalize_addr(addr: Any) -> str:
            if pd.isna(addr):
                return ''
            addr = str(addr).upper().strip()
            # Remove extra spaces
            addr = re.sub(r'\s+', ' ', addr)
            # Standardize common abbreviations
            replacements = {
                r'\bSTREET\b': 'ST',
                r'\bAVENUE\b': 'AVE',
                r'\bROAD\b': 'RD',
                r'\bBOULEVARD\b': 'BLVD',
                r'\bDRIVE\b': 'DR',
                r'\bLANE\b': 'LN',
                r'\bCOURT\b': 'CT',
                r'\bPLACE\b': 'PL',
                r'\bCIRCLE\b': 'CIR',
                r'\bHIGHWAY\b': 'HWY',
                r'\bPARKWAY\b': 'PKWY',
                r'\bTURNPIKE\b': 'TPKE',
            }
            for pattern, repl in replacements.items():
                addr = re.sub(pattern, repl, addr)
            return addr
        
        # Normalize addresses in each dataset
        self.licenses['address_normalized'] = self.licenses['address'].apply(normalize_addr)
        self.taxes['address_normalized'] = self.taxes['address'].apply(normalize_addr)
        
    def _normalize_names(self):
        """Normalize business/owner names for matching."""
        def normalize_name(name: Any) -> str:
            if pd.isna(name):
                return ''
            name = str(name).upper().strip()
            # Remove common suffixes
            suffixes = [r'\s+LLC$', r'\s+INC$', r'\s+CORP$', r'\s+CO$', r'\s+LTD$',
                       r'\s+LP$', r'\s+LLP$', r'\s+PC$', r'\s+PLC$', r'\s+CORPORATION$',
                       r'\s+COMPANY$', r'\s+LIMITED$', r'\s+INCORPORATED$']
            for suffix in suffixes:
                name = re.sub(suffix, '', name)
            name = re.sub(r'\s+', ' ', name).strip()
            return name
        
        # Normalize names in each dataset
        self.licenses['business_name_normalized'] = self.licenses['business_name'].apply(normalize_name)
        self.licenses['dba_normalized'] = self.licenses['dba_name'].apply(normalize_name)
        self.contracts['supplier_normalized'] = self.contracts['supplier'].apply(normalize_name)
        self.taxes['owner_normalized'] = self.taxes['owner_name_1'].apply(normalize_name)
        
    def analyze_address_clustering(self, threshold: int = 2) -> Dict[str, Any]:
        """
        Identify addresses that appear across multiple datasets.
        
        Args:
            threshold: Minimum occurrences to flag
            
        Returns:
            Dictionary with clustered addresses and findings
        """
        # Get all unique normalized addresses from licenses and taxes
        license_addresses = set(self.licenses['address_normalized'].dropna().unique())
        tax_addresses = set(self.taxes['address_normalized'].dropna().unique())
        
        # Find addresses in multiple datasets
        shared_addresses = license_addresses.intersection(tax_addresses)
        
        findings = []
        for addr in shared_addresses:
            if not addr:  # Skip empty addresses
                continue
                
            # Get license info
            license_matches = self.licenses[self.licenses['address_normalized'] == addr]
            tax_matches = self.taxes[self.taxes['address_normalized'] == addr]
            
            # Calculate total due
            total_tax_due = tax_matches['total_due'].sum()
            avg_years_delinquent = tax_matches['years_delinquent'].mean()
            
            findings.append({
                'address': addr,
                'license_count': len(license_matches),
                'tax_delinquent_count': len(tax_matches),
                'businesses': license_matches['business_name'].tolist()[:5],
                'total_tax_due': total_tax_due,
                'avg_years_delinquent': avg_years_delinquent,
                'pattern_type': 'ADDRESS_OVERLAP_LICENSE_TAX',
                'risk_score': min(1.0, (len(license_matches) + len(tax_matches)) / 10),
                'why_it_matters': f"Address appears in both business licenses ({len(license_matches)}) "
                                 f"and delinquent tax records ({len(tax_matches)}). "
                                 f"Total tax due: ${total_tax_due:,.2f}. "
                                 f"Could indicate: financial distress, shell company operations, "
                                 f"or properties being used for undisclosed business activities."
            })
        
        # Also analyze addresses with multiple licenses (density within licenses)
        license_addr_counts = self.licenses['address_normalized'].value_counts()
        dense_addresses = license_addr_counts[license_addr_counts >= threshold]
        
        density_findings = []
        for addr, count in dense_addresses.items():
            if not addr:
                continue
            matches = self.licenses[self.licenses['address_normalized'] == addr]
            density_findings.append({
                'address': addr,
                'license_count': count,
                'businesses': matches['business_name'].tolist()[:10],
                'dbas': matches['dba_name'].dropna().tolist()[:10],
                'pattern_type': 'ADDRESS_DENSITY',
                'risk_score': min(1.0, count / 10),
                'why_it_matters': f"{count} business licenses at single address. "
                                 f"Could indicate: shared office space, registered agent services, "
                                 f"shell company hub, or legitimate business center."
            })
        
        # Sort by risk score
        findings.sort(key=lambda x: x['risk_score'], reverse=True)
        density_findings.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return {
            'cross_dataset_overlaps': findings[:50],
            'address_density': density_findings[:50],
            'total_shared_addresses': len(shared_addresses),
            'summary': {
                'total_license_addresses': len(license_addresses),
                'total_tax_addresses': len(tax_addresses),
                'overlap_count': len(shared_addresses),
                'overlap_percentage': round(len(shared_addresses) / max(len(license_addresses), 1) * 100, 2)
            }
        }
    
    def analyze_name_similarity(self, threshold: float = 0.85) -> Dict[str, Any]:
        """
        Find similar names between license holders and contract suppliers.
        
        Args:
            threshold: Similarity threshold (0-1)
            
        Returns:
            Dictionary with name similarity findings
        """
        try:
            from Levenshtein import ratio
        except ImportError:
            return {'error': 'python-Levenshtein not installed', 'matches': []}
        
        # Get unique names from each dataset
        license_names = self.licenses['business_name_normalized'].dropna().unique()
        contract_suppliers = self.contracts['supplier_normalized'].dropna().unique()
        tax_owners = self.taxes['owner_normalized'].dropna().unique()
        
        matches = []
        
        # License holders to contract suppliers
        for license_name in license_names:
            if not license_name or len(license_name) < 3:
                continue
            for supplier in contract_suppliers:
                if not supplier or len(supplier) < 3:
                    continue
                similarity = ratio(license_name, supplier)
                if similarity >= threshold:
                    # Get contract details
                    supplier_contracts = self.contracts[
                        self.contracts['supplier_normalized'] == supplier
                    ]
                    total_value = supplier_contracts['contract_value_numeric'].sum()
                    contract_count = len(supplier_contracts)
                    
                    matches.append({
                        'license_name': license_name,
                        'contract_supplier': supplier,
                        'similarity_score': round(similarity, 3),
                        'contract_count': contract_count,
                        'total_contract_value': total_value,
                        'agencies': supplier_contracts['agency'].unique().tolist(),
                        'pattern_type': 'LICENSE_CONTRACT_NAME_MATCH',
                        'risk_score': round(similarity * min(1.0, contract_count / 5), 3),
                        'why_it_matters': f"Business license holder matches contract supplier with "
                                        f"{similarity*100:.1f}% similarity. {contract_count} contracts "
                                        f"worth ${total_value:,.2f}. Could indicate: legitimate business "
                                        f"relationships or potential self-dealing arrangements."
                    })
        
        # License holders to tax-delinquent property owners
        tax_delinquent_matches = []
        for license_name in license_names:
            if not license_name or len(license_name) < 3:
                continue
            for owner in tax_owners:
                if not owner or len(owner) < 3:
                    continue
                similarity = ratio(license_name, owner)
                if similarity >= threshold:
                    owner_records = self.taxes[self.taxes['owner_normalized'] == owner]
                    total_due = owner_records['total_due'].sum()
                    
                    tax_delinquent_matches.append({
                        'license_name': license_name,
                        'tax_owner': owner,
                        'similarity_score': round(similarity, 3),
                        'property_count': len(owner_records),
                        'total_tax_due': total_due,
                        'pattern_type': 'LICENSE_TAX_OWNER_MATCH',
                        'risk_score': round(similarity * min(1.0, total_due / 10000), 3),
                        'why_it_matters': f"Licensed business name matches tax-delinquent property owner "
                                        f"with {similarity*100:.1f}% similarity. ${total_due:,.2f} in "
                                        f"unpaid taxes. Could indicate: financial distress or business "
                                        f"operating from problematic property."
                    })
        
        # Sort by risk score
        matches.sort(key=lambda x: x['risk_score'], reverse=True)
        tax_delinquent_matches.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return {
            'license_contract_matches': matches[:100],
            'license_tax_owner_matches': tax_delinquent_matches[:100],
            'summary': {
                'total_license_names': len(license_names),
                'total_suppliers': len(contract_suppliers),
                'total_tax_owners': len(tax_owners),
                'license_contract_matches_found': len(matches),
                'license_tax_matches_found': len(tax_delinquent_matches)
            }
        }
    
    def analyze_contract_timing(self) -> Dict[str, Any]:
        """
        Analyze patterns in contract timing and procurement types.
        
        Returns:
            Dictionary with contract timing and type analysis
        """
        contracts = self.contracts.copy()
        
        # Contract duration analysis
        contracts['duration_days'] = (contracts['effective_to'] - contracts['effective_from']).dt.days
        
        # Temporal clustering - contracts starting around same time
        contracts['start_month'] = contracts['effective_from'].dt.to_period('M')
        monthly_counts = contracts.groupby('start_month').size()
        
        # Find months with unusual activity
        mean_monthly = monthly_counts.mean()
        std_monthly = monthly_counts.std()
        threshold = mean_monthly + 2 * std_monthly
        
        unusual_months = []
        for month, count in monthly_counts.items():
            if count > threshold:
                month_contracts = contracts[contracts['start_month'] == month]
                unusual_months.append({
                    'month': str(month),
                    'contract_count': count,
                    'total_value': month_contracts['contract_value_numeric'].sum(),
                    'suppliers': month_contracts['supplier'].unique().tolist()[:10],
                    'agencies': month_contracts['agency'].unique().tolist(),
                    'deviation_from_mean': round((count - mean_monthly) / max(std_monthly, 1), 2),
                    'pattern_type': 'TEMPORAL_SPIKE',
                    'why_it_matters': f"{count} contracts started in {month} (average: {mean_monthly:.1f}). "
                                     f"Could indicate: end-of-fiscal-year spending, coordinated procurement, "
                                     f"or contract bundling."
                })
        
        # Same-day contract awards
        contracts['start_date'] = contracts['effective_from'].dt.date
        daily_counts = contracts.groupby('start_date').size()
        same_day_awards = daily_counts[daily_counts >= 3]
        
        same_day_findings = []
        for date, count in same_day_awards.items():
            day_contracts = contracts[contracts['start_date'] == date]
            same_day_findings.append({
                'date': str(date),
                'contract_count': count,
                'total_value': day_contracts['contract_value_numeric'].sum(),
                'suppliers': day_contracts['supplier'].unique().tolist(),
                'pattern_type': 'SAME_DAY_AWARDS',
                'why_it_matters': f"{count} contracts awarded on same day. "
                                 f"Could indicate: batch processing, coordinated awards, "
                                 f"or expedited approvals."
            })
        
        # Short-duration contracts (potential circumvention of bid requirements)
        short_contracts = contracts[contracts['duration_days'] < 30]
        short_contract_findings = []
        for _, row in short_contracts.iterrows():
            if pd.notna(row['duration_days']):
                short_contract_findings.append({
                    'contract_number': row['contract_number'],
                    'supplier': row['supplier'],
                    'agency': row['agency'],
                    'duration_days': row['duration_days'],
                    'value': row['contract_value_numeric'],
                    'pattern_type': 'SHORT_DURATION',
                    'why_it_matters': f"Contract duration of only {row['duration_days']} days. "
                                     f"Could indicate: emergency procurement, test contract, "
                                     f"or potential bid threshold circumvention."
                })
        
        return {
            'temporal_spikes': unusual_months,
            'same_day_awards': same_day_findings[:50],
            'short_duration_contracts': short_contract_findings[:50],
            'summary': {
                'avg_monthly_contracts': round(mean_monthly, 1),
                'months_with_spikes': len(unusual_months),
                'days_with_multiple_awards': len(same_day_awards),
                'short_duration_count': len(short_contracts)
            }
        }
    
    def analyze_procurement_types(self) -> Dict[str, Any]:
        """
        Analyze procurement type patterns and potential anomalies.
        
        Returns:
            Dictionary with procurement type analysis
        """
        contracts = self.contracts.copy()
        
        # Overall distribution
        procurement_dist = contracts.groupby('procurement_type').agg({
            'contract_number': 'count',
            'contract_value_numeric': 'sum'
        }).reset_index()
        procurement_dist.columns = ['procurement_type', 'count', 'total_value']
        procurement_dist = procurement_dist.sort_values('total_value', ascending=False)
        
        # Supplier concentration by procurement type
        supplier_by_type = {}
        for ptype in contracts['procurement_type'].dropna().unique():
            type_contracts = contracts[contracts['procurement_type'] == ptype]
            supplier_counts = type_contracts['supplier'].value_counts()
            if len(supplier_counts) > 0:
                top_supplier = supplier_counts.index[0]
                top_supplier_share = supplier_counts.iloc[0] / len(type_contracts)
                
                supplier_by_type[ptype] = {
                    'total_contracts': len(type_contracts),
                    'unique_suppliers': len(supplier_counts),
                    'top_supplier': top_supplier,
                    'top_supplier_count': supplier_counts.iloc[0],
                    'top_supplier_share': round(top_supplier_share, 3),
                    'total_value': type_contracts['contract_value_numeric'].sum()
                }
        
        # Non-competitive procurement analysis (Agency Request, Small Purchase, etc.)
        non_competitive_types = ['Agency Request', 'Small Purchase', 'Sole Source', 'Emergency']
        non_competitive = contracts[contracts['procurement_type'].isin(non_competitive_types)]
        
        non_competitive_suppliers = non_competitive.groupby('supplier').agg({
            'contract_number': 'count',
            'contract_value_numeric': 'sum'
        }).reset_index()
        non_competitive_suppliers.columns = ['supplier', 'contract_count', 'total_value']
        non_competitive_suppliers = non_competitive_suppliers.sort_values('total_value', ascending=False)
        
        # Findings for non-competitive procurement
        non_competitive_findings = []
        for _, row in non_competitive_suppliers.head(20).iterrows():
            supplier_contracts = non_competitive[non_competitive['supplier'] == row['supplier']]
            non_competitive_findings.append({
                'supplier': row['supplier'],
                'contract_count': row['contract_count'],
                'total_value': row['total_value'],
                'agencies': supplier_contracts['agency'].unique().tolist(),
                'procurement_types': supplier_contracts['procurement_type'].unique().tolist(),
                'pattern_type': 'NON_COMPETITIVE_CONCENTRATION',
                'why_it_matters': f"Supplier received {row['contract_count']} non-competitive contracts "
                                 f"totaling ${row['total_value']:,.2f}. Could indicate: specialized expertise, "
                                 f"preferred vendor status, or potential favoritism."
            })
        
        return {
            'procurement_distribution': procurement_dist.to_dict('records'),
            'supplier_concentration_by_type': supplier_by_type,
            'non_competitive_suppliers': non_competitive_findings,
            'summary': {
                'total_contracts': len(contracts),
                'unique_procurement_types': contracts['procurement_type'].nunique(),
                'non_competitive_count': len(non_competitive),
                'non_competitive_percentage': round(len(non_competitive) / max(len(contracts), 1) * 100, 2)
            }
        }
    
    def analyze_agency_concentration(self) -> Dict[str, Any]:
        """
        Analyze contract concentration by agency.
        
        Returns:
            Dictionary with agency concentration analysis
        """
        contracts = self.contracts.copy()
        
        # Agency-level statistics
        agency_stats = contracts.groupby('agency').agg({
            'contract_number': 'count',
            'contract_value_numeric': 'sum',
            'supplier': 'nunique'
        }).reset_index()
        agency_stats.columns = ['agency', 'contract_count', 'total_value', 'unique_suppliers']
        
        # Calculate concentration metrics
        agency_stats['avg_value_per_contract'] = agency_stats['total_value'] / agency_stats['contract_count']
        agency_stats['contracts_per_supplier'] = agency_stats['contract_count'] / agency_stats['unique_suppliers']
        
        agency_stats = agency_stats.sort_values('total_value', ascending=False)
        
        # Supplier concentration within agencies
        agency_supplier_concentration = []
        for agency in contracts['agency'].dropna().unique():
            agency_contracts = contracts[contracts['agency'] == agency]
            supplier_values = agency_contracts.groupby('supplier')['contract_value_numeric'].sum()
            
            if len(supplier_values) > 0:
                total_value = supplier_values.sum()
                top_3_value = supplier_values.nlargest(3).sum()
                concentration = top_3_value / max(total_value, 1)
                
                if concentration > 0.5:  # Flag if top 3 suppliers have >50% of value
                    agency_supplier_concentration.append({
                        'agency': agency,
                        'total_contracts': len(agency_contracts),
                        'total_value': total_value,
                        'unique_suppliers': len(supplier_values),
                        'top_3_suppliers': supplier_values.nlargest(3).index.tolist(),
                        'top_3_value': top_3_value,
                        'top_3_share': round(concentration, 3),
                        'pattern_type': 'SUPPLIER_CONCENTRATION',
                        'why_it_matters': f"Top 3 suppliers control {concentration*100:.1f}% of agency's "
                                        f"contract value (${top_3_value:,.2f}). Could indicate: "
                                        f"specialized requirements, limited competition, or preferential treatment."
                    })
        
        # Supplier-agency relationships (suppliers working with multiple agencies)
        supplier_agency = contracts.groupby('supplier')['agency'].nunique().reset_index()
        supplier_agency.columns = ['supplier', 'agency_count']
        multi_agency = supplier_agency[supplier_agency['agency_count'] >= 3]
        
        multi_agency_findings = []
        for _, row in multi_agency.head(20).iterrows():
            supplier_contracts = contracts[contracts['supplier'] == row['supplier']]
            multi_agency_findings.append({
                'supplier': row['supplier'],
                'agency_count': row['agency_count'],
                'agencies': supplier_contracts['agency'].unique().tolist(),
                'total_contracts': len(supplier_contracts),
                'total_value': supplier_contracts['contract_value_numeric'].sum(),
                'pattern_type': 'MULTI_AGENCY_SUPPLIER',
                'why_it_matters': f"Supplier works with {row['agency_count']} different agencies. "
                                 f"Could indicate: broad capabilities, city-wide relationships, "
                                 f"or potential influence across departments."
            })
        
        return {
            'agency_statistics': agency_stats.to_dict('records'),
            'supplier_concentration': sorted(agency_supplier_concentration, 
                                            key=lambda x: x['top_3_share'], reverse=True),
            'multi_agency_suppliers': multi_agency_findings,
            'summary': {
                'total_agencies': contracts['agency'].nunique(),
                'total_suppliers': contracts['supplier'].nunique(),
                'agencies_with_high_concentration': len(agency_supplier_concentration),
                'suppliers_with_multiple_agencies': len(multi_agency)
            }
        }
    
    def analyze_tax_delinquent_overlaps(self) -> Dict[str, Any]:
        """
        Analyze overlaps between businesses/contracts and tax-delinquent properties.
        
        Returns:
            Dictionary with tax delinquency overlap analysis
        """
        # Already covered address overlaps in analyze_address_clustering
        # Here we focus on owner/business name matches and financial patterns
        
        try:
            from Levenshtein import ratio
        except ImportError:
            return {'error': 'python-Levenshtein not installed'}
        
        # High-value tax delinquencies
        high_value_delinquent = self.taxes[self.taxes['total_due'] >= 5000].copy()
        high_value_delinquent = high_value_delinquent.sort_values('total_due', ascending=False)
        
        # Long-term delinquencies
        long_term = self.taxes[self.taxes['years_delinquent'] >= 3].copy()
        long_term = long_term.sort_values('years_delinquent', ascending=False)
        
        # Cross-reference high-value delinquent owners with business names
        matches_with_businesses = []
        for _, tax_row in high_value_delinquent.head(100).iterrows():
            owner = tax_row['owner_normalized']
            if not owner or len(owner) < 3:
                continue
                
            for _, lic_row in self.licenses.iterrows():
                business = lic_row['business_name_normalized']
                if not business or len(business) < 3:
                    continue
                    
                similarity = ratio(owner, business)
                if similarity >= 0.80:
                    matches_with_businesses.append({
                        'tax_owner': tax_row['owner_name_1'],
                        'business_name': lic_row['business_name'],
                        'similarity': round(similarity, 3),
                        'tax_address': tax_row['address'],
                        'business_address': lic_row['address'],
                        'total_due': tax_row['total_due'],
                        'years_delinquent': tax_row['years_delinquent'],
                        'pattern_type': 'HIGH_VALUE_TAX_BUSINESS_MATCH',
                        'why_it_matters': f"Tax-delinquent property owner ({similarity*100:.1f}% name match) "
                                        f"appears to operate business. ${tax_row['total_due']:,.2f} owed "
                                        f"for {tax_row['years_delinquent']} years. Could indicate: "
                                        f"financial distress, asset shielding, or enforcement priority."
                    })
        
        # Contract suppliers with tax delinquencies
        supplier_tax_matches = []
        for supplier in self.contracts['supplier_normalized'].dropna().unique():
            if not supplier or len(supplier) < 3:
                continue
            for _, tax_row in self.taxes.iterrows():
                owner = tax_row['owner_normalized']
                if not owner or len(owner) < 3:
                    continue
                similarity = ratio(supplier, owner)
                if similarity >= 0.85:
                    supplier_contracts = self.contracts[
                        self.contracts['supplier_normalized'] == supplier
                    ]
                    supplier_tax_matches.append({
                        'supplier': supplier,
                        'tax_owner': tax_row['owner_name_1'],
                        'similarity': round(similarity, 3),
                        'contract_count': len(supplier_contracts),
                        'contract_value': supplier_contracts['contract_value_numeric'].sum(),
                        'total_tax_due': tax_row['total_due'],
                        'years_delinquent': tax_row['years_delinquent'],
                        'pattern_type': 'SUPPLIER_TAX_DELINQUENT',
                        'why_it_matters': f"City contractor appears tax-delinquent. {len(supplier_contracts)} "
                                        f"contracts worth ${supplier_contracts['contract_value_numeric'].sum():,.2f} "
                                        f"while owing ${tax_row['total_due']:,.2f} in property taxes. "
                                        f"Could indicate: financial instability or enforcement gap."
                    })
        
        # Sort by risk
        matches_with_businesses.sort(key=lambda x: x['total_due'], reverse=True)
        supplier_tax_matches.sort(key=lambda x: x['contract_value'], reverse=True)
        
        return {
            'high_value_delinquencies': high_value_delinquent[
                ['owner_name_1', 'address', 'total_due', 'years_delinquent']
            ].head(20).to_dict('records'),
            'long_term_delinquencies': long_term[
                ['owner_name_1', 'address', 'total_due', 'years_delinquent']
            ].head(20).to_dict('records'),
            'business_owner_matches': matches_with_businesses[:30],
            'supplier_tax_matches': supplier_tax_matches[:30],
            'summary': {
                'total_delinquent_properties': len(self.taxes),
                'total_tax_due': self.taxes['total_due'].sum(),
                'high_value_count': len(high_value_delinquent),
                'long_term_count': len(long_term),
                'business_matches_found': len(matches_with_businesses),
                'supplier_matches_found': len(supplier_tax_matches)
            }
        }
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive analysis across all datasets.
        
        Returns:
            Dictionary with all analysis results and recommendations
        """
        print("Running cross-dataset analysis...")
        
        print("  - Analyzing address clustering...")
        address_analysis = self.analyze_address_clustering()
        
        print("  - Analyzing name similarity...")
        name_analysis = self.analyze_name_similarity()
        
        print("  - Analyzing contract timing...")
        timing_analysis = self.analyze_contract_timing()
        
        print("  - Analyzing procurement types...")
        procurement_analysis = self.analyze_procurement_types()
        
        print("  - Analyzing agency concentration...")
        agency_analysis = self.analyze_agency_concentration()
        
        print("  - Analyzing tax delinquent overlaps...")
        tax_analysis = self.analyze_tax_delinquent_overlaps()
        
        # Compile key findings
        key_findings = []
        
        # Address clustering findings
        if address_analysis['total_shared_addresses'] > 0:
            key_findings.append({
                'category': 'Address Clustering',
                'finding': f"{address_analysis['total_shared_addresses']} addresses appear in both "
                          f"business licenses and delinquent tax records",
                'significance': 'HIGH',
                'action': 'Review properties for potential undisclosed business use or financial distress'
            })
        
        # Name similarity findings
        if name_analysis.get('summary', {}).get('license_contract_matches_found', 0) > 0:
            key_findings.append({
                'category': 'Name Similarity',
                'finding': f"{name_analysis['summary']['license_contract_matches_found']} matches between "
                          f"business license holders and city contract suppliers",
                'significance': 'MEDIUM',
                'action': 'Verify business relationships and potential self-dealing'
            })
        
        # Contract timing findings
        if timing_analysis.get('summary', {}).get('months_with_spikes', 0) > 0:
            key_findings.append({
                'category': 'Contract Timing',
                'finding': f"{timing_analysis['summary']['months_with_spikes']} months with unusual "
                          f"contract activity spikes",
                'significance': 'MEDIUM',
                'action': 'Review end-of-period spending and batch processing patterns'
            })
        
        # Procurement findings
        if procurement_analysis.get('summary', {}).get('non_competitive_percentage', 0) > 20:
            key_findings.append({
                'category': 'Procurement Types',
                'finding': f"{procurement_analysis['summary']['non_competitive_percentage']}% of contracts "
                          f"awarded through non-competitive processes",
                'significance': 'HIGH',
                'action': 'Evaluate necessity of non-competitive awards and supplier diversity'
            })
        
        # Agency concentration findings
        if agency_analysis.get('summary', {}).get('agencies_with_high_concentration', 0) > 0:
            key_findings.append({
                'category': 'Agency Concentration',
                'finding': f"{agency_analysis['summary']['agencies_with_high_concentration']} agencies "
                          f"have high supplier concentration (top 3 suppliers >50% of value)",
                'significance': 'MEDIUM',
                'action': 'Review competition levels and consider supplier diversification'
            })
        
        # Tax delinquency findings
        if tax_analysis.get('summary', {}).get('supplier_matches_found', 0) > 0:
            key_findings.append({
                'category': 'Tax Delinquency Overlaps',
                'finding': f"{tax_analysis['summary']['supplier_matches_found']} city contractors may have "
                          f"tax-delinquent property ownership connections",
                'significance': 'HIGH',
                'action': 'Review contractor eligibility and enforce tax compliance requirements'
            })
        
        # Recommendations for follow-up data
        follow_up_recommendations = [
            {
                'data_source': 'Corporate registration records',
                'purpose': 'Verify ownership networks and shell company relationships',
                'priority': 'HIGH'
            },
            {
                'data_source': 'Bid documents and evaluation records',
                'purpose': 'Validate competitive process integrity for flagged contracts',
                'priority': 'HIGH'
            },
            {
                'data_source': 'Property ownership transfer history',
                'purpose': 'Track asset movement among related entities',
                'priority': 'MEDIUM'
            },
            {
                'data_source': 'Campaign contribution records',
                'purpose': 'Identify potential pay-to-play relationships',
                'priority': 'MEDIUM'
            },
            {
                'data_source': 'Subcontractor payment records',
                'purpose': 'Trace money flows through prime contractors',
                'priority': 'MEDIUM'
            },
            {
                'data_source': 'Building permit records',
                'purpose': 'Verify legitimate business operations at flagged addresses',
                'priority': 'LOW'
            },
            {
                'data_source': 'Utility service records',
                'purpose': 'Confirm actual occupancy at business addresses',
                'priority': 'LOW'
            }
        ]
        
        return {
            'generated_at': datetime.now().isoformat(),
            'dataset_summary': {
                'business_licenses': {
                    'total_records': len(self.licenses),
                    'unique_businesses': self.licenses['business_name'].nunique(),
                    'unique_addresses': self.licenses['address'].nunique()
                },
                'city_contracts': {
                    'total_records': len(self.contracts),
                    'total_value': self.contracts['contract_value_numeric'].sum(),
                    'unique_suppliers': self.contracts['supplier'].nunique(),
                    'unique_agencies': self.contracts['agency'].nunique()
                },
                'delinquent_taxes': {
                    'total_records': len(self.taxes),
                    'total_due': self.taxes['total_due'].sum(),
                    'unique_owners': self.taxes['owner_name_1'].nunique()
                }
            },
            'analyses': {
                'address_clustering': address_analysis,
                'name_similarity': name_analysis,
                'contract_timing': timing_analysis,
                'procurement_types': procurement_analysis,
                'agency_concentration': agency_analysis,
                'tax_delinquent_overlaps': tax_analysis
            },
            'key_findings': key_findings,
            'follow_up_recommendations': follow_up_recommendations
        }


def format_report(results: Dict[str, Any]) -> str:
    """Format comprehensive results as readable text report."""
    lines = []
    
    lines.append("=" * 80)
    lines.append("CROSS-DATASET PATTERN ANALYSIS REPORT")
    lines.append(f"Generated: {results['generated_at']}")
    lines.append("=" * 80)
    
    # Dataset Summary
    lines.append("\n" + "=" * 80)
    lines.append("DATASET OVERVIEW")
    lines.append("=" * 80)
    
    ds = results['dataset_summary']
    lines.append(f"\nBusiness Licenses:")
    lines.append(f"  Total Records: {ds['business_licenses']['total_records']:,}")
    lines.append(f"  Unique Businesses: {ds['business_licenses']['unique_businesses']:,}")
    lines.append(f"  Unique Addresses: {ds['business_licenses']['unique_addresses']:,}")
    
    lines.append(f"\nCity Contracts:")
    lines.append(f"  Total Records: {ds['city_contracts']['total_records']:,}")
    lines.append(f"  Total Value: ${ds['city_contracts']['total_value']:,.2f}")
    lines.append(f"  Unique Suppliers: {ds['city_contracts']['unique_suppliers']:,}")
    lines.append(f"  Unique Agencies: {ds['city_contracts']['unique_agencies']:,}")
    
    lines.append(f"\nDelinquent Property Taxes:")
    lines.append(f"  Total Records: {ds['delinquent_taxes']['total_records']:,}")
    lines.append(f"  Total Due: ${ds['delinquent_taxes']['total_due']:,.2f}")
    lines.append(f"  Unique Owners: {ds['delinquent_taxes']['unique_owners']:,}")
    
    # Key Findings
    lines.append("\n" + "=" * 80)
    lines.append("KEY FINDINGS")
    lines.append("=" * 80)
    
    for i, finding in enumerate(results['key_findings'], 1):
        lines.append(f"\n{i}. [{finding['significance']}] {finding['category']}")
        lines.append(f"   Finding: {finding['finding']}")
        lines.append(f"   Action: {finding['action']}")
    
    # Address Clustering Details
    lines.append("\n" + "=" * 80)
    lines.append("ADDRESS CLUSTERING ANALYSIS")
    lines.append("=" * 80)
    
    addr = results['analyses']['address_clustering']
    lines.append(f"\nCross-Dataset Overlaps: {addr['total_shared_addresses']} addresses found in both licenses and tax records")
    
    if addr['cross_dataset_overlaps']:
        lines.append("\nTop Address Overlaps (License + Tax Delinquent):")
        for item in addr['cross_dataset_overlaps'][:10]:
            lines.append(f"  - {item['address']}")
            lines.append(f"    Licenses: {item['license_count']}, Tax Records: {item['tax_delinquent_count']}")
            lines.append(f"    Tax Due: ${item['total_tax_due']:,.2f}")
    
    if addr['address_density']:
        lines.append("\nHigh-Density Business Addresses:")
        for item in addr['address_density'][:10]:
            lines.append(f"  - {item['address']}: {item['license_count']} licenses")
            if item['businesses']:
                lines.append(f"    Businesses: {', '.join(item['businesses'][:3])}")
    
    # Name Similarity Details
    lines.append("\n" + "=" * 80)
    lines.append("NAME SIMILARITY ANALYSIS")
    lines.append("=" * 80)
    
    names = results['analyses']['name_similarity']
    if 'summary' in names:
        lines.append(f"\nLicense-Contract Matches: {names['summary']['license_contract_matches_found']}")
        lines.append(f"License-Tax Owner Matches: {names['summary']['license_tax_matches_found']}")
    
    if names.get('license_contract_matches'):
        lines.append("\nTop License-Contract Supplier Matches:")
        for item in names['license_contract_matches'][:10]:
            lines.append(f"  - {item['license_name']} <-> {item['contract_supplier']}")
            lines.append(f"    Similarity: {item['similarity_score']*100:.1f}%, "
                        f"Contracts: {item['contract_count']}, Value: ${item['total_contract_value']:,.2f}")
    
    # Contract Timing Details
    lines.append("\n" + "=" * 80)
    lines.append("CONTRACT TIMING ANALYSIS")
    lines.append("=" * 80)
    
    timing = results['analyses']['contract_timing']
    if timing.get('temporal_spikes'):
        lines.append("\nMonths with Unusual Activity:")
        for item in timing['temporal_spikes'][:5]:
            lines.append(f"  - {item['month']}: {item['contract_count']} contracts, "
                        f"${item['total_value']:,.2f}")
    
    if timing.get('same_day_awards'):
        lines.append(f"\nSame-Day Contract Awards: {len(timing['same_day_awards'])} days with 3+ awards")
    
    # Procurement Type Details
    lines.append("\n" + "=" * 80)
    lines.append("PROCUREMENT TYPE ANALYSIS")
    lines.append("=" * 80)
    
    proc = results['analyses']['procurement_types']
    if proc.get('procurement_distribution'):
        lines.append("\nProcurement Type Distribution:")
        for item in proc['procurement_distribution'][:8]:
            lines.append(f"  - {item['procurement_type']}: {item['count']} contracts, "
                        f"${item['total_value']:,.2f}")
    
    if proc.get('non_competitive_suppliers'):
        lines.append("\nTop Non-Competitive Award Recipients:")
        for item in proc['non_competitive_suppliers'][:5]:
            lines.append(f"  - {item['supplier']}: {item['contract_count']} contracts, "
                        f"${item['total_value']:,.2f}")
    
    # Agency Concentration Details
    lines.append("\n" + "=" * 80)
    lines.append("AGENCY CONCENTRATION ANALYSIS")
    lines.append("=" * 80)
    
    agency = results['analyses']['agency_concentration']
    if agency.get('supplier_concentration'):
        lines.append("\nAgencies with High Supplier Concentration:")
        for item in agency['supplier_concentration'][:5]:
            lines.append(f"  - {item['agency']}")
            lines.append(f"    Top 3 suppliers control {item['top_3_share']*100:.1f}% "
                        f"(${item['top_3_value']:,.2f})")
    
    if agency.get('multi_agency_suppliers'):
        lines.append("\nSuppliers Working with Multiple Agencies:")
        for item in agency['multi_agency_suppliers'][:5]:
            lines.append(f"  - {item['supplier']}: {item['agency_count']} agencies, "
                        f"${item['total_value']:,.2f}")
    
    # Tax Delinquent Overlaps
    lines.append("\n" + "=" * 80)
    lines.append("TAX DELINQUENT OVERLAPS")
    lines.append("=" * 80)
    
    tax = results['analyses']['tax_delinquent_overlaps']
    if 'summary' in tax:
        lines.append(f"\nTotal Delinquent Properties: {tax['summary']['total_delinquent_properties']:,}")
        lines.append(f"Total Tax Due: ${tax['summary']['total_tax_due']:,.2f}")
    
    if tax.get('supplier_tax_matches'):
        lines.append("\nCity Contractors with Potential Tax Delinquency:")
        for item in tax['supplier_tax_matches'][:5]:
            lines.append(f"  - {item['supplier']}")
            lines.append(f"    Contracts: {item['contract_count']}, Value: ${item['contract_value']:,.2f}")
            lines.append(f"    Tax Due: ${item['total_tax_due']:,.2f}")
    
    # Follow-up Recommendations
    lines.append("\n" + "=" * 80)
    lines.append("FOLLOW-UP DATA RECOMMENDATIONS")
    lines.append("=" * 80)
    lines.append("\nTo validate findings, consider obtaining:")
    
    for rec in results['follow_up_recommendations']:
        lines.append(f"\n[{rec['priority']}] {rec['data_source']}")
        lines.append(f"  Purpose: {rec['purpose']}")
    
    lines.append("\n" + "=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)
    
    return "\n".join(lines)
