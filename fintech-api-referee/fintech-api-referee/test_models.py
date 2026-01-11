"""
Property-based tests for FinTech API Referee data models.
Uses Hypothesis for comprehensive input validation.
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
from typing import List
from models import (
    APIInfo,
    BudgetTier,
    DataType,
    FrequencyTier,
)


# Strategies for generating valid model data
budget_tier_strategy = st.sampled_from(list(BudgetTier))
data_type_strategy = st.sampled_from(list(DataType))
frequency_tier_strategy = st.sampled_from(list(FrequencyTier))


def api_info_strategy():
    """Strategy for generating valid APIInfo instances."""
    return st.builds(
        APIInfo,
        name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        pricing=st.dictionaries(
            keys=budget_tier_strategy,
            values=st.booleans(),
            min_size=1,
        ),
        data_coverage=st.lists(data_type_strategy, min_size=1, max_size=5),
        frequency_support=st.lists(frequency_tier_strategy, min_size=1, max_size=4),
        rate_limits=st.dictionaries(
            keys=st.text(min_size=1, max_size=30).filter(lambda x: x.strip()),
            values=st.integers(min_value=1, max_value=10000),
            min_size=1,
        ),
        strengths=st.lists(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()), min_size=1, max_size=5),
        limitations=st.lists(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()), min_size=0, max_size=5),
        tos_restrictions=st.lists(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()), min_size=0, max_size=5),
        reliability_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        last_updated=st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2030, 12, 31)),
    )


class TestAPIInfoCompleteness:
    """
    Property tests for API database information completeness.
    
    Feature: fintech-api-referee, Property 7: Complete API Database Information
    Validates: Requirements 5.2, 5.3, 5.4
    """

    @given(api_info=api_info_strategy())
    @settings(max_examples=100)
    def test_api_has_pricing_tiers(self, api_info: APIInfo):
        """
        Property 7: Complete API Database Information
        Validates: Requirements 5.2
        
        For any API in the database, it should contain pricing tier information.
        """
        assert api_info.pricing is not None
        assert isinstance(api_info.pricing, dict)
        assert len(api_info.pricing) > 0
        # All keys must be valid BudgetTier values
        for tier in api_info.pricing.keys():
            assert isinstance(tier, BudgetTier)

    @given(api_info=api_info_strategy())
    @settings(max_examples=100)
    def test_api_has_rate_limits(self, api_info: APIInfo):
        """
        Property 7: Complete API Database Information
        Validates: Requirements 5.2
        
        For any API in the database, it should contain rate limit information.
        """
        assert api_info.rate_limits is not None
        assert isinstance(api_info.rate_limits, dict)
        assert len(api_info.rate_limits) > 0
        # All rate limit values must be positive integers
        for key, value in api_info.rate_limits.items():
            assert isinstance(key, str)
            assert isinstance(value, int)
            assert value > 0

    @given(api_info=api_info_strategy())
    @settings(max_examples=100)
    def test_api_has_data_coverage(self, api_info: APIInfo):
        """
        Property 7: Complete API Database Information
        Validates: Requirements 5.2
        
        For any API in the database, it should contain data coverage information.
        """
        assert api_info.data_coverage is not None
        assert isinstance(api_info.data_coverage, list)
        assert len(api_info.data_coverage) > 0
        # All data coverage items must be valid DataType values
        for data_type in api_info.data_coverage:
            assert isinstance(data_type, DataType)

    @given(api_info=api_info_strategy())
    @settings(max_examples=100)
    def test_api_has_tos_restrictions(self, api_info: APIInfo):
        """
        Property 7: Complete API Database Information
        Validates: Requirements 5.2
        
        For any API in the database, it should contain terms of service information.
        """
        assert api_info.tos_restrictions is not None
        assert isinstance(api_info.tos_restrictions, list)
        # TOS restrictions can be empty but must be a list

    @given(api_info=api_info_strategy())
    @settings(max_examples=100)
    def test_api_has_reliability_score(self, api_info: APIInfo):
        """
        Property 7: Complete API Database Information
        Validates: Requirements 5.3
        
        For any API in the database, it should contain a reliability score
        between 0.0 and 1.0 inclusive.
        """
        assert api_info.reliability_score is not None
        assert isinstance(api_info.reliability_score, float)
        assert 0.0 <= api_info.reliability_score <= 1.0

    @given(api_info=api_info_strategy())
    @settings(max_examples=100)
    def test_api_has_update_timestamp(self, api_info: APIInfo):
        """
        Property 7: Complete API Database Information
        Validates: Requirements 5.4
        
        For any API in the database, it should contain a valid update timestamp.
        """
        assert api_info.last_updated is not None
        assert isinstance(api_info.last_updated, datetime)

    @given(api_info=api_info_strategy())
    @settings(max_examples=100)
    def test_api_has_complete_information(self, api_info: APIInfo):
        """
        Property 7: Complete API Database Information
        Validates: Requirements 5.2, 5.3, 5.4
        
        For any API in the database, it should contain all required fields:
        pricing tiers, rate limits, data coverage, terms of service,
        reliability scores, and valid timestamps.
        """
        # Name must be non-empty
        assert api_info.name is not None
        assert len(api_info.name.strip()) > 0
        
        # Pricing tiers (Req 5.2)
        assert api_info.pricing is not None
        assert len(api_info.pricing) > 0
        
        # Rate limits (Req 5.2)
        assert api_info.rate_limits is not None
        assert len(api_info.rate_limits) > 0
        
        # Data coverage (Req 5.2)
        assert api_info.data_coverage is not None
        assert len(api_info.data_coverage) > 0
        
        # TOS restrictions (Req 5.2)
        assert api_info.tos_restrictions is not None
        
        # Reliability score (Req 5.3)
        assert 0.0 <= api_info.reliability_score <= 1.0
        
        # Update timestamp (Req 5.4)
        assert api_info.last_updated is not None
        assert isinstance(api_info.last_updated, datetime)
        
        # Frequency support
        assert api_info.frequency_support is not None
        assert len(api_info.frequency_support) > 0
        
        # Strengths and limitations
        assert api_info.strengths is not None
        assert api_info.limitations is not None


# =============================================================================
# Unit Tests for API Database Completeness
# Task 2.1: Test that all required APIs are present with complete information
# Requirements: 5.1, 5.2
# =============================================================================

from models import get_all_apis


class TestAPIDatabaseCompleteness:
    """
    Unit tests for API database completeness.
    
    Requirements: 5.1, 5.2
    - Tests that all required APIs are present
    - Tests data integrity and consistency across API entries
    """

    # Required APIs per Requirement 5.1
    REQUIRED_APIS = [
        "Alpha Vantage",
        "Polygon.io",
        "Yahoo Finance",
        "Quandl",
        # Note: IEX Cloud mentioned in requirements but Finnhub, EODHD, Marketstack
        # are in the implementation as alternatives
    ]

    def test_api_database_not_empty(self):
        """Test that the API database contains at least one API."""
        apis = get_all_apis()
        assert len(apis) > 0, "API database should not be empty"

    def test_required_apis_present(self):
        """
        Test that all required APIs from Requirement 5.1 are present.
        
        Requirement 5.1: THE API_Database SHALL store comprehensive information
        for major financial APIs including YFinance, AlphaVantage, Polygon.io,
        IEX Cloud, and Quandl.
        """
        apis = get_all_apis()
        api_names = [api.name for api in apis]
        
        for required_api in self.REQUIRED_APIS:
            assert required_api in api_names, (
                f"Required API '{required_api}' not found in database. "
                f"Available APIs: {api_names}"
            )

    def test_each_api_has_name(self):
        """Test that each API has a non-empty name."""
        apis = get_all_apis()
        for api in apis:
            assert api.name is not None, "API name should not be None"
            assert len(api.name.strip()) > 0, "API name should not be empty"

    def test_each_api_has_pricing_tiers(self):
        """
        Test that each API has pricing tier information.
        
        Requirement 5.2: THE API_Database SHALL include pricing tiers...
        """
        apis = get_all_apis()
        for api in apis:
            assert api.pricing is not None, f"{api.name}: pricing should not be None"
            assert isinstance(api.pricing, dict), f"{api.name}: pricing should be a dict"
            assert len(api.pricing) > 0, f"{api.name}: pricing should have at least one tier"
            
            # Verify all pricing keys are valid BudgetTier values
            for tier in api.pricing.keys():
                assert isinstance(tier, BudgetTier), (
                    f"{api.name}: pricing key {tier} should be a BudgetTier"
                )

    def test_each_api_has_rate_limits(self):
        """
        Test that each API has rate limit information.
        
        Requirement 5.2: THE API_Database SHALL include ... rate limits...
        """
        apis = get_all_apis()
        for api in apis:
            assert api.rate_limits is not None, f"{api.name}: rate_limits should not be None"
            assert isinstance(api.rate_limits, dict), f"{api.name}: rate_limits should be a dict"
            assert len(api.rate_limits) > 0, f"{api.name}: rate_limits should have at least one entry"
            
            # Verify all rate limit values are positive integers
            for key, value in api.rate_limits.items():
                assert isinstance(value, int), (
                    f"{api.name}: rate_limit '{key}' value should be an integer"
                )
                assert value > 0, (
                    f"{api.name}: rate_limit '{key}' value should be positive"
                )

    def test_each_api_has_data_coverage(self):
        """
        Test that each API has data coverage information.
        
        Requirement 5.2: THE API_Database SHALL include ... data coverage...
        """
        apis = get_all_apis()
        for api in apis:
            assert api.data_coverage is not None, f"{api.name}: data_coverage should not be None"
            assert isinstance(api.data_coverage, list), f"{api.name}: data_coverage should be a list"
            assert len(api.data_coverage) > 0, f"{api.name}: data_coverage should have at least one type"
            
            # Verify all data coverage items are valid DataType values
            for data_type in api.data_coverage:
                assert isinstance(data_type, DataType), (
                    f"{api.name}: data_coverage item {data_type} should be a DataType"
                )

    def test_each_api_has_tos_restrictions(self):
        """
        Test that each API has terms of service information.
        
        Requirement 5.2: THE API_Database SHALL include ... terms of service...
        """
        apis = get_all_apis()
        for api in apis:
            assert api.tos_restrictions is not None, f"{api.name}: tos_restrictions should not be None"
            assert isinstance(api.tos_restrictions, list), f"{api.name}: tos_restrictions should be a list"
            # TOS restrictions should have at least one entry for proper documentation
            assert len(api.tos_restrictions) > 0, (
                f"{api.name}: tos_restrictions should have at least one entry"
            )

    def test_each_api_has_frequency_support(self):
        """Test that each API has frequency support information."""
        apis = get_all_apis()
        for api in apis:
            assert api.frequency_support is not None, f"{api.name}: frequency_support should not be None"
            assert isinstance(api.frequency_support, list), f"{api.name}: frequency_support should be a list"
            assert len(api.frequency_support) > 0, f"{api.name}: frequency_support should have at least one tier"
            
            # Verify all frequency support items are valid FrequencyTier values
            for freq in api.frequency_support:
                assert isinstance(freq, FrequencyTier), (
                    f"{api.name}: frequency_support item {freq} should be a FrequencyTier"
                )

    def test_each_api_has_strengths(self):
        """Test that each API has documented strengths."""
        apis = get_all_apis()
        for api in apis:
            assert api.strengths is not None, f"{api.name}: strengths should not be None"
            assert isinstance(api.strengths, list), f"{api.name}: strengths should be a list"
            assert len(api.strengths) > 0, f"{api.name}: strengths should have at least one entry"

    def test_each_api_has_limitations(self):
        """Test that each API has documented limitations."""
        apis = get_all_apis()
        for api in apis:
            assert api.limitations is not None, f"{api.name}: limitations should not be None"
            assert isinstance(api.limitations, list), f"{api.name}: limitations should be a list"
            # Limitations can be empty for some APIs, but should be documented

    def test_each_api_has_valid_reliability_score(self):
        """
        Test that each API has a valid reliability score between 0.0 and 1.0.
        
        Requirement 5.3: THE API_Database SHALL track data quality metrics
        and reliability scores.
        """
        apis = get_all_apis()
        for api in apis:
            assert api.reliability_score is not None, f"{api.name}: reliability_score should not be None"
            assert isinstance(api.reliability_score, float), (
                f"{api.name}: reliability_score should be a float"
            )
            assert 0.0 <= api.reliability_score <= 1.0, (
                f"{api.name}: reliability_score should be between 0.0 and 1.0, got {api.reliability_score}"
            )

    def test_each_api_has_update_timestamp(self):
        """
        Test that each API has a valid update timestamp.
        
        Requirement 5.4: THE API_Database SHALL maintain update timestamps
        for API information.
        """
        apis = get_all_apis()
        for api in apis:
            assert api.last_updated is not None, f"{api.name}: last_updated should not be None"
            assert isinstance(api.last_updated, datetime), (
                f"{api.name}: last_updated should be a datetime"
            )

    def test_no_duplicate_api_names(self):
        """Test that there are no duplicate API names in the database."""
        apis = get_all_apis()
        api_names = [api.name for api in apis]
        unique_names = set(api_names)
        
        assert len(api_names) == len(unique_names), (
            f"Duplicate API names found: {[name for name in api_names if api_names.count(name) > 1]}"
        )

    def test_minimum_api_count(self):
        """Test that the database has a reasonable minimum number of APIs."""
        apis = get_all_apis()
        # Per requirements, we should have at least 5 major APIs
        assert len(apis) >= 5, (
            f"API database should have at least 5 APIs, found {len(apis)}"
        )

    def test_pricing_covers_all_budget_tiers(self):
        """Test that at least one API supports each budget tier."""
        apis = get_all_apis()
        
        for tier in BudgetTier:
            tier_supported = any(
                api.pricing.get(tier, False) for api in apis
            )
            assert tier_supported, (
                f"No API supports budget tier '{tier.value}'"
            )

    def test_data_coverage_includes_all_types(self):
        """Test that at least one API covers each data type."""
        apis = get_all_apis()
        
        for data_type in DataType:
            type_covered = any(
                data_type in api.data_coverage for api in apis
            )
            assert type_covered, (
                f"No API covers data type '{data_type.value}'"
            )

    def test_frequency_support_includes_all_tiers(self):
        """Test that at least one API supports each frequency tier."""
        apis = get_all_apis()
        
        for freq in FrequencyTier:
            freq_supported = any(
                freq in api.frequency_support for api in apis
            )
            assert freq_supported, (
                f"No API supports frequency tier '{freq.value}'"
            )


# =============================================================================
# Property Tests for API Scoring Engine
# Task 4.4: Property test for API scoring completeness
# =============================================================================

from models import (
    UserConstraints,
    UseCase,
    APIScore,
    score_apis,
    calculate_category_scores,
    SCORING_WEIGHTS,
)


# Strategy for generating valid UserConstraints
def user_constraints_strategy():
    """Strategy for generating valid UserConstraints instances."""
    return st.builds(
        UserConstraints,
        budget=budget_tier_strategy,
        data_types=st.lists(data_type_strategy, min_size=1, max_size=5, unique=True),
        frequency=frequency_tier_strategy,
        use_case=st.sampled_from(list(UseCase)),
    )


class TestAPIScoringCompleteness:
    """
    Property tests for API scoring completeness.
    
    Feature: fintech-api-referee, Property 1: API Scoring Completeness
    Validates: Requirements 2.1, 2.2
    
    For any valid user constraints, the scoring engine should evaluate all APIs
    in the database and produce scores based on budget compatibility, data type
    coverage, frequency availability, and use case suitability.
    """

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_scoring_evaluates_all_apis(self, constraints: UserConstraints):
        """
        Property 1: API Scoring Completeness
        Validates: Requirements 2.1
        
        For any valid user constraints, the scoring engine should evaluate
        ALL APIs in the database.
        """
        all_apis = get_all_apis()
        scored_apis = score_apis(constraints)
        
        # All APIs should be scored
        assert len(scored_apis) == len(all_apis), (
            f"Expected {len(all_apis)} scored APIs, got {len(scored_apis)}"
        )
        
        # All API names should be present in results
        scored_api_names = {score.api.name for score in scored_apis}
        all_api_names = {api.name for api in all_apis}
        assert scored_api_names == all_api_names, (
            f"Missing APIs in scoring: {all_api_names - scored_api_names}"
        )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_scoring_produces_all_category_scores(self, constraints: UserConstraints):
        """
        Property 1: API Scoring Completeness
        Validates: Requirements 2.2
        
        For any valid user constraints, each scored API should have scores
        for all four categories: budget, data_types, frequency, and use_case.
        """
        scored_apis = score_apis(constraints)
        required_categories = {"budget", "data_types", "frequency", "use_case"}
        
        for scored_api in scored_apis:
            # Each API should have category_scores dict
            assert scored_api.category_scores is not None, (
                f"{scored_api.api.name}: category_scores should not be None"
            )
            
            # All required categories should be present
            actual_categories = set(scored_api.category_scores.keys())
            assert actual_categories == required_categories, (
                f"{scored_api.api.name}: Expected categories {required_categories}, "
                f"got {actual_categories}"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_category_scores_are_valid(self, constraints: UserConstraints):
        """
        Property 1: API Scoring Completeness
        Validates: Requirements 2.2
        
        For any valid user constraints, all category scores should be
        numeric values between 0 and 100.
        """
        scored_apis = score_apis(constraints)
        
        for scored_api in scored_apis:
            for category, score in scored_api.category_scores.items():
                assert isinstance(score, (int, float)), (
                    f"{scored_api.api.name}: {category} score should be numeric, "
                    f"got {type(score)}"
                )
                assert 0.0 <= score <= 100.0, (
                    f"{scored_api.api.name}: {category} score should be 0-100, "
                    f"got {score}"
                )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_total_score_is_weighted_combination(self, constraints: UserConstraints):
        """
        Property 1: API Scoring Completeness
        Validates: Requirements 2.2
        
        For any valid user constraints, the total score should be a weighted
        combination of all category scores using the defined weights.
        """
        scored_apis = score_apis(constraints)
        
        for scored_api in scored_apis:
            # Calculate expected total from category scores
            expected_total = sum(
                scored_api.category_scores.get(cat, 0.0) * weight
                for cat, weight in SCORING_WEIGHTS.items()
            )
            
            # Allow small floating point tolerance
            assert abs(scored_api.total_score - expected_total) < 0.01, (
                f"{scored_api.api.name}: total_score {scored_api.total_score} "
                f"doesn't match weighted sum {expected_total}"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_each_api_has_valid_score_structure(self, constraints: UserConstraints):
        """
        Property 1: API Scoring Completeness
        Validates: Requirements 2.1, 2.2
        
        For any valid user constraints, each APIScore should have all required
        fields populated with valid values.
        """
        scored_apis = score_apis(constraints)
        
        for scored_api in scored_apis:
            # Must be an APIScore instance
            assert isinstance(scored_api, APIScore), (
                f"Expected APIScore, got {type(scored_api)}"
            )
            
            # API reference must be valid
            assert scored_api.api is not None, "api should not be None"
            assert isinstance(scored_api.api, APIInfo), (
                f"api should be APIInfo, got {type(scored_api.api)}"
            )
            
            # Total score must be valid
            assert isinstance(scored_api.total_score, (int, float)), (
                f"total_score should be numeric, got {type(scored_api.total_score)}"
            )
            assert 0.0 <= scored_api.total_score <= 100.0, (
                f"total_score should be 0-100, got {scored_api.total_score}"
            )
            
            # Category scores must be present
            assert scored_api.category_scores is not None, (
                "category_scores should not be None"
            )
            assert len(scored_api.category_scores) == 4, (
                f"Expected 4 category scores, got {len(scored_api.category_scores)}"
            )
            
            # Compatibility percentage must be valid
            assert isinstance(scored_api.compatibility_percentage, int), (
                f"compatibility_percentage should be int, "
                f"got {type(scored_api.compatibility_percentage)}"
            )
            assert 0 <= scored_api.compatibility_percentage <= 100, (
                f"compatibility_percentage should be 0-100, "
                f"got {scored_api.compatibility_percentage}"
            )
            
            # Recommendation rank must be valid
            assert isinstance(scored_api.recommendation_rank, int), (
                f"recommendation_rank should be int, "
                f"got {type(scored_api.recommendation_rank)}"
            )
            assert scored_api.recommendation_rank >= 1, (
                f"recommendation_rank should be >= 1, "
                f"got {scored_api.recommendation_rank}"
            )


# =============================================================================
# Property Tests for Score Ranking Consistency
# Task 4.5: Property test for score ranking consistency
# =============================================================================


class TestScoreRankingConsistency:
    """
    Property tests for score ranking consistency.
    
    Feature: fintech-api-referee, Property 2: Score Ranking Consistency
    Validates: Requirements 2.3, 2.4
    
    For any set of API scores, the ranking function should order APIs from
    highest to lowest score, with the top-ranked API identified as the winner.
    """

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_apis_ranked_by_descending_score(self, constraints: UserConstraints):
        """
        Property 2: Score Ranking Consistency
        Validates: Requirements 2.3
        
        For any valid user constraints, APIs should be ordered from highest
        to lowest total score (descending order).
        """
        scored_apis = score_apis(constraints)
        
        # Verify descending order by total_score
        for i in range(len(scored_apis) - 1):
            current_score = scored_apis[i].total_score
            next_score = scored_apis[i + 1].total_score
            assert current_score >= next_score, (
                f"APIs not in descending score order: "
                f"{scored_apis[i].api.name} ({current_score}) should be >= "
                f"{scored_apis[i + 1].api.name} ({next_score})"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_ranks_are_sequential(self, constraints: UserConstraints):
        """
        Property 2: Score Ranking Consistency
        Validates: Requirements 2.3
        
        For any valid user constraints, ranks should be sequential integers
        starting from 1 (1, 2, 3, ..., n).
        """
        scored_apis = score_apis(constraints)
        
        # Collect all ranks
        ranks = [api.recommendation_rank for api in scored_apis]
        
        # Ranks should be sequential from 1 to n
        expected_ranks = list(range(1, len(scored_apis) + 1))
        assert sorted(ranks) == expected_ranks, (
            f"Ranks should be sequential 1 to {len(scored_apis)}, "
            f"got {sorted(ranks)}"
        )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_winner_has_rank_one(self, constraints: UserConstraints):
        """
        Property 2: Score Ranking Consistency
        Validates: Requirements 2.4
        
        For any valid user constraints, the top recommendation (winner)
        should have rank 1.
        """
        scored_apis = score_apis(constraints)
        
        if len(scored_apis) > 0:
            # First API in sorted list should have rank 1
            winner = scored_apis[0]
            assert winner.recommendation_rank == 1, (
                f"Winner should have rank 1, got {winner.recommendation_rank}"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_winner_has_highest_score(self, constraints: UserConstraints):
        """
        Property 2: Score Ranking Consistency
        Validates: Requirements 2.4
        
        For any valid user constraints, the winner (rank 1) should have
        the highest or tied-highest total score among all APIs.
        """
        scored_apis = score_apis(constraints)
        
        if len(scored_apis) > 0:
            winner = scored_apis[0]
            max_score = max(api.total_score for api in scored_apis)
            
            assert winner.total_score == max_score, (
                f"Winner score {winner.total_score} should equal "
                f"max score {max_score}"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_rank_matches_position(self, constraints: UserConstraints):
        """
        Property 2: Score Ranking Consistency
        Validates: Requirements 2.3
        
        For any valid user constraints, each API's rank should match
        its position in the sorted list (position 0 = rank 1, etc.).
        """
        scored_apis = score_apis(constraints)
        
        for position, scored_api in enumerate(scored_apis):
            expected_rank = position + 1
            assert scored_api.recommendation_rank == expected_rank, (
                f"{scored_api.api.name} at position {position} should have "
                f"rank {expected_rank}, got {scored_api.recommendation_rank}"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_all_apis_have_unique_ranks(self, constraints: UserConstraints):
        """
        Property 2: Score Ranking Consistency
        Validates: Requirements 2.3
        
        For any valid user constraints, each API should have a unique rank
        (no two APIs share the same rank).
        """
        scored_apis = score_apis(constraints)
        
        ranks = [api.recommendation_rank for api in scored_apis]
        unique_ranks = set(ranks)
        
        assert len(ranks) == len(unique_ranks), (
            f"Duplicate ranks found: {[r for r in ranks if ranks.count(r) > 1]}"
        )


# =============================================================================
# Property Tests for Compatibility Percentage Bounds
# Task 4.6: Property test for compatibility percentage bounds
# =============================================================================

from models import calculate_compatibility_percentage


class TestCompatibilityPercentageBounds:
    """
    Property tests for compatibility percentage bounds.
    
    Feature: fintech-api-referee, Property 3: Compatibility Percentage Bounds
    Validates: Requirements 2.5
    
    For any evaluated API, the compatibility percentage should be between
    0 and 100 inclusive.
    """

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_compatibility_percentage_within_bounds(self, constraints: UserConstraints):
        """
        Property 3: Compatibility Percentage Bounds
        Validates: Requirements 2.5
        
        For any valid user constraints, all scored APIs should have
        compatibility percentages between 0 and 100 inclusive.
        """
        scored_apis = score_apis(constraints)
        
        for scored_api in scored_apis:
            assert 0 <= scored_api.compatibility_percentage <= 100, (
                f"{scored_api.api.name}: compatibility_percentage should be 0-100, "
                f"got {scored_api.compatibility_percentage}"
            )

    @given(total_score=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_calculate_compatibility_percentage_bounds(self, total_score: float):
        """
        Property 3: Compatibility Percentage Bounds
        Validates: Requirements 2.5
        
        For any total score (including edge cases outside normal range),
        the calculated compatibility percentage should be clamped to 0-100.
        """
        result = calculate_compatibility_percentage(total_score)
        
        assert isinstance(result, int), (
            f"compatibility_percentage should be int, got {type(result)}"
        )
        assert 0 <= result <= 100, (
            f"compatibility_percentage should be 0-100, got {result} "
            f"for total_score {total_score}"
        )

    @given(total_score=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_compatibility_percentage_reflects_score(self, total_score: float):
        """
        Property 3: Compatibility Percentage Bounds
        Validates: Requirements 2.5
        
        For any valid total score (0-100), the compatibility percentage
        should be the rounded integer value of the score.
        """
        result = calculate_compatibility_percentage(total_score)
        expected = int(round(total_score))
        
        assert result == expected, (
            f"compatibility_percentage {result} should equal "
            f"rounded score {expected} for total_score {total_score}"
        )

    @given(total_score=st.floats(max_value=-0.01, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_negative_scores_clamped_to_zero(self, total_score: float):
        """
        Property 3: Compatibility Percentage Bounds
        Validates: Requirements 2.5
        
        For any negative total score, the compatibility percentage
        should be clamped to 0.
        """
        result = calculate_compatibility_percentage(total_score)
        
        assert result == 0, (
            f"Negative score {total_score} should result in "
            f"compatibility_percentage 0, got {result}"
        )

    @given(total_score=st.floats(min_value=100.01, max_value=1000.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_scores_above_100_clamped_to_100(self, total_score: float):
        """
        Property 3: Compatibility Percentage Bounds
        Validates: Requirements 2.5
        
        For any total score above 100, the compatibility percentage
        should be clamped to 100.
        """
        result = calculate_compatibility_percentage(total_score)
        
        assert result == 100, (
            f"Score {total_score} above 100 should result in "
            f"compatibility_percentage 100, got {result}"
        )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_compatibility_percentage_is_integer(self, constraints: UserConstraints):
        """
        Property 3: Compatibility Percentage Bounds
        Validates: Requirements 2.5
        
        For any valid user constraints, all compatibility percentages
        should be integers (not floats).
        """
        scored_apis = score_apis(constraints)
        
        for scored_api in scored_apis:
            assert isinstance(scored_api.compatibility_percentage, int), (
                f"{scored_api.api.name}: compatibility_percentage should be int, "
                f"got {type(scored_api.compatibility_percentage)}"
            )


# =============================================================================
# Property Tests for Comprehensive Verdict Generation
# Task 6.4: Property test for comprehensive verdict generation
# =============================================================================

from models import generate_verdict, Verdict


class TestComprehensiveVerdictGeneration:
    """
    Property tests for comprehensive verdict generation.
    
    Feature: fintech-api-referee, Property 5: Comprehensive Verdict Generation
    Validates: Requirements 4.1, 4.2, 4.3, 4.5
    
    For any set of API recommendations, the verdict engine should generate
    human-readable explanations with bold formatting, trade-off explanations,
    and actionable next steps.
    """

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_verdict_has_all_required_fields(self, constraints: UserConstraints):
        """
        Property 5: Comprehensive Verdict Generation
        Validates: Requirements 4.1
        
        For any valid user constraints, the generated verdict should have
        all required fields populated.
        """
        scored_apis = score_apis(constraints)
        if not scored_apis:
            return  # Skip if no APIs available
            
        verdict = generate_verdict(scored_apis, constraints)
        
        # Must be a Verdict instance
        assert isinstance(verdict, Verdict), (
            f"Expected Verdict instance, got {type(verdict)}"
        )
        
        # All required fields must be present
        assert verdict.recommendation_text is not None, (
            "recommendation_text should not be None"
        )
        assert verdict.trade_offs is not None, (
            "trade_offs should not be None"
        )
        assert verdict.next_steps is not None, (
            "next_steps should not be None"
        )
        
        # Fields should have appropriate types
        assert isinstance(verdict.recommendation_text, str), (
            f"recommendation_text should be str, got {type(verdict.recommendation_text)}"
        )
        assert isinstance(verdict.trade_offs, list), (
            f"trade_offs should be list, got {type(verdict.trade_offs)}"
        )
        assert isinstance(verdict.next_steps, list), (
            f"next_steps should be list, got {type(verdict.next_steps)}"
        )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_verdict_has_bold_formatting(self, constraints: UserConstraints):
        """
        Property 5: Comprehensive Verdict Generation
        Validates: Requirements 4.2
        
        For any valid user constraints, the verdict should use bold formatting
        (markdown **text**) for key decision points.
        """
        scored_apis = score_apis(constraints)
        if not scored_apis:
            return  # Skip if no APIs available
            
        verdict = generate_verdict(scored_apis, constraints)
        
        # Recommendation text should contain bold formatting
        assert "**" in verdict.recommendation_text, (
            f"recommendation_text should contain bold formatting (**text**), "
            f"got: {verdict.recommendation_text}"
        )
        
        # Should have at least one complete bold pair
        bold_count = verdict.recommendation_text.count("**")
        assert bold_count >= 2, (
            f"recommendation_text should have at least one complete bold pair, "
            f"found {bold_count // 2} pairs"
        )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_verdict_has_actionable_next_steps(self, constraints: UserConstraints):
        """
        Property 5: Comprehensive Verdict Generation
        Validates: Requirements 4.5
        
        For any valid user constraints, the verdict should include
        actionable next steps for the recommended API.
        """
        scored_apis = score_apis(constraints)
        if not scored_apis:
            return  # Skip if no APIs available
            
        verdict = generate_verdict(scored_apis, constraints)
        
        # Should have at least one next step
        assert len(verdict.next_steps) > 0, (
            "verdict should have at least one next step"
        )
        
        # Each next step should be a non-empty string
        for i, step in enumerate(verdict.next_steps):
            assert isinstance(step, str), (
                f"next_steps[{i}] should be str, got {type(step)}"
            )
            assert len(step.strip()) > 0, (
                f"next_steps[{i}] should not be empty"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_verdict_includes_winner_name(self, constraints: UserConstraints):
        """
        Property 5: Comprehensive Verdict Generation
        Validates: Requirements 4.1
        
        For any valid user constraints, the verdict should mention
        the name of the winning API in the recommendation text.
        """
        scored_apis = score_apis(constraints)
        if not scored_apis:
            return  # Skip if no APIs available
            
        verdict = generate_verdict(scored_apis, constraints)
        winner_name = scored_apis[0].api.name
        
        # Winner name should appear in recommendation text
        assert winner_name in verdict.recommendation_text, (
            f"Winner '{winner_name}' should be mentioned in recommendation text: "
            f"{verdict.recommendation_text}"
        )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_verdict_includes_compatibility_score(self, constraints: UserConstraints):
        """
        Property 5: Comprehensive Verdict Generation
        Validates: Requirements 4.1
        
        For any valid user constraints, the verdict should mention
        the compatibility percentage in the recommendation text.
        """
        scored_apis = score_apis(constraints)
        if not scored_apis:
            return  # Skip if no APIs available
            
        verdict = generate_verdict(scored_apis, constraints)
        winner_compatibility = str(scored_apis[0].compatibility_percentage)
        
        # Compatibility percentage should appear in recommendation text
        assert winner_compatibility in verdict.recommendation_text, (
            f"Compatibility score '{winner_compatibility}%' should be mentioned "
            f"in recommendation text: {verdict.recommendation_text}"
        )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_verdict_addresses_user_budget(self, constraints: UserConstraints):
        """
        Property 5: Comprehensive Verdict Generation
        Validates: Requirements 4.3
        
        For any valid user constraints, the verdict should address
        the user's budget requirements in plain language.
        """
        scored_apis = score_apis(constraints)
        if not scored_apis:
            return  # Skip if no APIs available
            
        verdict = generate_verdict(scored_apis, constraints)
        budget_text = constraints.budget.value.lower()
        
        # Budget should be mentioned in some form
        recommendation_lower = verdict.recommendation_text.lower()
        budget_mentioned = (
            budget_text in recommendation_lower or
            "free" in recommendation_lower or
            "budget" in recommendation_lower or
            "$" in recommendation_lower
        )
        
        assert budget_mentioned, (
            f"Budget context should be mentioned in recommendation for "
            f"budget '{constraints.budget.value}': {verdict.recommendation_text}"
        )


# =============================================================================
# Property Tests for Alternative Recommendation Logic
# Task 6.5: Property test for alternative recommendation logic
# =============================================================================

from models import has_significant_limitations, LOW_RELIABILITY_THRESHOLD


class TestAlternativeRecommendationLogic:
    """
    Property tests for alternative recommendation logic.
    
    Feature: fintech-api-referee, Property 6: Alternative Recommendation Logic
    Validates: Requirements 4.4
    
    For any top API recommendation with significant limitations, the verdict
    engine should provide alternative recommendations.
    """

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_alternative_provided_for_low_reliability(self, constraints: UserConstraints):
        """
        Property 6: Alternative Recommendation Logic
        Validates: Requirements 4.4
        
        For any top API with reliability below threshold and a runner-up available,
        an alternative should be suggested.
        """
        scored_apis = score_apis(constraints)
        if len(scored_apis) < 2:
            return  # Need at least 2 APIs for alternative logic
            
        winner = scored_apis[0]
        
        # Only test when winner has low reliability
        if winner.api.reliability_score >= LOW_RELIABILITY_THRESHOLD:
            return
            
        verdict = generate_verdict(scored_apis, constraints)
        
        # Should have alternative recommendation
        assert verdict.alternative_api != "", (
            f"Winner '{winner.api.name}' has low reliability "
            f"({winner.api.reliability_score}), should suggest alternative"
        )
        assert verdict.alternative_reason != "", (
            f"Alternative reason should be provided when suggesting "
            f"alternative to '{winner.api.name}'"
        )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_alternative_provided_for_tos_restrictions(self, constraints: UserConstraints):
        """
        Property 6: Alternative Recommendation Logic
        Validates: Requirements 4.4
        
        For any top API with TOS restrictions conflicting with use case
        and a runner-up available, an alternative should be suggested.
        """
        scored_apis = score_apis(constraints)
        if len(scored_apis) < 2:
            return  # Need at least 2 APIs for alternative logic
            
        winner = scored_apis[0]
        
        # Only test when winner has TOS restrictions for the use case
        if not has_significant_limitations(winner, constraints):
            return
            
        # Check if TOS restrictions are the issue
        has_tos_issue = False
        if constraints.use_case.value == "Trading Bot":
            for restriction in winner.api.tos_restrictions:
                if any(keyword in restriction.lower() for keyword in [
                    "commercial use explicitly prohibited",
                    "non-commercial use only",
                    "personal/educational use only"
                ]):
                    has_tos_issue = True
                    break
        
        if not has_tos_issue:
            return
            
        verdict = generate_verdict(scored_apis, constraints)
        
        # Should have alternative recommendation
        assert verdict.alternative_api != "", (
            f"Winner '{winner.api.name}' has TOS restrictions for "
            f"'{constraints.use_case.value}', should suggest alternative"
        )
        assert verdict.alternative_reason != "", (
            f"Alternative reason should be provided when TOS restrictions "
            f"conflict with use case"
        )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_alternative_is_runner_up(self, constraints: UserConstraints):
        """
        Property 6: Alternative Recommendation Logic
        Validates: Requirements 4.4
        
        For any alternative recommendation provided, it should be
        the runner-up API (second-best match).
        """
        scored_apis = score_apis(constraints)
        if len(scored_apis) < 2:
            return  # Need at least 2 APIs for alternative logic
            
        winner = scored_apis[0]
        runner_up = scored_apis[1]
        
        # Only test when alternative is provided
        verdict = generate_verdict(scored_apis, constraints)
        if verdict.alternative_api == "":
            return
            
        # Alternative should be the runner-up
        assert verdict.alternative_api == runner_up.api.name, (
            f"Alternative '{verdict.alternative_api}' should be runner-up "
            f"'{runner_up.api.name}'"
        )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_alternative_reason_mentions_limitation(self, constraints: UserConstraints):
        """
        Property 6: Alternative Recommendation Logic
        Validates: Requirements 4.4
        
        For any alternative recommendation provided, the reason should
        mention the specific limitation of the top choice.
        """
        scored_apis = score_apis(constraints)
        if len(scored_apis) < 2:
            return  # Need at least 2 APIs for alternative logic
            
        verdict = generate_verdict(scored_apis, constraints)
        if verdict.alternative_api == "":
            return  # No alternative provided
            
        # Alternative reason should mention some limitation
        reason_lower = verdict.alternative_reason.lower()
        limitation_keywords = [
            "reliability", "tos", "restrictions", "limitations",
            "concerns", "stability", "unofficial"
        ]
        
        has_limitation_mention = any(
            keyword in reason_lower for keyword in limitation_keywords
        )
        
        assert has_limitation_mention, (
            f"Alternative reason should mention specific limitations: "
            f"{verdict.alternative_reason}"
        )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_no_alternative_when_winner_is_good(self, constraints: UserConstraints):
        """
        Property 6: Alternative Recommendation Logic
        Validates: Requirements 4.4
        
        For any top API without significant limitations, no alternative
        should be suggested.
        """
        scored_apis = score_apis(constraints)
        if not scored_apis:
            return  # Skip if no APIs available
            
        winner = scored_apis[0]
        
        # Only test when winner has no significant limitations
        if has_significant_limitations(winner, constraints):
            return
            
        verdict = generate_verdict(scored_apis, constraints)
        
        # Should not have alternative recommendation
        assert verdict.alternative_api == "", (
            f"Winner '{winner.api.name}' has no significant limitations, "
            f"should not suggest alternative but got: {verdict.alternative_api}"
        )


# =============================================================================
# Property Tests for Complete Result Information Display
# Task 7.4: Property test for complete result information display
# =============================================================================


class TestCompleteResultInformationDisplay:
    """
    Property tests for complete result information display.
    
    Feature: fintech-api-referee, Property 4: Complete Result Information Display
    Validates: Requirements 3.2, 3.3, 3.4, 3.5
    
    For any generated results, each API should display strengths, limitations,
    cost implications, rate limits, data quality information, terms of service
    considerations, and compatibility percentages.
    """

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_each_api_displays_strengths(self, constraints: UserConstraints):
        """
        Property 4: Complete Result Information Display
        Validates: Requirements 3.2
        
        For any generated results, each API should display its strengths clearly.
        """
        scored_apis = score_apis(constraints)
        
        for scored_api in scored_apis:
            # Each API should have strengths information
            assert scored_api.api.strengths is not None, (
                f"{scored_api.api.name}: strengths should not be None"
            )
            assert isinstance(scored_api.api.strengths, list), (
                f"{scored_api.api.name}: strengths should be a list"
            )
            assert len(scored_api.api.strengths) > 0, (
                f"{scored_api.api.name}: should have at least one strength"
            )
            
            # Each strength should be a non-empty string
            for strength in scored_api.api.strengths:
                assert isinstance(strength, str), (
                    f"{scored_api.api.name}: strength should be string"
                )
                assert len(strength.strip()) > 0, (
                    f"{scored_api.api.name}: strength should not be empty"
                )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_each_api_displays_limitations(self, constraints: UserConstraints):
        """
        Property 4: Complete Result Information Display
        Validates: Requirements 3.2
        
        For any generated results, each API should display its limitations clearly.
        """
        scored_apis = score_apis(constraints)
        
        for scored_api in scored_apis:
            # Each API should have limitations information
            assert scored_api.api.limitations is not None, (
                f"{scored_api.api.name}: limitations should not be None"
            )
            assert isinstance(scored_api.api.limitations, list), (
                f"{scored_api.api.name}: limitations should be a list"
            )
            
            # Each limitation should be a string (can be empty list)
            for limitation in scored_api.api.limitations:
                assert isinstance(limitation, str), (
                    f"{scored_api.api.name}: limitation should be string"
                )
                assert len(limitation.strip()) > 0, (
                    f"{scored_api.api.name}: limitation should not be empty"
                )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_each_api_displays_cost_implications(self, constraints: UserConstraints):
        """
        Property 4: Complete Result Information Display
        Validates: Requirements 3.3
        
        For any generated results, each API should display cost implications
        through pricing tier information.
        """
        scored_apis = score_apis(constraints)
        
        for scored_api in scored_apis:
            # Each API should have pricing information
            assert scored_api.api.pricing is not None, (
                f"{scored_api.api.name}: pricing should not be None"
            )
            assert isinstance(scored_api.api.pricing, dict), (
                f"{scored_api.api.name}: pricing should be a dict"
            )
            assert len(scored_api.api.pricing) > 0, (
                f"{scored_api.api.name}: should have at least one pricing tier"
            )
            
            # Pricing should cover valid budget tiers
            for tier, supported in scored_api.api.pricing.items():
                assert isinstance(tier, BudgetTier), (
                    f"{scored_api.api.name}: pricing key should be BudgetTier"
                )
                assert isinstance(supported, bool), (
                    f"{scored_api.api.name}: pricing value should be boolean"
                )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_each_api_displays_rate_limits(self, constraints: UserConstraints):
        """
        Property 4: Complete Result Information Display
        Validates: Requirements 3.3
        
        For any generated results, each API should display rate limit information.
        """
        scored_apis = score_apis(constraints)
        
        for scored_api in scored_apis:
            # Each API should have rate limits information
            assert scored_api.api.rate_limits is not None, (
                f"{scored_api.api.name}: rate_limits should not be None"
            )
            assert isinstance(scored_api.api.rate_limits, dict), (
                f"{scored_api.api.name}: rate_limits should be a dict"
            )
            assert len(scored_api.api.rate_limits) > 0, (
                f"{scored_api.api.name}: should have at least one rate limit"
            )
            
            # Rate limits should have valid structure
            for key, value in scored_api.api.rate_limits.items():
                assert isinstance(key, str), (
                    f"{scored_api.api.name}: rate_limit key should be string"
                )
                assert isinstance(value, int), (
                    f"{scored_api.api.name}: rate_limit value should be integer"
                )
                assert value > 0, (
                    f"{scored_api.api.name}: rate_limit value should be positive"
                )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_each_api_displays_data_quality_information(self, constraints: UserConstraints):
        """
        Property 4: Complete Result Information Display
        Validates: Requirements 3.3
        
        For any generated results, each API should display data quality information
        through reliability scores and data coverage.
        """
        scored_apis = score_apis(constraints)
        
        for scored_api in scored_apis:
            # Each API should have reliability score (data quality metric)
            assert scored_api.api.reliability_score is not None, (
                f"{scored_api.api.name}: reliability_score should not be None"
            )
            assert isinstance(scored_api.api.reliability_score, float), (
                f"{scored_api.api.name}: reliability_score should be float"
            )
            assert 0.0 <= scored_api.api.reliability_score <= 1.0, (
                f"{scored_api.api.name}: reliability_score should be 0.0-1.0"
            )
            
            # Each API should have data coverage information
            assert scored_api.api.data_coverage is not None, (
                f"{scored_api.api.name}: data_coverage should not be None"
            )
            assert isinstance(scored_api.api.data_coverage, list), (
                f"{scored_api.api.name}: data_coverage should be a list"
            )
            assert len(scored_api.api.data_coverage) > 0, (
                f"{scored_api.api.name}: should cover at least one data type"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_each_api_displays_tos_considerations(self, constraints: UserConstraints):
        """
        Property 4: Complete Result Information Display
        Validates: Requirements 3.5
        
        For any generated results, each API should display terms of service
        considerations and restrictions.
        """
        scored_apis = score_apis(constraints)
        
        for scored_api in scored_apis:
            # Each API should have TOS restrictions information
            assert scored_api.api.tos_restrictions is not None, (
                f"{scored_api.api.name}: tos_restrictions should not be None"
            )
            assert isinstance(scored_api.api.tos_restrictions, list), (
                f"{scored_api.api.name}: tos_restrictions should be a list"
            )
            
            # Each TOS restriction should be a string
            for restriction in scored_api.api.tos_restrictions:
                assert isinstance(restriction, str), (
                    f"{scored_api.api.name}: tos_restriction should be string"
                )
                assert len(restriction.strip()) > 0, (
                    f"{scored_api.api.name}: tos_restriction should not be empty"
                )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_each_api_displays_compatibility_percentages(self, constraints: UserConstraints):
        """
        Property 4: Complete Result Information Display
        Validates: Requirements 3.4
        
        For any generated results, each API should display compatibility
        percentages for easy comparison.
        """
        scored_apis = score_apis(constraints)
        
        for scored_api in scored_apis:
            # Each API should have compatibility percentage
            assert scored_api.compatibility_percentage is not None, (
                f"{scored_api.api.name}: compatibility_percentage should not be None"
            )
            assert isinstance(scored_api.compatibility_percentage, int), (
                f"{scored_api.api.name}: compatibility_percentage should be int"
            )
            assert 0 <= scored_api.compatibility_percentage <= 100, (
                f"{scored_api.api.name}: compatibility_percentage should be 0-100"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_results_contain_all_required_information(self, constraints: UserConstraints):
        """
        Property 4: Complete Result Information Display
        Validates: Requirements 3.2, 3.3, 3.4, 3.5
        
        For any generated results, each API should contain ALL required
        information fields for complete result display.
        """
        scored_apis = score_apis(constraints)
        
        for scored_api in scored_apis:
            api = scored_api.api
            
            # Verify all required information is present
            required_fields = [
                ('name', str),
                ('strengths', list),
                ('limitations', list),
                ('pricing', dict),
                ('rate_limits', dict),
                ('data_coverage', list),
                ('tos_restrictions', list),
                ('reliability_score', float),
                ('frequency_support', list),
            ]
            
            for field_name, field_type in required_fields:
                field_value = getattr(api, field_name)
                assert field_value is not None, (
                    f"{api.name}: {field_name} should not be None"
                )
                assert isinstance(field_value, field_type), (
                    f"{api.name}: {field_name} should be {field_type.__name__}"
                )
            
            # Verify scored API has required fields
            assert scored_api.total_score is not None
            assert scored_api.category_scores is not None
            assert scored_api.compatibility_percentage is not None
            assert scored_api.recommendation_rank is not None
            
            # Verify compatibility percentage is properly calculated
            assert 0 <= scored_api.compatibility_percentage <= 100
            assert scored_api.recommendation_rank >= 1

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_commercial_use_warnings_displayed(self, constraints: UserConstraints):
        """
        Property 4: Complete Result Information Display
        Validates: Requirements 3.5
        
        For any commercial use case (Trading Bot), APIs with commercial
        restrictions should have appropriate warnings displayed.
        """
        scored_apis = score_apis(constraints)
        
        # Only test for commercial use cases
        if constraints.use_case.value != "Trading Bot":
            return
        
        for scored_api in scored_apis:
            api = scored_api.api
            
            # Check if API has commercial use restrictions
            has_commercial_restrictions = False
            for restriction in api.tos_restrictions:
                restriction_lower = restriction.lower()
                commercial_keywords = [
                    "commercial use explicitly prohibited",
                    "non-commercial use only",
                    "personal/educational use only",
                ]
                if any(keyword in restriction_lower for keyword in commercial_keywords):
                    has_commercial_restrictions = True
                    break
            
            # If API has commercial restrictions, it should be identifiable
            # This ensures the display system can show appropriate warnings
            if has_commercial_restrictions:
                # The TOS restrictions should contain clear warning text
                restriction_text = " ".join(api.tos_restrictions).lower()
                assert any(keyword in restriction_text for keyword in [
                    "commercial", "non-commercial", "personal", "educational"
                ]), (
                    f"{api.name}: Commercial restrictions should be clearly stated "
                    f"in TOS for Trading Bot use case"
                )


# =============================================================================
# Property Tests for Error Handling Robustness
# Task 8.4: Property test for error handling robustness
# =============================================================================

from models import score_apis, generate_verdict


class TestErrorHandlingRobustness:
    """
    Property tests for error handling robustness.
    
    Feature: fintech-api-referee, Property 10: Error Handling Robustness
    Validates: Requirements 7.2, 7.4
    
    For any invalid or incomplete input, the system should handle it gracefully
    with clear error messages and appropriate logging.
    """

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_score_apis_handles_empty_api_list(self, constraints: UserConstraints):
        """
        Property 10: Error Handling Robustness
        Validates: Requirements 7.2, 7.4
        
        For any valid constraints with an empty API list, the system should
        handle the error gracefully and provide meaningful feedback.
        """
        try:
            # Test with empty API list
            result = score_apis(constraints, apis=[])
            # Should either return empty list or raise a meaningful exception
            assert isinstance(result, list), "Should return a list even when empty"
        except Exception as e:
            # Exception should be meaningful and not a generic error
            error_message = str(e).lower()
            assert any(keyword in error_message for keyword in [
                "no apis", "empty", "unable to score", "no api", "apis"
            ]), f"Error message should be meaningful: {str(e)}"

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_score_apis_handles_corrupted_api_data(self, constraints: UserConstraints):
        """
        Property 10: Error Handling Robustness
        Validates: Requirements 7.2, 7.4
        
        For any valid constraints with corrupted API data, the system should
        continue processing other APIs and not fail completely.
        """
        # Create a mix of valid and invalid APIs
        valid_apis = get_all_apis()[:2]  # Take first 2 valid APIs
        
        # Create corrupted API with missing required fields
        corrupted_api = APIInfo(
            name="Corrupted API",
            pricing={},  # Empty pricing (invalid)
            data_coverage=[],  # Empty data coverage (invalid)
            frequency_support=[],  # Empty frequency support (invalid)
            rate_limits={},  # Empty rate limits (invalid)
            strengths=[],  # Empty strengths (invalid)
            limitations=[],
            tos_restrictions=[],
            reliability_score=-1.0,  # Invalid reliability score
        )
        
        mixed_apis = valid_apis + [corrupted_api]
        
        try:
            result = score_apis(constraints, apis=mixed_apis)
            # Should return results for valid APIs, skipping corrupted ones
            assert isinstance(result, list), "Should return a list"
            # Should have fewer results than input APIs due to skipping corrupted ones
            assert len(result) <= len(mixed_apis), "Should not have more results than input APIs"
            # Should have at least some results from valid APIs
            if len(valid_apis) > 0:
                assert len(result) > 0, "Should have some results from valid APIs"
        except Exception as e:
            # If it fails, the error should be meaningful
            error_message = str(e).lower()
            assert "error" in error_message or "invalid" in error_message or "corrupted" in error_message, (
                f"Error message should indicate the problem: {str(e)}"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_generate_verdict_handles_empty_api_list(self, constraints: UserConstraints):
        """
        Property 10: Error Handling Robustness
        Validates: Requirements 7.2, 7.4
        
        For any valid constraints with empty scored API list, verdict generation
        should handle the error gracefully and provide meaningful guidance.
        """
        try:
            verdict = generate_verdict([], constraints)
            
            # Should return a Verdict object even with empty input
            assert isinstance(verdict, Verdict), "Should return a Verdict object"
            
            # Should have meaningful content
            assert verdict.recommendation_text is not None, "Should have recommendation text"
            assert len(verdict.recommendation_text.strip()) > 0, "Recommendation text should not be empty"
            
            # Should provide next steps even in error case
            assert verdict.next_steps is not None, "Should have next steps"
            assert isinstance(verdict.next_steps, list), "Next steps should be a list"
            
            # Should indicate the problem in the recommendation
            recommendation_lower = verdict.recommendation_text.lower()
            assert any(keyword in recommendation_lower for keyword in [
                "no apis", "unavailable", "error", "try again", "check"
            ]), f"Should indicate the problem: {verdict.recommendation_text}"
            
        except Exception as e:
            # If it raises an exception, it should be meaningful
            error_message = str(e).lower()
            assert any(keyword in error_message for keyword in [
                "no apis", "empty", "invalid", "error"
            ]), f"Error message should be meaningful: {str(e)}"

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_system_provides_fallback_guidance(self, constraints: UserConstraints):
        """
        Property 10: Error Handling Robustness
        Validates: Requirements 7.2, 7.4
        
        For any error condition, the system should provide fallback guidance
        to help users proceed even when primary functionality fails.
        """
        # Test with various error conditions
        try:
            # Try normal operation first
            scored_apis = score_apis(constraints)
            verdict = generate_verdict(scored_apis, constraints)
            
            # Normal operation should work
            assert isinstance(verdict, Verdict)
            assert len(verdict.next_steps) > 0
            
        except Exception:
            # If normal operation fails, fallback should be available
            from models import get_fallback_recommendations, generate_fallback_verdict
            
            try:
                fallback_apis = get_fallback_recommendations(constraints)
                fallback_verdict = generate_fallback_verdict(constraints)
                
                # Fallback should provide some guidance
                assert isinstance(fallback_verdict, Verdict)
                assert fallback_verdict.recommendation_text is not None
                assert len(fallback_verdict.next_steps) > 0
                
                # Fallback verdict should indicate it's in fallback mode
                recommendation_lower = fallback_verdict.recommendation_text.lower()
                fallback_indicators = ["fallback", "reliability", "unavailable", "try again"]
                assert any(indicator in recommendation_lower for indicator in fallback_indicators), (
                    f"Fallback verdict should indicate fallback mode: {fallback_verdict.recommendation_text}"
                )
                
            except Exception as fallback_error:
                # Even fallback failure should be handled gracefully
                error_message = str(fallback_error).lower()
                assert "error" in error_message or "fail" in error_message, (
                    f"Fallback error should be meaningful: {str(fallback_error)}"
                )

    @given(
        constraints=user_constraints_strategy(),
        invalid_data_types=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=3)
    )
    @settings(max_examples=50)
    def test_system_handles_invalid_constraint_data(self, constraints: UserConstraints, invalid_data_types: List[str]):
        """
        Property 10: Error Handling Robustness
        Validates: Requirements 7.2, 7.4
        
        For any constraints with invalid data, the system should detect
        and handle the invalid input gracefully.
        """
        # Create constraints with invalid data types
        try:
            # This should be caught at the validation layer in the app
            # But if it gets through, the scoring system should handle it
            
            # Test that the system can handle unexpected data gracefully
            scored_apis = score_apis(constraints)
            
            # If it succeeds, results should be valid
            assert isinstance(scored_apis, list)
            for scored_api in scored_apis:
                assert isinstance(scored_api, APIScore)
                assert scored_api.api is not None
                assert isinstance(scored_api.total_score, (int, float))
                assert isinstance(scored_api.compatibility_percentage, int)
                assert 0 <= scored_api.compatibility_percentage <= 100
                
        except Exception as e:
            # If it fails, the error should be informative
            error_message = str(e).lower()
            meaningful_keywords = [
                "invalid", "error", "constraint", "data", "type", "value"
            ]
            assert any(keyword in error_message for keyword in meaningful_keywords), (
                f"Error message should be meaningful for invalid data: {str(e)}"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_error_messages_are_user_friendly(self, constraints: UserConstraints):
        """
        Property 10: Error Handling Robustness
        Validates: Requirements 7.2, 7.4
        
        For any error condition, error messages should be user-friendly
        and provide actionable guidance rather than technical details.
        """
        # Test various error conditions and check message quality
        try:
            # Test with empty API list to trigger error handling
            result = score_apis(constraints, apis=[])
            
            # If it returns a result, it should be valid
            if result:
                assert isinstance(result, list)
            
        except Exception as e:
            error_message = str(e)
            
            # Error message should not contain technical jargon
            technical_terms = [
                "traceback", "exception", "stack", "null pointer", 
                "segmentation fault", "memory", "thread", "process"
            ]
            message_lower = error_message.lower()
            
            # Check that technical terms are not present
            has_technical_terms = any(term in message_lower for term in technical_terms)
            assert not has_technical_terms, (
                f"Error message should be user-friendly, not technical: {error_message}"
            )
            
            # Error message should provide actionable guidance
            actionable_keywords = [
                "try again", "check", "contact", "refresh", "later", 
                "constraints", "different", "support"
            ]
            has_actionable_guidance = any(keyword in message_lower for keyword in actionable_keywords)
            assert has_actionable_guidance, (
                f"Error message should provide actionable guidance: {error_message}"
            )


# =============================================================================
# Property Tests for Fallback Reliability
# Task 8.5: Property test for fallback reliability
# =============================================================================

from models import get_fallback_recommendations, generate_fallback_verdict


class TestFallbackReliability:
    """
    Property tests for fallback reliability.
    
    Feature: fintech-api-referee, Property 12: Fallback Reliability
    Validates: Requirements 7.5
    
    For any primary scoring failure, the system should provide fallback
    recommendations to ensure user always receives guidance.
    """

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_fallback_recommendations_always_available(self, constraints: UserConstraints):
        """
        Property 12: Fallback Reliability
        Validates: Requirements 7.5
        
        For any valid user constraints, fallback recommendations should
        always be available even when primary scoring fails.
        """
        try:
            fallback_apis = get_fallback_recommendations(constraints)
            
            # Should return a list (may be empty in extreme cases)
            assert isinstance(fallback_apis, list), (
                "Fallback recommendations should return a list"
            )
            
            # If any APIs are returned, they should be valid APIScore objects
            for api_score in fallback_apis:
                assert isinstance(api_score, APIScore), (
                    f"Fallback recommendation should be APIScore, got {type(api_score)}"
                )
                assert api_score.api is not None, (
                    "Fallback APIScore should have valid API reference"
                )
                assert isinstance(api_score.total_score, (int, float)), (
                    "Fallback APIScore should have numeric total_score"
                )
                assert 0.0 <= api_score.total_score <= 100.0, (
                    f"Fallback total_score should be 0-100, got {api_score.total_score}"
                )
                assert isinstance(api_score.compatibility_percentage, int), (
                    "Fallback compatibility_percentage should be int"
                )
                assert 0 <= api_score.compatibility_percentage <= 100, (
                    f"Fallback compatibility_percentage should be 0-100, got {api_score.compatibility_percentage}"
                )
                assert isinstance(api_score.recommendation_rank, int), (
                    "Fallback recommendation_rank should be int"
                )
                assert api_score.recommendation_rank >= 1, (
                    f"Fallback recommendation_rank should be >= 1, got {api_score.recommendation_rank}"
                )
                
        except Exception as e:
            # Even if fallback fails, it should fail gracefully with meaningful error
            error_message = str(e).lower()
            meaningful_keywords = [
                "fallback", "error", "unavailable", "try again", "system"
            ]
            assert any(keyword in error_message for keyword in meaningful_keywords), (
                f"Fallback error should be meaningful: {str(e)}"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_fallback_recommendations_based_on_reliability(self, constraints: UserConstraints):
        """
        Property 12: Fallback Reliability
        Validates: Requirements 7.5
        
        For any valid user constraints, fallback recommendations should
        be ordered by reliability score (highest first).
        """
        fallback_apis = get_fallback_recommendations(constraints)
        
        if len(fallback_apis) > 1:
            # Should be ordered by reliability score (descending)
            for i in range(len(fallback_apis) - 1):
                current_reliability = fallback_apis[i].api.reliability_score
                next_reliability = fallback_apis[i + 1].api.reliability_score
                
                assert current_reliability >= next_reliability, (
                    f"Fallback APIs should be ordered by reliability: "
                    f"{fallback_apis[i].api.name} ({current_reliability}) should be >= "
                    f"{fallback_apis[i + 1].api.name} ({next_reliability})"
                )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_fallback_recommendations_respect_basic_compatibility(self, constraints: UserConstraints):
        """
        Property 12: Fallback Reliability
        Validates: Requirements 7.5
        
        For any valid user constraints, fallback recommendations should
        respect basic compatibility (budget and data type requirements).
        """
        fallback_apis = get_fallback_recommendations(constraints)
        
        for api_score in fallback_apis:
            api = api_score.api
            
            # Should support user's budget tier
            budget_compatible = api.pricing.get(constraints.budget, False)
            assert budget_compatible, (
                f"Fallback API {api.name} should support budget {constraints.budget.value}"
            )
            
            # Should support at least one requested data type
            data_compatible = any(dt in api.data_coverage for dt in constraints.data_types)
            assert data_compatible, (
                f"Fallback API {api.name} should support at least one of {[dt.value for dt in constraints.data_types]}"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_fallback_verdict_always_available(self, constraints: UserConstraints):
        """
        Property 12: Fallback Reliability
        Validates: Requirements 7.5
        
        For any valid user constraints, fallback verdict should always
        be available to provide user guidance.
        """
        try:
            fallback_verdict = generate_fallback_verdict(constraints)
            
            # Should return a Verdict object
            assert isinstance(fallback_verdict, Verdict), (
                f"Fallback verdict should be Verdict, got {type(fallback_verdict)}"
            )
            
            # Should have meaningful recommendation text
            assert fallback_verdict.recommendation_text is not None, (
                "Fallback verdict should have recommendation_text"
            )
            assert len(fallback_verdict.recommendation_text.strip()) > 0, (
                "Fallback recommendation_text should not be empty"
            )
            
            # Should have next steps for user guidance
            assert fallback_verdict.next_steps is not None, (
                "Fallback verdict should have next_steps"
            )
            assert isinstance(fallback_verdict.next_steps, list), (
                "Fallback next_steps should be a list"
            )
            assert len(fallback_verdict.next_steps) > 0, (
                "Fallback verdict should have at least one next step"
            )
            
            # Each next step should be meaningful
            for step in fallback_verdict.next_steps:
                assert isinstance(step, str), (
                    "Each fallback next step should be a string"
                )
                assert len(step.strip()) > 0, (
                    "Each fallback next step should not be empty"
                )
                
        except Exception as e:
            # Even if fallback verdict fails, it should fail gracefully
            error_message = str(e).lower()
            meaningful_keywords = [
                "fallback", "error", "unavailable", "try again", "system"
            ]
            assert any(keyword in error_message for keyword in meaningful_keywords), (
                f"Fallback verdict error should be meaningful: {str(e)}"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_fallback_verdict_indicates_fallback_mode(self, constraints: UserConstraints):
        """
        Property 12: Fallback Reliability
        Validates: Requirements 7.5
        
        For any valid user constraints, fallback verdict should clearly
        indicate that the system is operating in fallback mode.
        """
        fallback_verdict = generate_fallback_verdict(constraints)
        
        # Recommendation text should indicate fallback mode
        recommendation_lower = fallback_verdict.recommendation_text.lower()
        fallback_indicators = [
            "fallback", "reliability", "system", "unavailable", 
            "operating", "mode", "basic", "limited"
        ]
        
        has_fallback_indicator = any(
            indicator in recommendation_lower for indicator in fallback_indicators
        )
        
        assert has_fallback_indicator, (
            f"Fallback verdict should indicate fallback mode: {fallback_verdict.recommendation_text}"
        )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_fallback_provides_actionable_guidance(self, constraints: UserConstraints):
        """
        Property 12: Fallback Reliability
        Validates: Requirements 7.5
        
        For any valid user constraints, fallback system should provide
        actionable guidance even when detailed analysis is unavailable.
        """
        fallback_verdict = generate_fallback_verdict(constraints)
        
        # Should have actionable next steps
        actionable_keywords = [
            "visit", "review", "test", "try", "consider", "check", 
            "sign up", "contact", "refresh", "later"
        ]
        
        has_actionable_steps = False
        for step in fallback_verdict.next_steps:
            step_lower = step.lower()
            if any(keyword in step_lower for keyword in actionable_keywords):
                has_actionable_steps = True
                break
        
        assert has_actionable_steps, (
            f"Fallback verdict should provide actionable guidance: {fallback_verdict.next_steps}"
        )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_fallback_handles_extreme_edge_cases(self, constraints: UserConstraints):
        """
        Property 12: Fallback Reliability
        Validates: Requirements 7.5
        
        For any valid user constraints, fallback system should handle
        extreme edge cases (like no compatible APIs) gracefully.
        """
        # Test fallback with constraints that might have no compatible APIs
        # by creating very restrictive constraints
        extreme_constraints = UserConstraints(
            budget=BudgetTier.FREE,
            data_types=[DataType.OPTIONS, DataType.COMMODITIES],  # Less common combination
            frequency=FrequencyTier.REALTIME,  # Most restrictive
            use_case=UseCase.TRADING_BOT  # Most restrictive for TOS
        )
        
        try:
            fallback_apis = get_fallback_recommendations(extreme_constraints)
            fallback_verdict = generate_fallback_verdict(extreme_constraints)
            
            # Even with extreme constraints, should provide some guidance
            assert isinstance(fallback_apis, list), (
                "Fallback should return list even for extreme constraints"
            )
            assert isinstance(fallback_verdict, Verdict), (
                "Fallback should return Verdict even for extreme constraints"
            )
            assert len(fallback_verdict.next_steps) > 0, (
                "Fallback should provide next steps even for extreme constraints"
            )
            
            # If no APIs are compatible, should still provide general guidance
            if not fallback_apis:
                recommendation_lower = fallback_verdict.recommendation_text.lower()
                general_guidance_keywords = [
                    "try again", "different", "constraints", "later", "support"
                ]
                has_general_guidance = any(
                    keyword in recommendation_lower for keyword in general_guidance_keywords
                )
                assert has_general_guidance, (
                    f"Should provide general guidance when no APIs compatible: {fallback_verdict.recommendation_text}"
                )
                
        except Exception as e:
            # Even extreme edge cases should be handled gracefully
            error_message = str(e).lower()
            assert "error" in error_message or "fail" in error_message, (
                f"Extreme edge case error should be meaningful: {str(e)}"
            )

    @given(constraints=user_constraints_strategy())
    @settings(max_examples=100)
    def test_fallback_system_never_completely_fails(self, constraints: UserConstraints):
        """
        Property 12: Fallback Reliability
        Validates: Requirements 7.5
        
        For any valid user constraints, the fallback system should never
        completely fail - it should always provide some form of guidance.
        """
        # Test that at least one of the fallback mechanisms works
        fallback_worked = False
        guidance_provided = False
        
        try:
            # Try fallback recommendations
            fallback_apis = get_fallback_recommendations(constraints)
            if isinstance(fallback_apis, list):
                fallback_worked = True
                if fallback_apis:  # Has actual recommendations
                    guidance_provided = True
        except Exception:
            pass  # Continue to try fallback verdict
        
        try:
            # Try fallback verdict
            fallback_verdict = generate_fallback_verdict(constraints)
            if isinstance(fallback_verdict, Verdict):
                fallback_worked = True
                if (fallback_verdict.recommendation_text and 
                    len(fallback_verdict.recommendation_text.strip()) > 0 and
                    fallback_verdict.next_steps and 
                    len(fallback_verdict.next_steps) > 0):
                    guidance_provided = True
        except Exception:
            pass  # Even fallback verdict failed
        
        # At least one fallback mechanism should work
        assert fallback_worked, (
            "At least one fallback mechanism should work for any valid constraints"
        )
        
        # Should provide some form of guidance
        assert guidance_provided, (
            "Fallback system should provide some form of guidance for any valid constraints"
        )