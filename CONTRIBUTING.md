# Contributing to License Ledger Patterns

Thank you for your interest in contributing to License Ledger Patterns! This guide will help you get started.

## Philosophy

This project is built on three core principles:

1. **Neutrality**: We surface patterns, not accusations. All findings are presented as signals requiring validation.
2. **Transparency**: Methodologies are documented and explainable to non-technical users.
3. **Utility**: Output is designed for journalists and auditors who need actionable insights.

## Getting Started

### Development Setup

```bash
# Clone the repository
git clone https://github.com/closespark/license-ledger-patterns.git
cd license-ledger-patterns

# Install dependencies
pip install -r requirements.txt

# Test with sample data
python cli.py sample_data.csv
```

### Running Tests

```bash
# Test CLI
python cli.py sample_data.csv --output test.txt

# Test programmatic usage
python example.py
```

## Types of Contributions

### 1. New Pattern Detectors

Add new analysis methods to `analyzer.py`:

- Follow the existing pattern of returning DataFrames or lists
- Include risk scores (0-1 normalized)
- Add "why_it_matters" explanations
- Document methodology

Example:
```python
def analyze_new_pattern(self, threshold: int = 5) -> pd.DataFrame:
    """
    Brief description of what this detects.
    
    Args:
        threshold: Explanation of threshold
        
    Returns:
        DataFrame with findings
    """
    # Analysis logic
    # ...
    
    # Add risk scores and explanations
    results['risk_score'] = ...
    results['why_it_matters'] = ...
    
    return results
```

### 2. Output Formats

Extend `reporter.py` to add new output formats:

- CSV export
- Excel with charts
- HTML reports
- Visualizations

### 3. Data Integrations

Help load data from common sources:

- OpenData portals
- API integrations
- Database connectors

### 4. Documentation

Improve documentation:

- Use case examples
- Methodology explanations
- Tutorial content
- Translation

## Code Style

### Python

- Follow PEP 8
- Use type hints where helpful
- Document all public functions
- Keep functions focused and testable

### Documentation

- Use clear, neutral language
- Avoid jargon where possible
- Include examples
- Explain "why" not just "what"

## Pull Request Process

1. **Fork and Branch**: Create a feature branch from `main`
2. **Test**: Ensure your changes work with sample data
3. **Document**: Update README and docstrings
4. **Commit**: Use clear, descriptive commit messages
5. **PR**: Submit with description of changes and rationale

### Commit Message Format

```
Add feature: Brief description

Longer explanation of what changed and why.
Include use cases and examples if relevant.
```

## Adding New Pattern Types

When adding a new pattern detector:

1. Add the analysis method to `LicenseAnalyzer`
2. Add a reporting method to `Reporter`
3. Integrate into CLI and summary report
4. Update README with new capability
5. Add example to sample data if needed

## Testing Checklist

Before submitting:

- [ ] Code runs without errors on sample data
- [ ] New features have docstrings
- [ ] README updated if needed
- [ ] Output is neutral and explainable
- [ ] Risk scores are normalized 0-1
- [ ] "Why it matters" context included

## Questions?

Open an issue for:
- Feature requests
- Bug reports
- Methodology questions
- Documentation improvements

## Code of Conduct

### Our Standards

- **Professional**: Maintain high-quality, well-documented code
- **Respectful**: Value diverse perspectives and use cases
- **Constructive**: Focus on improvement and learning
- **Ethical**: Never promote surveillance or discrimination

### Not Acceptable

- Accusatory or inflammatory language
- Privacy-violating features
- Discriminatory algorithms or analysis
- Misleading or deceptive output

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in:
- Git commit history
- Release notes
- Project documentation

Thank you for helping make municipal data more accessible and analyzable!
