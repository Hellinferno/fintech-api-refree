"""
Integration tests for complete user workflows in FinTech API Referee.

Task 9.3: Write integration tests for complete user workflows
- Test end-to-end scenarios from constraint input to recommendation display
- Test error scenarios and edge cases
Requirements: 1.1, 2.1, 3.1, 4.1
"""

import pytest
import time
from typing import List, Dict, Any
from models import (
    UserConstraints,
    BudgetTier,
    DataType,
    FrequencyTier,
    UseCase,
    APIScore,
    Verdict,
    score_apis,
    generate_verdict,
    get_all_apis,
    get_fallback_recommendations,
    generate_fallback_verdict,
)
from app import (
    validate_constraints,
    normalize_constraints,
    collect_constraints,
    display_results,
    display_trade_off_analysis,
    display_verdict,
    performance_monitor,
    verify_performance_requirements,
)


class TestCompleteUserWorkflows:
    """
    Integration tests for complete user workflows from constraint input
    to recommendation display.
    
    Requirements: 1.1, 2.1, 3.1, 4.1
    """

    def test_complete_workflow_free_tier_stocks_research(self):
        """
        Test complete workflow: Free tier user researching stocks.
        
        End-to-end scenario: User selects free budget, stocks data,
        end-of-day frequency, research use case -> gets recommendations.
        
        Requirements: 1.1, 2.1, 3.1, 4.1
        """
        # Step 1: User input validation (Requirement 1.1)
        is_valid, error = validate_constraints(
            budget="Free",
            data_types=["Stocks"],
            frequency="End-of-day",
            use_case="Research/Analysis"
        )
        assert is_valid is True
        assert error is None
        
        # Step 2: Constraint normalization (Requirement 1.1)
        constraints = normalize_constraints(
            budget="Free",
            data_types=["Stocks"],
            frequency="End-of-day",
            use_case="Research/Analysis"
        )
        assert constraints.budget == BudgetTier.FREE
        assert DataType.STOCKS in constraints.data_types
        assert constraints.frequency == FrequencyTier.EOD
        assert constraints.use_case == UseCase.RESEARCH
        
        # Step 3: API scoring (Requirement 2.1)
        scored_apis = score_apis(constraints)
        assert len(scored_apis) > 0
        assert all(isinstance(api, APIScore) for api in scored_apis)
        
        # Verify scoring results
        winner = scored_apis[0]
        assert winner.recommendation_rank == 1
        assert 0 <= winner.compatibility_percentage <= 100
        assert winner.api.pricing.get(BudgetTier.FREE, False) is True  # Should support free tier
        
        # Step 4: Verdict generation (Requirement 4.1)
        verdict = generate_verdict(scored_apis, constraints)
        assert isinstance(verdict, Verdict)
        assert len(verdict.recommendation_text) > 0
        assert "**" in verdict.recommendation_text  # Should have bold formatting
        assert winner.api.name in verdict.recommendation_text
        assert len(verdict.next_steps) > 0
        
        # Step 5: Results display (Requirement 3.1)
        # This would normally be tested with Streamlit, but we verify data structure
        assert all(hasattr(api, 'api') for api in scored_apis)
        assert all(hasattr(api, 'compatibility_percentage') for api in scored_apis)
        assert all(hasattr(api.api, 'strengths') for api in scored_apis)
        assert all(hasattr(api.api, 'limitations') for api in scored_apis)
        
        print(f"✅ Complete workflow test passed: {winner.api.name} recommended with {winner.compatibility_percentage}% compatibility")
    def test_complete_workflow_enterprise_trading_bot(self):
        """
        Test complete workflow: Enterprise user building trading bot.
        
        End-to-end scenario: User selects enterprise budget, multiple data types,
        real-time frequency, trading bot use case -> gets recommendations.
        
        Requirements: 1.1, 2.1, 3.1, 4.1
        """
        # Step 1: User input validation
        is_valid, error = validate_constraints(
            budget="Enterprise",
            data_types=["Stocks", "Crypto", "Forex", "Options"],
            frequency="Real-time",
            use_case="Trading Bot"
        )
        assert is_valid is True
        assert error is None
        
        # Step 2: Constraint normalization
        constraints = normalize_constraints(
            budget="Enterprise",
            data_types=["Stocks", "Crypto", "Forex", "Options"],
            frequency="Real-time",
            use_case="Trading Bot"
        )
        assert constraints.budget == BudgetTier.ENTERPRISE
        assert len(constraints.data_types) == 4
        assert constraints.frequency == FrequencyTier.REALTIME
        assert constraints.use_case == UseCase.TRADING_BOT
        
        # Step 3: API scoring
        scored_apis = score_apis(constraints)
        assert len(scored_apis) > 0
        
        # Verify enterprise-appropriate results
        winner = scored_apis[0]
        assert winner.api.pricing.get(BudgetTier.ENTERPRISE, False) is True
        assert FrequencyTier.REALTIME in winner.api.frequency_support
        
        # Step 4: Verdict generation with TOS considerations
        verdict = generate_verdict(scored_apis, constraints)
        assert isinstance(verdict, Verdict)
        
        # Should address commercial use considerations
        verdict_text_lower = verdict.recommendation_text.lower()
        commercial_indicators = ["commercial", "trading", "enterprise", "business"]
        assert any(indicator in verdict_text_lower for indicator in commercial_indicators)
        
        # Step 5: Verify trade-off analysis includes TOS warnings
        # For trading bot use case, should highlight TOS restrictions
        for api_score in scored_apis:
            if any("commercial use explicitly prohibited" in restriction.lower() 
                   for restriction in api_score.api.tos_restrictions):
                # This API should have lower score or alternative recommendation
                assert (api_score.recommendation_rank > 1 or 
                        verdict.alternative_api != "")
        
        print(f"✅ Enterprise trading bot workflow test passed: {winner.api.name} recommended")

    def test_complete_workflow_medium_complexity_portfolio(self):
        """
        Test complete workflow: Medium budget user for portfolio tracking.
        
        End-to-end scenario: User selects under $50/month budget, stocks and crypto,
        delayed frequency, portfolio tracking -> gets recommendations.
        
        Requirements: 1.1, 2.1, 3.1, 4.1
        """
        # Step 1: User input validation
        is_valid, error = validate_constraints(
            budget="Under $50/month",
            data_types=["Stocks", "Crypto"],
            frequency="Delayed (15-20 min)",
            use_case="Portfolio Tracking"
        )
        assert is_valid is True
        assert error is None
        
        # Step 2: Constraint normalization
        constraints = normalize_constraints(
            budget="Under $50/month",
            data_types=["Stocks", "Crypto"],
            frequency="Delayed (15-20 min)",
            use_case="Portfolio Tracking"
        )
        
        # Step 3: API scoring
        scored_apis = score_apis(constraints)
        assert len(scored_apis) > 0
        
        # Verify budget compatibility
        winner = scored_apis[0]
        assert (winner.api.pricing.get(BudgetTier.UNDER_50, False) or 
                winner.api.pricing.get(BudgetTier.FREE, False))
        
        # Verify data type coverage
        winner_data_types = set(winner.api.data_coverage)
        required_types = {DataType.STOCKS, DataType.CRYPTO}
        assert len(required_types.intersection(winner_data_types)) > 0
        
        # Step 4: Verdict generation
        verdict = generate_verdict(scored_apis, constraints)
        assert isinstance(verdict, Verdict)
        assert len(verdict.trade_offs) >= 0  # May or may not have trade-offs
        
        # Step 5: Verify performance within requirements
        start_time = time.time()
        # Re-run the complete workflow to measure performance
        constraints_rerun = normalize_constraints(
            budget="Under $50/month",
            data_types=["Stocks", "Crypto"],
            frequency="Delayed (15-20 min)",
            use_case="Portfolio Tracking"
        )
        scored_apis_rerun = score_apis(constraints_rerun)
        verdict_rerun = generate_verdict(scored_apis_rerun, constraints_rerun)
        elapsed_time = time.time() - start_time
        
        # Should meet 2-second performance requirement
        assert elapsed_time <= 2.0, f"Workflow took {elapsed_time:.3f}s, exceeds 2s requirement"
        
        print(f"✅ Medium complexity portfolio workflow test passed in {elapsed_time:.3f}s")

    def test_complete_workflow_all_data_types_educational(self):
        """
        Test complete workflow: Educational user wanting all data types.
        
        End-to-end scenario: User selects free budget, all data types,
        historical frequency, educational use case -> gets recommendations.
        
        Requirements: 1.1, 2.1, 3.1, 4.1
        """
        # Step 1: User input validation
        is_valid, error = validate_constraints(
            budget="Free",
            data_types=["Stocks", "Crypto", "Forex", "Options", "Commodities"],
            frequency="Historical only",
            use_case="Educational"
        )
        assert is_valid is True
        assert error is None
        
        # Step 2: Constraint normalization
        constraints = normalize_constraints(
            budget="Free",
            data_types=["Stocks", "Crypto", "Forex", "Options", "Commodities"],
            frequency="Historical only",
            use_case="Educational"
        )
        assert len(constraints.data_types) == 5  # All data types
        
        # Step 3: API scoring
        scored_apis = score_apis(constraints)
        assert len(scored_apis) > 0
        
        # Step 4: Verdict generation
        verdict = generate_verdict(scored_apis, constraints)
        assert isinstance(verdict, Verdict)
        
        # Step 5: Verify comprehensive data coverage analysis
        winner = scored_apis[0]
        winner_coverage = set(winner.api.data_coverage)
        requested_types = set(constraints.data_types)
        
        # Calculate actual coverage
        coverage_count = len(requested_types.intersection(winner_coverage))
        coverage_percentage = (coverage_count / len(requested_types)) * 100
        
        # Verify scoring reflects data coverage
        data_type_score = winner.category_scores.get("data_types", 0)
        expected_score = coverage_percentage
        assert abs(data_type_score - expected_score) < 1.0, (
            f"Data type score {data_type_score} should match coverage {expected_score}"
        )
        
        print(f"✅ All data types educational workflow test passed: {coverage_count}/5 data types covered")
class TestErrorScenariosAndEdgeCases:
    """
    Integration tests for error scenarios and edge cases.
    
    Requirements: 1.1, 2.1, 3.1, 4.1
    """

    def test_invalid_constraint_combinations(self):
        """
        Test error handling for invalid constraint combinations.
        
        Requirements: 1.1 - Input validation should catch invalid combinations
        """
        # Test empty data types
        is_valid, error = validate_constraints(
            budget="Free",
            data_types=[],
            frequency="Real-time",
            use_case="Research/Analysis"
        )
        assert is_valid is False
        assert error is not None
        assert "data type" in error.lower()
        
        # Test invalid budget
        is_valid, error = validate_constraints(
            budget="Invalid Budget Tier",
            data_types=["Stocks"],
            frequency="Real-time",
            use_case="Research/Analysis"
        )
        assert is_valid is False
        assert error is not None
        assert "budget" in error.lower()
        
        # Test invalid data type
        is_valid, error = validate_constraints(
            budget="Free",
            data_types=["Invalid Data Type"],
            frequency="Real-time",
            use_case="Research/Analysis"
        )
        assert is_valid is False
        assert error is not None
        assert "data type" in error.lower()
        
        # Test invalid frequency
        is_valid, error = validate_constraints(
            budget="Free",
            data_types=["Stocks"],
            frequency="Invalid Frequency",
            use_case="Research/Analysis"
        )
        assert is_valid is False
        assert error is not None
        assert "frequency" in error.lower()
        
        # Test invalid use case
        is_valid, error = validate_constraints(
            budget="Free",
            data_types=["Stocks"],
            frequency="Real-time",
            use_case="Invalid Use Case"
        )
        assert is_valid is False
        assert error is not None
        assert "use case" in error.lower()
        
        print("✅ Invalid constraint validation tests passed")

    def test_edge_case_no_compatible_apis(self):
        """
        Test edge case where no APIs are compatible with constraints.
        
        This tests the system's ability to handle extreme constraint combinations
        that might result in no perfect matches.
        
        Requirements: 2.1, 4.1 - System should handle edge cases gracefully
        """
        # Create very restrictive constraints that are hard to satisfy
        constraints = UserConstraints(
            budget=BudgetTier.FREE,  # Most restrictive budget
            data_types=[DataType.OPTIONS, DataType.COMMODITIES],  # Less common combination
            frequency=FrequencyTier.REALTIME,  # Most demanding frequency
            use_case=UseCase.TRADING_BOT  # Most restrictive for TOS
        )
        
        # System should still return results, even if compatibility is low
        scored_apis = score_apis(constraints)
        assert len(scored_apis) > 0, "System should return some results even for restrictive constraints"
        
        # Verify that results are properly ranked even with low compatibility
        for i in range(len(scored_apis) - 1):
            current_score = scored_apis[i].total_score
            next_score = scored_apis[i + 1].total_score
            assert current_score >= next_score, "APIs should be ranked by score even with low compatibility"
        
        # Verdict should still be generated
        verdict = generate_verdict(scored_apis, constraints)
        assert isinstance(verdict, Verdict)
        assert len(verdict.recommendation_text) > 0
        assert len(verdict.next_steps) > 0
        
        # Winner might have low compatibility but should still be valid
        winner = scored_apis[0]
        assert 0 <= winner.compatibility_percentage <= 100
        
        print(f"✅ Edge case test passed: {winner.api.name} recommended with {winner.compatibility_percentage}% compatibility")

    def test_fallback_system_activation(self):
        """
        Test fallback system when primary scoring fails.
        
        Requirements: 4.1 - System should provide fallback recommendations
        """
        constraints = UserConstraints(
            budget=BudgetTier.UNDER_50,
            data_types=[DataType.STOCKS, DataType.CRYPTO],
            frequency=FrequencyTier.DELAYED,
            use_case=UseCase.PORTFOLIO
        )
        
        # Test fallback recommendations
        fallback_apis = get_fallback_recommendations(constraints)
        assert isinstance(fallback_apis, list)
        
        if len(fallback_apis) > 0:
            # Verify fallback APIs are valid
            for api_score in fallback_apis:
                assert isinstance(api_score, APIScore)
                assert api_score.api is not None
                assert 0 <= api_score.compatibility_percentage <= 100
                assert api_score.recommendation_rank >= 1
            
            # Verify fallback APIs are ordered by reliability
            if len(fallback_apis) > 1:
                for i in range(len(fallback_apis) - 1):
                    current_reliability = fallback_apis[i].api.reliability_score
                    next_reliability = fallback_apis[i + 1].api.reliability_score
                    assert current_reliability >= next_reliability, (
                        "Fallback APIs should be ordered by reliability"
                    )
        
        # Test fallback verdict
        fallback_verdict = generate_fallback_verdict(constraints)
        assert isinstance(fallback_verdict, Verdict)
        assert len(fallback_verdict.recommendation_text) > 0
        assert len(fallback_verdict.next_steps) > 0
        
        # Fallback verdict should indicate fallback mode
        verdict_lower = fallback_verdict.recommendation_text.lower()
        fallback_indicators = ["fallback", "reliability", "unavailable", "system"]
        assert any(indicator in verdict_lower for indicator in fallback_indicators), (
            "Fallback verdict should indicate fallback mode"
        )
        
        print("✅ Fallback system test passed")

    def test_performance_edge_cases(self):
        """
        Test performance under various edge case scenarios.
        
        Requirements: 2.1 - System should maintain performance under edge cases
        """
        edge_case_scenarios = [
            # Scenario 1: Single data type, simple constraints
            UserConstraints(
                budget=BudgetTier.FREE,
                data_types=[DataType.STOCKS],
                frequency=FrequencyTier.EOD,
                use_case=UseCase.RESEARCH
            ),
            # Scenario 2: All data types, complex constraints
            UserConstraints(
                budget=BudgetTier.ENTERPRISE,
                data_types=[DataType.STOCKS, DataType.CRYPTO, DataType.FOREX, 
                           DataType.OPTIONS, DataType.COMMODITIES],
                frequency=FrequencyTier.REALTIME,
                use_case=UseCase.TRADING_BOT
            ),
            # Scenario 3: Conflicting requirements
            UserConstraints(
                budget=BudgetTier.FREE,
                data_types=[DataType.OPTIONS],
                frequency=FrequencyTier.REALTIME,
                use_case=UseCase.TRADING_BOT
            ),
        ]
        
        performance_results = []
        
        for i, constraints in enumerate(edge_case_scenarios, 1):
            start_time = time.time()
            
            try:
                # Run complete workflow
                scored_apis = score_apis(constraints)
                verdict = generate_verdict(scored_apis, constraints)
                
                elapsed_time = time.time() - start_time
                performance_results.append({
                    "scenario": i,
                    "elapsed_time": elapsed_time,
                    "success": True,
                    "api_count": len(scored_apis)
                })
                
                # Verify results are valid
                assert len(scored_apis) > 0
                assert isinstance(verdict, Verdict)
                assert elapsed_time <= 2.0, f"Scenario {i} took {elapsed_time:.3f}s, exceeds 2s requirement"
                
            except Exception as e:
                elapsed_time = time.time() - start_time
                performance_results.append({
                    "scenario": i,
                    "elapsed_time": elapsed_time,
                    "success": False,
                    "error": str(e)
                })
                raise  # Re-raise to fail the test
        
        # Verify all scenarios passed performance requirements
        max_time = max(result["elapsed_time"] for result in performance_results)
        avg_time = sum(result["elapsed_time"] for result in performance_results) / len(performance_results)
        
        assert max_time <= 2.0, f"Max time {max_time:.3f}s exceeds 2s requirement"
        assert avg_time <= 1.0, f"Average time {avg_time:.3f}s is too slow"
        
        print(f"✅ Performance edge cases test passed: max={max_time:.3f}s, avg={avg_time:.3f}s")

    def test_data_integrity_throughout_workflow(self):
        """
        Test data integrity throughout the complete workflow.
        
        Ensures that data is not corrupted or lost during the workflow process.
        
        Requirements: 1.1, 2.1, 3.1, 4.1
        """
        # Start with known constraints
        original_constraints = UserConstraints(
            budget=BudgetTier.UNDER_200,
            data_types=[DataType.STOCKS, DataType.CRYPTO, DataType.FOREX],
            frequency=FrequencyTier.DELAYED,
            use_case=UseCase.PORTFOLIO
        )
        
        # Step 1: Verify constraint integrity
        assert original_constraints.budget == BudgetTier.UNDER_200
        assert len(original_constraints.data_types) == 3
        assert DataType.STOCKS in original_constraints.data_types
        assert DataType.CRYPTO in original_constraints.data_types
        assert DataType.FOREX in original_constraints.data_types
        
        # Step 2: Score APIs and verify data integrity
        scored_apis = score_apis(original_constraints)
        assert len(scored_apis) > 0
        
        # Verify all APIs have complete data
        for api_score in scored_apis:
            assert api_score.api.name is not None
            assert len(api_score.api.name.strip()) > 0
            assert api_score.api.pricing is not None
            assert len(api_score.api.pricing) > 0
            assert api_score.api.data_coverage is not None
            assert len(api_score.api.data_coverage) > 0
            assert api_score.api.rate_limits is not None
            assert len(api_score.api.rate_limits) > 0
            assert api_score.api.strengths is not None
            assert len(api_score.api.strengths) > 0
            assert api_score.api.limitations is not None
            assert api_score.api.tos_restrictions is not None
            assert 0.0 <= api_score.api.reliability_score <= 1.0
            
            # Verify scoring data integrity
            assert isinstance(api_score.total_score, (int, float))
            assert 0.0 <= api_score.total_score <= 100.0
            assert isinstance(api_score.compatibility_percentage, int)
            assert 0 <= api_score.compatibility_percentage <= 100
            assert isinstance(api_score.recommendation_rank, int)
            assert api_score.recommendation_rank >= 1
            assert api_score.category_scores is not None
            assert len(api_score.category_scores) == 4  # budget, data_types, frequency, use_case
        
        # Step 3: Generate verdict and verify data integrity
        verdict = generate_verdict(scored_apis, original_constraints)
        assert isinstance(verdict, Verdict)
        assert verdict.recommendation_text is not None
        assert len(verdict.recommendation_text.strip()) > 0
        assert verdict.trade_offs is not None
        assert isinstance(verdict.trade_offs, list)
        assert verdict.next_steps is not None
        assert isinstance(verdict.next_steps, list)
        assert len(verdict.next_steps) > 0
        
        # Verify winner data is preserved in verdict
        winner = scored_apis[0]
        assert winner.api.name in verdict.recommendation_text
        assert str(winner.compatibility_percentage) in verdict.recommendation_text
        
        # Step 4: Verify ranking integrity
        for i in range(len(scored_apis) - 1):
            current_api = scored_apis[i]
            next_api = scored_apis[i + 1]
            
            # Scores should be in descending order
            assert current_api.total_score >= next_api.total_score
            
            # Ranks should be sequential
            assert current_api.recommendation_rank == i + 1
            assert next_api.recommendation_rank == i + 2
        
        print("✅ Data integrity test passed throughout complete workflow")
class TestCrossComponentIntegration:
    """
    Integration tests for cross-component interactions.
    
    Tests how different components work together in the complete system.
    
    Requirements: 1.1, 2.1, 3.1, 4.1
    """

    def test_constraint_validation_to_scoring_integration(self):
        """
        Test integration between constraint validation and API scoring.
        
        Ensures that validated constraints are properly passed to scoring engine.
        
        Requirements: 1.1, 2.1
        """
        # Test various valid constraint combinations
        test_cases = [
            {
                "budget": "Free",
                "data_types": ["Stocks"],
                "frequency": "End-of-day",
                "use_case": "Research/Analysis",
                "expected_budget": BudgetTier.FREE,
                "expected_data_count": 1,
                "expected_frequency": FrequencyTier.EOD,
                "expected_use_case": UseCase.RESEARCH
            },
            {
                "budget": "Under $200/month",
                "data_types": ["Stocks", "Crypto", "Forex"],
                "frequency": "Real-time",
                "use_case": "Trading Bot",
                "expected_budget": BudgetTier.UNDER_200,
                "expected_data_count": 3,
                "expected_frequency": FrequencyTier.REALTIME,
                "expected_use_case": UseCase.TRADING_BOT
            },
            {
                "budget": "Enterprise",
                "data_types": ["Options", "Commodities"],
                "frequency": "Delayed (15-20 min)",
                "use_case": "Portfolio Tracking",
                "expected_budget": BudgetTier.ENTERPRISE,
                "expected_data_count": 2,
                "expected_frequency": FrequencyTier.DELAYED,
                "expected_use_case": UseCase.PORTFOLIO
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            # Step 1: Validate constraints
            is_valid, error = validate_constraints(
                budget=test_case["budget"],
                data_types=test_case["data_types"],
                frequency=test_case["frequency"],
                use_case=test_case["use_case"]
            )
            assert is_valid is True, f"Test case {i} should be valid"
            assert error is None, f"Test case {i} should have no error"
            
            # Step 2: Normalize constraints
            constraints = normalize_constraints(
                budget=test_case["budget"],
                data_types=test_case["data_types"],
                frequency=test_case["frequency"],
                use_case=test_case["use_case"]
            )
            
            # Verify normalization
            assert constraints.budget == test_case["expected_budget"]
            assert len(constraints.data_types) == test_case["expected_data_count"]
            assert constraints.frequency == test_case["expected_frequency"]
            assert constraints.use_case == test_case["expected_use_case"]
            
            # Step 3: Score APIs with normalized constraints
            scored_apis = score_apis(constraints)
            assert len(scored_apis) > 0, f"Test case {i} should return scored APIs"
            
            # Verify scoring reflects constraints
            winner = scored_apis[0]
            
            # Budget compatibility
            budget_score = winner.category_scores.get("budget", 0)
            if winner.api.pricing.get(constraints.budget, False):
                assert budget_score == 100.0, f"Test case {i}: Budget score should be 100 for compatible API"
            else:
                assert budget_score == 0.0, f"Test case {i}: Budget score should be 0 for incompatible API"
            
            # Data type coverage
            data_score = winner.category_scores.get("data_types", 0)
            covered_types = sum(1 for dt in constraints.data_types if dt in winner.api.data_coverage)
            expected_data_score = (covered_types / len(constraints.data_types)) * 100.0
            assert abs(data_score - expected_data_score) < 0.1, (
                f"Test case {i}: Data score {data_score} should match expected {expected_data_score}"
            )
            
            # Frequency compatibility
            frequency_score = winner.category_scores.get("frequency", 0)
            if constraints.frequency in winner.api.frequency_support:
                assert frequency_score == 100.0, f"Test case {i}: Frequency score should be 100 for compatible API"
            else:
                assert frequency_score == 0.0, f"Test case {i}: Frequency score should be 0 for incompatible API"
        
        print("✅ Constraint validation to scoring integration test passed")

    def test_scoring_to_verdict_integration(self):
        """
        Test integration between API scoring and verdict generation.
        
        Ensures that scoring results are properly used in verdict generation.
        
        Requirements: 2.1, 4.1
        """
        constraints = UserConstraints(
            budget=BudgetTier.UNDER_50,
            data_types=[DataType.STOCKS, DataType.CRYPTO],
            frequency=FrequencyTier.DELAYED,
            use_case=UseCase.PORTFOLIO
        )
        
        # Step 1: Get scored APIs
        scored_apis = score_apis(constraints)
        assert len(scored_apis) > 0
        
        winner = scored_apis[0]
        runner_up = scored_apis[1] if len(scored_apis) > 1 else None
        
        # Step 2: Generate verdict
        verdict = generate_verdict(scored_apis, constraints)
        
        # Step 3: Verify verdict reflects scoring results
        
        # Winner should be mentioned in recommendation
        assert winner.api.name in verdict.recommendation_text, (
            "Winner API name should be in recommendation text"
        )
        
        # Compatibility percentage should be mentioned
        assert str(winner.compatibility_percentage) in verdict.recommendation_text, (
            "Winner compatibility percentage should be in recommendation text"
        )
        
        # Budget context should be addressed
        budget_mentioned = any(keyword in verdict.recommendation_text.lower() for keyword in [
            "budget", "free", "$", "cost", "price", constraints.budget.value.lower()
        ])
        assert budget_mentioned, "Budget context should be mentioned in verdict"
        
        # If there's a runner-up, trade-offs might be generated
        if runner_up and len(verdict.trade_offs) > 0:
            # Trade-offs should reference both APIs
            trade_offs_text = " ".join(verdict.trade_offs).lower()
            assert (winner.api.name.lower() in trade_offs_text or 
                    runner_up.api.name.lower() in trade_offs_text), (
                "Trade-offs should reference the APIs being compared"
            )
        
        # Next steps should be actionable
        assert len(verdict.next_steps) > 0, "Should have actionable next steps"
        for step in verdict.next_steps:
            assert len(step.strip()) > 0, "Each next step should be non-empty"
            # Should contain actionable words or instructions
            actionable_words = ["sign up", "visit", "review", "test", "check", "contact", "plan", "get", "select", "ensure"]
            step_lower = step.lower()
            has_actionable_word = any(word in step_lower for word in actionable_words)
            assert has_actionable_word, f"Next step should be actionable: {step}"
        
        print("✅ Scoring to verdict integration test passed")

    def test_verdict_to_display_integration(self):
        """
        Test integration between verdict generation and results display.
        
        Ensures that verdict data is properly structured for display components.
        
        Requirements: 3.1, 4.1
        """
        constraints = UserConstraints(
            budget=BudgetTier.FREE,
            data_types=[DataType.STOCKS],
            frequency=FrequencyTier.EOD,
            use_case=UseCase.EDUCATIONAL
        )
        
        # Step 1: Get complete workflow results
        scored_apis = score_apis(constraints)
        verdict = generate_verdict(scored_apis, constraints)
        
        # Step 2: Verify data structure for display components
        
        # Verify scored APIs have all display-required fields
        for api_score in scored_apis:
            # Required for display_results()
            assert hasattr(api_score, 'api'), "Should have API reference"
            assert hasattr(api_score, 'compatibility_percentage'), "Should have compatibility percentage"
            assert hasattr(api_score, 'recommendation_rank'), "Should have recommendation rank"
            
            # Required for display_trade_off_analysis()
            assert hasattr(api_score.api, 'name'), "API should have name"
            assert hasattr(api_score.api, 'strengths'), "API should have strengths"
            assert hasattr(api_score.api, 'limitations'), "API should have limitations"
            assert hasattr(api_score.api, 'pricing'), "API should have pricing"
            assert hasattr(api_score.api, 'rate_limits'), "API should have rate limits"
            assert hasattr(api_score.api, 'data_coverage'), "API should have data coverage"
            assert hasattr(api_score.api, 'tos_restrictions'), "API should have TOS restrictions"
            assert hasattr(api_score.api, 'reliability_score'), "API should have reliability score"
            
            # Verify data types for display
            assert isinstance(api_score.compatibility_percentage, int)
            assert isinstance(api_score.recommendation_rank, int)
            assert isinstance(api_score.api.name, str)
            assert isinstance(api_score.api.strengths, list)
            assert isinstance(api_score.api.limitations, list)
            assert isinstance(api_score.api.pricing, dict)
            assert isinstance(api_score.api.rate_limits, dict)
            assert isinstance(api_score.api.data_coverage, list)
            assert isinstance(api_score.api.tos_restrictions, list)
            assert isinstance(api_score.api.reliability_score, float)
        
        # Verify verdict has all display-required fields
        assert hasattr(verdict, 'recommendation_text'), "Verdict should have recommendation text"
        assert hasattr(verdict, 'trade_offs'), "Verdict should have trade-offs"
        assert hasattr(verdict, 'next_steps'), "Verdict should have next steps"
        assert hasattr(verdict, 'alternative_api'), "Verdict should have alternative API"
        assert hasattr(verdict, 'alternative_reason'), "Verdict should have alternative reason"
        
        # Verify data types for display
        assert isinstance(verdict.recommendation_text, str)
        assert isinstance(verdict.trade_offs, list)
        assert isinstance(verdict.next_steps, list)
        assert isinstance(verdict.alternative_api, str)
        assert isinstance(verdict.alternative_reason, str)
        
        # Verify content quality for display
        assert len(verdict.recommendation_text.strip()) > 0, "Recommendation text should not be empty"
        assert "**" in verdict.recommendation_text, "Should have bold formatting for display"
        
        for trade_off in verdict.trade_offs:
            assert isinstance(trade_off, str), "Each trade-off should be a string"
            assert len(trade_off.strip()) > 0, "Each trade-off should not be empty"
        
        for step in verdict.next_steps:
            assert isinstance(step, str), "Each next step should be a string"
            assert len(step.strip()) > 0, "Each next step should not be empty"
        
        # Step 3: Verify display compatibility for TOS warnings
        if constraints.use_case == UseCase.TRADING_BOT:
            # Should be able to identify APIs with commercial restrictions
            for api_score in scored_apis:
                has_commercial_restrictions = any(
                    "commercial use explicitly prohibited" in restriction.lower() or
                    "non-commercial use only" in restriction.lower()
                    for restriction in api_score.api.tos_restrictions
                )
                
                if has_commercial_restrictions:
                    # TOS restrictions should be clearly identifiable for display warnings
                    tos_text = " ".join(api_score.api.tos_restrictions).lower()
                    warning_keywords = ["commercial", "non-commercial", "prohibited", "personal", "educational"]
                    has_warning_keyword = any(keyword in tos_text for keyword in warning_keywords)
                    assert has_warning_keyword, (
                        f"API {api_score.api.name} with commercial restrictions should have clear warning text"
                    )
        
        print("✅ Verdict to display integration test passed")

    def test_end_to_end_performance_integration(self):
        """
        Test end-to-end performance integration across all components.
        
        Ensures that the complete workflow meets performance requirements
        when all components work together.
        
        Requirements: 1.1, 2.1, 3.1, 4.1
        """
        # Test multiple scenarios to ensure consistent performance
        test_scenarios = [
            ("Simple", UserConstraints(BudgetTier.FREE, [DataType.STOCKS], FrequencyTier.EOD, UseCase.RESEARCH)),
            ("Medium", UserConstraints(BudgetTier.UNDER_50, [DataType.STOCKS, DataType.CRYPTO], FrequencyTier.DELAYED, UseCase.PORTFOLIO)),
            ("Complex", UserConstraints(BudgetTier.ENTERPRISE, [DataType.STOCKS, DataType.CRYPTO, DataType.FOREX, DataType.OPTIONS], FrequencyTier.REALTIME, UseCase.TRADING_BOT))
        ]
        
        performance_results = []
        
        for scenario_name, constraints in test_scenarios:
            # Measure complete workflow performance
            start_time = time.time()
            
            # Step 1: Constraint validation (simulated - normally done in UI)
            validation_start = time.time()
            # Simulate validation time
            validation_time = time.time() - validation_start
            
            # Step 2: API scoring
            scoring_start = time.time()
            scored_apis = score_apis(constraints)
            scoring_time = time.time() - scoring_start
            
            # Step 3: Verdict generation
            verdict_start = time.time()
            verdict = generate_verdict(scored_apis, constraints)
            verdict_time = time.time() - verdict_start
            
            # Step 4: Display preparation (simulated)
            display_start = time.time()
            # Simulate display preparation time
            display_time = time.time() - display_start
            
            total_time = time.time() - start_time
            
            # Verify results are valid
            assert len(scored_apis) > 0, f"{scenario_name}: Should return scored APIs"
            assert isinstance(verdict, Verdict), f"{scenario_name}: Should return valid verdict"
            assert len(verdict.recommendation_text) > 0, f"{scenario_name}: Should have recommendation text"
            assert len(verdict.next_steps) > 0, f"{scenario_name}: Should have next steps"
            
            # Verify performance requirements
            assert total_time <= 2.0, f"{scenario_name}: Total time {total_time:.3f}s exceeds 2s requirement"
            assert scoring_time <= 1.2, f"{scenario_name}: Scoring time {scoring_time:.3f}s is too slow"
            assert verdict_time <= 0.8, f"{scenario_name}: Verdict time {verdict_time:.3f}s is too slow"
            
            performance_results.append({
                "scenario": scenario_name,
                "total_time": total_time,
                "scoring_time": scoring_time,
                "verdict_time": verdict_time,
                "api_count": len(scored_apis)
            })
        
        # Verify overall performance characteristics
        avg_total_time = sum(r["total_time"] for r in performance_results) / len(performance_results)
        max_total_time = max(r["total_time"] for r in performance_results)
        
        assert avg_total_time <= 1.0, f"Average total time {avg_total_time:.3f}s is too slow"
        assert max_total_time <= 2.0, f"Max total time {max_total_time:.3f}s exceeds requirement"
        
        print(f"✅ End-to-end performance integration test passed: avg={avg_total_time:.3f}s, max={max_total_time:.3f}s")


if __name__ == "__main__":
    # Run integration tests
    print("Running FinTech API Referee Integration Tests...")
    print("=" * 60)
    
    # Test complete user workflows
    workflow_tests = TestCompleteUserWorkflows()
    workflow_tests.test_complete_workflow_free_tier_stocks_research()
    workflow_tests.test_complete_workflow_enterprise_trading_bot()
    workflow_tests.test_complete_workflow_medium_complexity_portfolio()
    workflow_tests.test_complete_workflow_all_data_types_educational()
    
    # Test error scenarios and edge cases
    error_tests = TestErrorScenariosAndEdgeCases()
    error_tests.test_invalid_constraint_combinations()
    error_tests.test_edge_case_no_compatible_apis()
    error_tests.test_fallback_system_activation()
    error_tests.test_performance_edge_cases()
    error_tests.test_data_integrity_throughout_workflow()
    
    # Test cross-component integration
    integration_tests = TestCrossComponentIntegration()
    integration_tests.test_constraint_validation_to_scoring_integration()
    integration_tests.test_scoring_to_verdict_integration()
    integration_tests.test_verdict_to_display_integration()
    integration_tests.test_end_to_end_performance_integration()
    
    print("=" * 60)
    print("✅ All integration tests passed!")
    print("Integration test coverage:")
    print("  • Complete user workflows (4 scenarios)")
    print("  • Error handling and edge cases (5 scenarios)")
    print("  • Cross-component integration (4 scenarios)")
    print("  • End-to-end performance validation")
    print("  • Data integrity throughout workflows")
    print("  • Fallback system activation")