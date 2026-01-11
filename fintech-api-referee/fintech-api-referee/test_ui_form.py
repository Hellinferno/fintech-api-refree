"""
Unit tests for UI form completeness.

Task 3.1: Write unit tests for UI form completeness
- Test that all required form options are present and correctly labeled
- Test input validation and error handling
Requirements: 1.2, 1.3, 1.4, 1.5
"""

import pytest
from models import BudgetTier, DataType, FrequencyTier, UseCase
from app import validate_constraints, validate_data_types, normalize_constraints


class TestFormOptionsCompleteness:
    """
    Unit tests verifying all required form options are present and correctly labeled.
    
    Requirements: 1.2, 1.3, 1.4, 1.5
    """

    def test_budget_options_present(self):
        """
        Test that all required budget options are present.
        
        Requirement 1.2: THE API_Referee SHALL collect budget constraints with
        options for "Free", "Under $50/month", "Under $200/month", and "Enterprise"
        """
        expected_options = ["Free", "Under $50/month", "Under $200/month", "Enterprise"]
        actual_options = [tier.value for tier in BudgetTier]
        
        for expected in expected_options:
            assert expected in actual_options, (
                f"Budget option '{expected}' not found. Available: {actual_options}"
            )

    def test_budget_options_count(self):
        """Test that exactly 4 budget options exist as per requirements."""
        assert len(BudgetTier) == 4, (
            f"Expected 4 budget options, found {len(BudgetTier)}"
        )

    def test_data_type_options_present(self):
        """
        Test that all required data type options are present.
        
        Requirement 1.3: THE API_Referee SHALL collect data type preferences
        including "Stocks", "Crypto", "Forex", "Options", and "Commodities"
        """
        expected_options = ["Stocks", "Crypto", "Forex", "Options", "Commodities"]
        actual_options = [dt.value for dt in DataType]
        
        for expected in expected_options:
            assert expected in actual_options, (
                f"Data type option '{expected}' not found. Available: {actual_options}"
            )

    def test_data_type_options_count(self):
        """Test that exactly 5 data type options exist as per requirements."""
        assert len(DataType) == 5, (
            f"Expected 5 data type options, found {len(DataType)}"
        )

    def test_frequency_options_present(self):
        """
        Test that all required frequency options are present.
        
        Requirement 1.4: THE API_Referee SHALL collect frequency requirements
        with options for "Real-time", "Delayed (15-20 min)", "End-of-day",
        and "Historical only"
        """
        expected_options = ["Real-time", "Delayed (15-20 min)", "End-of-day", "Historical only"]
        actual_options = [freq.value for freq in FrequencyTier]
        
        for expected in expected_options:
            assert expected in actual_options, (
                f"Frequency option '{expected}' not found. Available: {actual_options}"
            )

    def test_frequency_options_count(self):
        """Test that exactly 4 frequency options exist as per requirements."""
        assert len(FrequencyTier) == 4, (
            f"Expected 4 frequency options, found {len(FrequencyTier)}"
        )

    def test_use_case_options_present(self):
        """
        Test that all required use case options are present.
        
        Requirement 1.5: THE API_Referee SHALL collect use case information
        including "Research/Analysis", "Trading Bot", "Portfolio Tracking",
        and "Educational"
        """
        expected_options = ["Research/Analysis", "Trading Bot", "Portfolio Tracking", "Educational"]
        actual_options = [uc.value for uc in UseCase]
        
        for expected in expected_options:
            assert expected in actual_options, (
                f"Use case option '{expected}' not found. Available: {actual_options}"
            )

    def test_use_case_options_count(self):
        """Test that exactly 4 use case options exist as per requirements."""
        assert len(UseCase) == 4, (
            f"Expected 4 use case options, found {len(UseCase)}"
        )



class TestInputValidation:
    """
    Unit tests for input validation and error handling.
    
    Requirements: 1.2, 1.3, 1.4, 1.5
    """

    def test_validate_constraints_valid_input(self):
        """Test that valid constraints pass validation."""
        is_valid, error = validate_constraints(
            budget="Free",
            data_types=["Stocks"],
            frequency="Real-time",
            use_case="Research/Analysis"
        )
        assert is_valid is True
        assert error is None

    def test_validate_constraints_all_data_types(self):
        """Test validation with all data types selected."""
        is_valid, error = validate_constraints(
            budget="Enterprise",
            data_types=["Stocks", "Crypto", "Forex", "Options", "Commodities"],
            frequency="End-of-day",
            use_case="Trading Bot"
        )
        assert is_valid is True
        assert error is None

    def test_validate_constraints_invalid_budget(self):
        """Test that invalid budget value fails validation."""
        is_valid, error = validate_constraints(
            budget="Invalid Budget",
            data_types=["Stocks"],
            frequency="Real-time",
            use_case="Research/Analysis"
        )
        assert is_valid is False
        assert error is not None
        assert "Invalid budget" in error

    def test_validate_constraints_empty_data_types(self):
        """
        Test that empty data types list fails validation.
        
        Requirement 1.3: Users must select at least one data type.
        """
        is_valid, error = validate_constraints(
            budget="Free",
            data_types=[],
            frequency="Real-time",
            use_case="Research/Analysis"
        )
        assert is_valid is False
        assert error is not None
        assert "data type" in error.lower()

    def test_validate_constraints_invalid_data_type(self):
        """Test that invalid data type value fails validation."""
        is_valid, error = validate_constraints(
            budget="Free",
            data_types=["Invalid Type"],
            frequency="Real-time",
            use_case="Research/Analysis"
        )
        assert is_valid is False
        assert error is not None
        assert "Invalid data type" in error

    def test_validate_constraints_invalid_frequency(self):
        """Test that invalid frequency value fails validation."""
        is_valid, error = validate_constraints(
            budget="Free",
            data_types=["Stocks"],
            frequency="Invalid Frequency",
            use_case="Research/Analysis"
        )
        assert is_valid is False
        assert error is not None
        assert "Invalid frequency" in error

    def test_validate_constraints_invalid_use_case(self):
        """Test that invalid use case value fails validation."""
        is_valid, error = validate_constraints(
            budget="Free",
            data_types=["Stocks"],
            frequency="Real-time",
            use_case="Invalid Use Case"
        )
        assert is_valid is False
        assert error is not None
        assert "Invalid use case" in error

    def test_validate_data_types_empty_list(self):
        """Test validate_data_types with empty list."""
        is_valid, error = validate_data_types([])
        assert is_valid is False
        assert error is not None
        assert "select at least one" in error.lower()

    def test_validate_data_types_valid_list(self):
        """Test validate_data_types with valid list."""
        is_valid, error = validate_data_types(["Stocks", "Crypto"])
        assert is_valid is True
        assert error is None


class TestConstraintNormalization:
    """
    Unit tests for constraint normalization.
    
    Requirements: 1.2, 1.3, 1.4, 1.5
    """

    def test_normalize_constraints_creates_user_constraints(self):
        """Test that normalize_constraints creates a valid UserConstraints object."""
        constraints = normalize_constraints(
            budget="Free",
            data_types=["Stocks"],
            frequency="Real-time",
            use_case="Research/Analysis"
        )
        
        assert constraints is not None
        assert constraints.budget == BudgetTier.FREE
        assert DataType.STOCKS in constraints.data_types
        assert constraints.frequency == FrequencyTier.REALTIME
        assert constraints.use_case == UseCase.RESEARCH

    def test_normalize_constraints_multiple_data_types(self):
        """Test normalization with multiple data types."""
        constraints = normalize_constraints(
            budget="Under $50/month",
            data_types=["Stocks", "Crypto", "Forex"],
            frequency="Delayed (15-20 min)",
            use_case="Portfolio Tracking"
        )
        
        assert len(constraints.data_types) == 3
        assert DataType.STOCKS in constraints.data_types
        assert DataType.CRYPTO in constraints.data_types
        assert DataType.FOREX in constraints.data_types

    def test_normalize_constraints_all_budget_tiers(self):
        """Test normalization works for all budget tiers."""
        budget_mappings = [
            ("Free", BudgetTier.FREE),
            ("Under $50/month", BudgetTier.UNDER_50),
            ("Under $200/month", BudgetTier.UNDER_200),
            ("Enterprise", BudgetTier.ENTERPRISE),
        ]
        
        for budget_str, expected_tier in budget_mappings:
            constraints = normalize_constraints(
                budget=budget_str,
                data_types=["Stocks"],
                frequency="Real-time",
                use_case="Research/Analysis"
            )
            assert constraints.budget == expected_tier, (
                f"Budget '{budget_str}' should map to {expected_tier}"
            )

    def test_normalize_constraints_all_frequency_tiers(self):
        """Test normalization works for all frequency tiers."""
        frequency_mappings = [
            ("Real-time", FrequencyTier.REALTIME),
            ("Delayed (15-20 min)", FrequencyTier.DELAYED),
            ("End-of-day", FrequencyTier.EOD),
            ("Historical only", FrequencyTier.HISTORICAL),
        ]
        
        for freq_str, expected_tier in frequency_mappings:
            constraints = normalize_constraints(
                budget="Free",
                data_types=["Stocks"],
                frequency=freq_str,
                use_case="Research/Analysis"
            )
            assert constraints.frequency == expected_tier, (
                f"Frequency '{freq_str}' should map to {expected_tier}"
            )

    def test_normalize_constraints_all_use_cases(self):
        """Test normalization works for all use cases."""
        use_case_mappings = [
            ("Research/Analysis", UseCase.RESEARCH),
            ("Trading Bot", UseCase.TRADING_BOT),
            ("Portfolio Tracking", UseCase.PORTFOLIO),
            ("Educational", UseCase.EDUCATIONAL),
        ]
        
        for uc_str, expected_uc in use_case_mappings:
            constraints = normalize_constraints(
                budget="Free",
                data_types=["Stocks"],
                frequency="Real-time",
                use_case=uc_str
            )
            assert constraints.use_case == expected_uc, (
                f"Use case '{uc_str}' should map to {expected_uc}"
            )
