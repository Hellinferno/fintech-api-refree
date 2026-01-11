"""
FinTech API Referee - Main Streamlit Application

A decision-support tool that helps developers and traders choose
the optimal financial data API for their specific use case.
"""

import streamlit as st
import logging
import time
from typing import Optional, Tuple, List, Dict, Any
from contextlib import contextmanager
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
)

# Configure logging for error handling
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Performance monitoring constants - Requirements 7.1, 7.3
PERFORMANCE_TARGET_SECONDS = 2.0
PERFORMANCE_WARNING_SECONDS = 1.5


@contextmanager
def performance_monitor(operation_name: str, target_seconds: float = PERFORMANCE_TARGET_SECONDS):
    """
    Context manager for monitoring operation performance against requirements.
    
    Args:
        operation_name: Name of the operation being monitored
        target_seconds: Target completion time in seconds
        
    Yields:
        Dictionary containing timing information that gets updated during execution
        
    Requirements: 7.1, 7.3
    """
    timing_info = {"start_time": time.time(), "operation": operation_name}
    
    try:
        logger.info(f"Starting {operation_name}")
        yield timing_info
        
    finally:
        end_time = time.time()
        elapsed = end_time - timing_info["start_time"]
        timing_info["elapsed_seconds"] = elapsed
        timing_info["target_seconds"] = target_seconds
        timing_info["within_target"] = elapsed <= target_seconds
        
        # Log performance results
        if elapsed > target_seconds:
            logger.warning(f"PERFORMANCE VIOLATION: {operation_name} took {elapsed:.3f}s (target: {target_seconds:.1f}s)")
        elif elapsed > target_seconds * 0.75:  # 75% of target
            logger.info(f"Performance acceptable: {operation_name} took {elapsed:.3f}s (target: {target_seconds:.1f}s)")
        else:
            logger.debug(f"Performance excellent: {operation_name} took {elapsed:.3f}s (target: {target_seconds:.1f}s)")


def display_performance_feedback(timing_info: Dict[str, Any]) -> None:
    """
    Display performance feedback to users based on timing information.
    
    Args:
        timing_info: Dictionary containing timing and performance data
        
    Requirements: 7.1, 7.3
    """
    elapsed = timing_info.get("elapsed_seconds", 0)
    target = timing_info.get("target_seconds", PERFORMANCE_TARGET_SECONDS)
    operation = timing_info.get("operation", "operation")
    
    if elapsed > target:
        st.error(f"⚠️ **Performance Issue**: {operation} took {elapsed:.2f} seconds (exceeds {target:.1f}s requirement)")
    elif elapsed > target * 0.75:
        st.info(f"⏱️ {operation.title()} completed in {elapsed:.2f} seconds")
    else:
        # Only show timing for fast operations in debug mode to avoid UI clutter
        if logger.isEnabledFor(logging.DEBUG):
            st.success(f"✅ Fast {operation} completed in {elapsed:.2f} seconds")


def verify_performance_requirements() -> Dict[str, Any]:
    """
    Verify that the system meets performance requirements by running test scenarios.
    
    Returns:
        Dictionary containing performance test results
        
    Requirements: 7.1, 7.3
    """
    logger.info("Starting performance requirement verification")
    
    # Test scenarios with different constraint combinations
    test_scenarios = [
        # Scenario 1: Simple constraints
        UserConstraints(
            budget=BudgetTier.FREE,
            data_types=[DataType.STOCKS],
            frequency=FrequencyTier.EOD,
            use_case=UseCase.RESEARCH
        ),
        # Scenario 2: Complex constraints
        UserConstraints(
            budget=BudgetTier.ENTERPRISE,
            data_types=[DataType.STOCKS, DataType.CRYPTO, DataType.FOREX],
            frequency=FrequencyTier.REALTIME,
            use_case=UseCase.TRADING_BOT
        ),
        # Scenario 3: Medium complexity
        UserConstraints(
            budget=BudgetTier.UNDER_50,
            data_types=[DataType.STOCKS, DataType.CRYPTO],
            frequency=FrequencyTier.DELAYED,
            use_case=UseCase.PORTFOLIO
        ),
    ]
    
    results = {
        "total_tests": len(test_scenarios),
        "passed_tests": 0,
        "failed_tests": 0,
        "test_results": [],
        "max_time": 0.0,
        "min_time": float('inf'),
        "avg_time": 0.0,
    }
    
    total_time = 0.0
    
    for i, constraints in enumerate(test_scenarios, 1):
        logger.info(f"Running performance test scenario {i}/{len(test_scenarios)}")
        
        try:
            with performance_monitor(f"test scenario {i}", PERFORMANCE_TARGET_SECONDS) as timing:
                # Run the complete recommendation process
                scored_apis = score_apis(constraints)
                verdict = generate_verdict(scored_apis, constraints)
            
            elapsed = timing["elapsed_seconds"]
            within_target = timing["within_target"]
            
            test_result = {
                "scenario": i,
                "elapsed_seconds": elapsed,
                "within_target": within_target,
                "constraints": {
                    "budget": constraints.budget.value,
                    "data_types": [dt.value for dt in constraints.data_types],
                    "frequency": constraints.frequency.value,
                    "use_case": constraints.use_case.value,
                },
                "api_count": len(scored_apis) if scored_apis else 0,
            }
            
            results["test_results"].append(test_result)
            total_time += elapsed
            results["max_time"] = max(results["max_time"], elapsed)
            results["min_time"] = min(results["min_time"], elapsed)
            
            if within_target:
                results["passed_tests"] += 1
                logger.info(f"✅ Test scenario {i} passed: {elapsed:.3f}s <= {PERFORMANCE_TARGET_SECONDS}s")
            else:
                results["failed_tests"] += 1
                logger.warning(f"❌ Test scenario {i} failed: {elapsed:.3f}s > {PERFORMANCE_TARGET_SECONDS}s")
                
        except Exception as e:
            logger.error(f"Error in performance test scenario {i}: {str(e)}", exc_info=True)
            results["failed_tests"] += 1
            results["test_results"].append({
                "scenario": i,
                "elapsed_seconds": None,
                "within_target": False,
                "error": str(e),
                "constraints": {
                    "budget": constraints.budget.value,
                    "data_types": [dt.value for dt in constraints.data_types],
                    "frequency": constraints.frequency.value,
                    "use_case": constraints.use_case.value,
                }
            })
    
    # Calculate average time
    if results["passed_tests"] + results["failed_tests"] > 0:
        results["avg_time"] = total_time / len(test_scenarios)
    
    # Overall assessment
    pass_rate = results["passed_tests"] / results["total_tests"] * 100
    results["pass_rate"] = pass_rate
    results["meets_requirements"] = pass_rate >= 90  # 90% pass rate threshold
    
    logger.info(f"Performance verification complete: {results['passed_tests']}/{results['total_tests']} tests passed "
               f"({pass_rate:.1f}% pass rate)")
    logger.info(f"Timing summary: min={results['min_time']:.3f}s, max={results['max_time']:.3f}s, "
               f"avg={results['avg_time']:.3f}s")
    
    return results


def validate_data_types(data_types: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate that at least one data type is selected.
    
    Args:
        data_types: List of selected data type values
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Requirements: 1.3
    """
    if not data_types:
        return False, "Please select at least one data type."
    return True, None


def validate_constraints(
    budget: str,
    data_types: List[str],
    frequency: str,
    use_case: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate all user constraints for completeness and correctness.
    
    Args:
        budget: Selected budget tier value
        data_types: List of selected data type values
        frequency: Selected frequency tier value
        use_case: Selected use case value
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
    """
    # Validate budget
    valid_budgets = [tier.value for tier in BudgetTier]
    if budget not in valid_budgets:
        return False, f"Invalid budget selection: {budget}"
    
    # Validate data types
    is_valid, error = validate_data_types(data_types)
    if not is_valid:
        return False, error
    
    valid_data_types = [dt.value for dt in DataType]
    for dt in data_types:
        if dt not in valid_data_types:
            return False, f"Invalid data type: {dt}"
    
    # Validate frequency
    valid_frequencies = [freq.value for freq in FrequencyTier]
    if frequency not in valid_frequencies:
        return False, f"Invalid frequency selection: {frequency}"
    
    # Validate use case
    valid_use_cases = [uc.value for uc in UseCase]
    if use_case not in valid_use_cases:
        return False, f"Invalid use case: {use_case}"
    
    return True, None


def normalize_constraints(
    budget: str,
    data_types: List[str],
    frequency: str,
    use_case: str
) -> UserConstraints:
    """
    Normalize and convert raw form values to UserConstraints object.
    
    Args:
        budget: Selected budget tier value
        data_types: List of selected data type values
        frequency: Selected frequency tier value
        use_case: Selected use case value
        
    Returns:
        Normalized UserConstraints object
        
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
    """
    return UserConstraints(
        budget=BudgetTier(budget),
        data_types=[DataType(dt) for dt in data_types],
        frequency=FrequencyTier(frequency),
        use_case=UseCase(use_case),
    )


def collect_constraints() -> Tuple[Optional[UserConstraints], bool, Optional[str]]:
    """
    Collects user constraints from sidebar form with validation.
    
    Returns:
        Tuple of (constraints, is_valid, error_message)
        - constraints: UserConstraints object if valid, None otherwise
        - is_valid: Whether the constraints are valid
        - error_message: Error message if invalid, None otherwise
        
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 6.3
    """
    with st.sidebar:
        st.header("Your Requirements")
        
        # Budget selection - Requirement 1.2
        budget = st.selectbox(
            "💰 Budget",
            options=[tier.value for tier in BudgetTier],
            help="Select your monthly budget for API costs",
            key="budget_selector",
        )
        
        # Data type selection - Requirement 1.3
        data_types = st.multiselect(
            "📈 Data Types",
            options=[dt.value for dt in DataType],
            default=[DataType.STOCKS.value],
            help="Select the types of financial data you need",
            key="data_types_selector",
        )
        
        # Frequency selection - Requirement 1.4
        frequency = st.selectbox(
            "⏱️ Data Frequency",
            options=[freq.value for freq in FrequencyTier],
            help="How often do you need data updates?",
            key="frequency_selector",
        )
        
        # Use case selection - Requirement 1.5
        use_case = st.selectbox(
            "🎯 Use Case",
            options=[uc.value for uc in UseCase],
            help="What will you use the data for?",
            key="use_case_selector",
        )
        
        st.markdown("---")
        
        # Submit button
        analyze_clicked = st.button(
            "🔍 Find Best APIs",
            type="primary",
            use_container_width=True,
        )
        
        # Immediate feedback on constraint updates - Requirement 6.3
        st.markdown("---")
        st.markdown("##### Current Selection")
        
        # Show current constraint summary
        st.markdown(f"**Budget:** {budget}")
        
        if data_types:
            st.markdown(f"**Data:** {', '.join(data_types)}")
        else:
            st.markdown("**Data:** ⚠️ *None selected*")
        
        st.markdown(f"**Frequency:** {frequency}")
        st.markdown(f"**Use Case:** {use_case}")
    
    # Validate constraints
    is_valid, error = validate_constraints(budget, data_types, frequency, use_case)
    
    if is_valid:
        constraints = normalize_constraints(budget, data_types, frequency, use_case)
        return constraints, analyze_clicked, None
    else:
        return None, analyze_clicked, error


def display_constraint_summary(constraints: UserConstraints) -> None:
    """
    Display a summary of the user's selected constraints.
    
    Args:
        constraints: The validated user constraints
        
    Requirements: 6.3
    """
    st.info(
        f"🔍 **Analyzing APIs for your requirements:**\n\n"
        f"• **Budget:** {constraints.budget.value}\n"
        f"• **Data Types:** {', '.join(dt.value for dt in constraints.data_types)}\n"
        f"• **Frequency:** {constraints.frequency.value}\n"
        f"• **Use Case:** {constraints.use_case.value}"
    )


def display_results(scored_apis: List['APIScore']) -> None:
    """
    Display scored APIs with winner prominently highlighted and compatibility percentages.
    
    Args:
        scored_apis: List of APIScore objects sorted by score (highest first)
        
    Requirements: 3.1, 3.4
    """
    if not scored_apis:
        st.warning("No APIs available for evaluation.")
        return
    
    # Display winner prominently with recommendation badge
    winner = scored_apis[0]
    
    # Winner section with prominent styling
    st.markdown("### 🏆 **Winner**")
    
    # Create columns for winner display
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**{winner.api.name}**")
        st.markdown(f"*{winner.api.strengths[0] if winner.api.strengths else 'Top recommendation'}*")
    
    with col2:
        # Display compatibility percentage prominently
        st.metric(
            label="Compatibility",
            value=f"{winner.compatibility_percentage}%",
            delta=None
        )
    
    # Winner details in an expandable section
    with st.expander(f"📋 {winner.api.name} Details", expanded=True):
        # Create columns for organized display
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.markdown("**✅ Strengths:**")
            for strength in winner.api.strengths:
                st.markdown(f"• {strength}")
        
        with detail_col2:
            st.markdown("**⚠️ Limitations:**")
            for limitation in winner.api.limitations:
                st.markdown(f"• {limitation}")
    
    # Display other APIs if there are more than one
    if len(scored_apis) > 1:
        st.markdown("---")
        st.markdown("### 📊 **Other Options**")
        
        for api_score in scored_apis[1:]:
            # Create columns for each API
            api_col1, api_col2 = st.columns([3, 1])
            
            with api_col1:
                st.markdown(f"**{api_score.api.name}** (Rank #{api_score.recommendation_rank})")
                if api_score.api.strengths:
                    st.markdown(f"*{api_score.api.strengths[0]}*")
            
            with api_col2:
                # Show compatibility percentage for each API
                st.metric(
                    label="Compatibility",
                    value=f"{api_score.compatibility_percentage}%",
                    delta=None
                )
            
            # API details in collapsible section
            with st.expander(f"📋 {api_score.api.name} Details"):
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    st.markdown("**✅ Strengths:**")
                    for strength in api_score.api.strengths:
                        st.markdown(f"• {strength}")
                
                with detail_col2:
                    st.markdown("**⚠️ Limitations:**")
                    for limitation in api_score.api.limitations:
                        st.markdown(f"• {limitation}")
            
            st.markdown("")  # Add spacing between APIs


def display_trade_off_analysis(scored_apis: List['APIScore'], constraints: UserConstraints) -> None:
    """
    Build trade-off analysis table showing API comparisons with strengths, limitations,
    cost implications, rate limits, and TOS considerations.
    
    Args:
        scored_apis: List of APIScore objects sorted by score (highest first)
        constraints: User's constraints for context
        
    Requirements: 3.2, 3.3, 3.5
    """
    if not scored_apis:
        return
    
    st.markdown("### 📊 **Trade-off Analysis**")
    st.markdown("Compare key factors across all APIs to make an informed decision:")
    
    # Create comparison table data
    table_data = []
    
    for api_score in scored_apis:
        api = api_score.api
        
        # Format rate limits for display
        rate_limit_text = []
        for key, value in api.rate_limits.items():
            if "minute" in key.lower():
                rate_limit_text.append(f"{value}/min")
            elif "day" in key.lower():
                rate_limit_text.append(f"{value}/day")
            else:
                rate_limit_text.append(f"{key}: {value}")
        rate_limits_display = ", ".join(rate_limit_text) if rate_limit_text else "Not specified"
        
        # Format pricing for display
        pricing_tiers = []
        for tier, supported in api.pricing.items():
            if supported:
                pricing_tiers.append(tier.value)
        pricing_display = ", ".join(pricing_tiers) if pricing_tiers else "Not available"
        
        # Format data coverage
        data_coverage_display = ", ".join([dt.value for dt in api.data_coverage])
        
        # Check for TOS warnings
        tos_warnings = []
        for restriction in api.tos_restrictions:
            restriction_lower = restriction.lower()
            if "commercial use explicitly prohibited" in restriction_lower:
                tos_warnings.append("⚠️ No commercial use")
            elif "non-commercial use only" in restriction_lower:
                tos_warnings.append("⚠️ Non-commercial only")
            elif "personal/educational use only" in restriction_lower:
                tos_warnings.append("⚠️ Personal/educational only")
            elif "unofficial api" in restriction_lower:
                tos_warnings.append("⚠️ Unofficial API")
        
        # Add commercial use warning for Trading Bot use case
        if constraints.use_case.value == "Trading Bot" and tos_warnings:
            tos_display = " | ".join(tos_warnings)
        else:
            tos_display = " | ".join(tos_warnings) if tos_warnings else "✅ No major restrictions"
        
        # Format strengths and limitations
        top_strengths = api.strengths[:2] if len(api.strengths) >= 2 else api.strengths
        strengths_display = " | ".join(top_strengths) if top_strengths else "Not specified"
        
        top_limitations = api.limitations[:2] if len(api.limitations) >= 2 else api.limitations
        limitations_display = " | ".join(top_limitations) if top_limitations else "None noted"
        
        table_data.append({
            "API": f"**{api.name}**" + (f" 🏆" if api_score.recommendation_rank == 1 else f" (#{api_score.recommendation_rank})"),
            "Compatibility": f"{api_score.compatibility_percentage}%",
            "Pricing Tiers": pricing_display,
            "Rate Limits": rate_limits_display,
            "Data Coverage": data_coverage_display,
            "Key Strengths": strengths_display,
            "Main Limitations": limitations_display,
            "TOS Considerations": tos_display,
            "Reliability": f"{int(api.reliability_score * 100)}%"
        })
    
    # Display the comparison table
    import pandas as pd
    df = pd.DataFrame(table_data)
    
    # Display table with custom styling
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "API": st.column_config.TextColumn("API", width="medium"),
            "Compatibility": st.column_config.TextColumn("Match %", width="small"),
            "Pricing Tiers": st.column_config.TextColumn("Pricing", width="medium"),
            "Rate Limits": st.column_config.TextColumn("Rate Limits", width="small"),
            "Data Coverage": st.column_config.TextColumn("Data Types", width="medium"),
            "Key Strengths": st.column_config.TextColumn("Strengths", width="large"),
            "Main Limitations": st.column_config.TextColumn("Limitations", width="large"),
            "TOS Considerations": st.column_config.TextColumn("Terms of Service", width="large"),
            "Reliability": st.column_config.TextColumn("Reliability", width="small")
        }
    )
    
    # Add explanatory notes
    st.markdown("---")
    st.markdown("**📝 How to read this table:**")
    st.markdown(
        "• **Match %**: How well each API fits your specific requirements\n"
        "• **🏆**: Winner (best overall match)\n"
        "• **⚠️**: Important warnings or restrictions to consider\n"
        "• **✅**: No major restrictions identified"
    )
    
    # Highlight TOS warnings for commercial use cases
    if constraints.use_case.value == "Trading Bot":
        st.warning(
            "⚠️ **Commercial Use Notice**: You selected 'Trading Bot' as your use case. "
            "Pay special attention to 'Terms of Service' column for any commercial use restrictions."
        )


def display_verdict(verdict: 'Verdict') -> None:
    """
    Display the generated verdict above detailed results.
    
    Args:
        verdict: The Verdict object containing recommendation text, trade-offs, and next steps
        
    Requirements: 4.1
    """
    st.markdown("### 🎯 **Recommendation**")
    
    # Display main recommendation with markdown formatting
    st.markdown(verdict.recommendation_text)
    
    # Display trade-offs if available
    if verdict.trade_offs:
        st.markdown("**Trade-offs to consider:**")
        for trade_off in verdict.trade_offs:
            st.markdown(f"• {trade_off}")
    
    # Display alternative recommendation if provided
    if verdict.alternative_api and verdict.alternative_reason:
        st.info(f"💡 **Alternative Option**: {verdict.alternative_reason}")
    
    # Display actionable next steps
    if verdict.next_steps:
        st.markdown("**Next steps:**")
        for i, step in enumerate(verdict.next_steps, 1):
            st.markdown(f"{i}. {step}")
    
    st.markdown("---")


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="FinTech API Referee",
        page_icon="📊",
        layout="wide",
    )

    # Main header
    st.title("📊 FinTech API Referee")
    st.markdown(
        "Find the perfect financial data API for your needs. "
        "Enter your constraints and get personalized recommendations."
    )

    # Collect constraints from sidebar - Requirement 1.1
    constraints, analyze_clicked, error = collect_constraints()

    # Main content area
    if analyze_clicked:
        if error:
            st.warning(error)
        elif constraints:
            # Display constraint summary
            display_constraint_summary(constraints)

            try:
                # Use comprehensive performance monitoring - Requirements 7.1, 7.3
                with performance_monitor("recommendation generation", PERFORMANCE_TARGET_SECONDS) as timing:
                    logger.info(f"Starting API analysis for constraints: budget={constraints.budget.value}, "
                               f"data_types={[dt.value for dt in constraints.data_types]}, "
                               f"frequency={constraints.frequency.value}, use_case={constraints.use_case.value}")
                    
                    # Score APIs with detailed timing
                    with performance_monitor("API scoring", PERFORMANCE_TARGET_SECONDS * 0.6) as scoring_timing:
                        scored_apis = score_apis(constraints)
                    
                    logger.info(f"Successfully scored {len(scored_apis)} APIs in {scoring_timing['elapsed_seconds']:.3f} seconds")
                    
                    # Generate verdict with detailed timing
                    with performance_monitor("verdict generation", PERFORMANCE_TARGET_SECONDS * 0.4) as verdict_timing:
                        verdict = generate_verdict(scored_apis, constraints)
                    
                    logger.info(f"Successfully generated verdict in {verdict_timing['elapsed_seconds']:.3f} seconds")
                    
                    # Log comprehensive performance breakdown
                    total_time = timing.get("elapsed_seconds", time.time() - timing["start_time"])
                    logger.info(f"Performance breakdown - Scoring: {scoring_timing['elapsed_seconds']:.3f}s, "
                               f"Verdict: {verdict_timing['elapsed_seconds']:.3f}s, Total: {total_time:.3f}s")
                    
                    # Display performance feedback to user
                    display_performance_feedback(timing)
                    
                    # Display results with verdict integration
                    st.markdown("---")
                    st.subheader("🏆 Recommendations")
                    
                    # Display verdict first (Requirement 4.1)
                    display_verdict(verdict)
                    
                    # Display detailed results
                    display_results(scored_apis)
                    
                    # Display trade-off analysis
                    display_trade_off_analysis(scored_apis, constraints)
                
            except Exception as e:
                # Try fallback recommendation system - Requirements 7.5
                try:
                    from models import get_fallback_recommendations, generate_fallback_verdict
                    
                    logger.info("Attempting fallback recommendation system")
                    st.warning(
                        "⚠️ **Primary analysis system unavailable** - using fallback recommendations based on reliability scores."
                    )
                    
                    fallback_apis = get_fallback_recommendations(constraints)
                    fallback_verdict = generate_fallback_verdict(constraints)
                    
                    if fallback_apis:
                        # Display results with fallback data
                        st.markdown("---")
                        st.subheader("🏆 Fallback Recommendations")
                        
                        # Display fallback verdict
                        display_verdict(fallback_verdict)
                        
                        # Display fallback results
                        display_results(fallback_apis)
                        
                        # Note about fallback mode
                        st.info(
                            "📝 **Note**: These recommendations are based on reliability scores only. "
                            "For detailed analysis including trade-offs and comprehensive scoring, "
                            "please try again later when the system is fully operational."
                        )
                    else:
                        raise Exception("Fallback system also failed")
                        
                except Exception as fallback_error:
                    logger.error(f"Fallback system also failed: {str(fallback_error)}", exc_info=True)
                    
                    # Display user-friendly error message
                    st.error(
                        "⚠️ **Unable to generate recommendations**\n\n"
                        "We encountered an issue while analyzing the APIs. "
                        "Please try again with different constraints or contact support if the problem persists."
                    )
                    
                    # Provide fallback guidance
                    st.info(
                        "💡 **In the meantime, here are some general recommendations:**\n\n"
                        "• **For beginners**: Try Alpha Vantage (generous free tier)\n"
                        "• **For trading bots**: Consider Polygon.io or Finnhub (commercial use allowed)\n"
                        "• **For research**: Yahoo Finance (free but unofficial) or Alpha Vantage\n"
                        "• **For enterprise**: Quandl or Polygon.io (institutional grade)"
                    )
    else:
        # Welcome message when no analysis has been run
        st.markdown("---")
        st.markdown(
            "👈 **Get started** by entering your requirements in the sidebar "
            "and clicking **Find Best APIs**."
        )


if __name__ == "__main__":
    main()
