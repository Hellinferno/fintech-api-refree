#!/usr/bin/env python3
"""
Performance verification script for FinTech API Referee.

This script tests that the scoring system meets the 2-second performance requirement
by running various constraint scenarios and measuring execution times.

Requirements: 7.1, 7.3
"""

import sys
import time
import logging
from typing import List, Dict, Any
from models import (
    UserConstraints,
    BudgetTier,
    DataType,
    FrequencyTier,
    UseCase,
    score_apis,
    generate_verdict,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Performance requirements
PERFORMANCE_TARGET_SECONDS = 2.0
PERFORMANCE_WARNING_SECONDS = 1.5


def run_performance_test(constraints: UserConstraints, scenario_name: str) -> Dict[str, Any]:
    """
    Run a single performance test scenario.
    
    Args:
        constraints: User constraints to test
        scenario_name: Name of the test scenario
        
    Returns:
        Dictionary containing test results
    """
    logger.info(f"Running performance test: {scenario_name}")
    
    start_time = time.time()
    
    try:
        # Measure scoring performance
        scoring_start = time.time()
        scored_apis = score_apis(constraints)
        scoring_time = time.time() - scoring_start
        
        # Measure verdict generation performance
        verdict_start = time.time()
        verdict = generate_verdict(scored_apis, constraints)
        verdict_time = time.time() - verdict_start
        
        total_time = time.time() - start_time
        
        result = {
            "scenario": scenario_name,
            "success": True,
            "total_time": total_time,
            "scoring_time": scoring_time,
            "verdict_time": verdict_time,
            "within_target": total_time <= PERFORMANCE_TARGET_SECONDS,
            "api_count": len(scored_apis),
            "constraints": {
                "budget": constraints.budget.value,
                "data_types": [dt.value for dt in constraints.data_types],
                "frequency": constraints.frequency.value,
                "use_case": constraints.use_case.value,
            }
        }
        
        # Log results
        status = "✅ PASS" if result["within_target"] else "❌ FAIL"
        logger.info(f"{status} {scenario_name}: {total_time:.3f}s (scoring: {scoring_time:.3f}s, verdict: {verdict_time:.3f}s)")
        
        return result
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"❌ ERROR {scenario_name}: {str(e)} (after {total_time:.3f}s)")
        
        return {
            "scenario": scenario_name,
            "success": False,
            "total_time": total_time,
            "error": str(e),
            "within_target": False,
            "constraints": {
                "budget": constraints.budget.value,
                "data_types": [dt.value for dt in constraints.data_types],
                "frequency": constraints.frequency.value,
                "use_case": constraints.use_case.value,
            }
        }


def main():
    """Run comprehensive performance verification tests."""
    logger.info("Starting FinTech API Referee Performance Verification")
    logger.info(f"Performance target: {PERFORMANCE_TARGET_SECONDS} seconds")
    
    # Define test scenarios
    test_scenarios = [
        (
            UserConstraints(
                budget=BudgetTier.FREE,
                data_types=[DataType.STOCKS],
                frequency=FrequencyTier.EOD,
                use_case=UseCase.RESEARCH
            ),
            "Simple Free Tier"
        ),
        (
            UserConstraints(
                budget=BudgetTier.UNDER_50,
                data_types=[DataType.STOCKS, DataType.CRYPTO],
                frequency=FrequencyTier.DELAYED,
                use_case=UseCase.PORTFOLIO
            ),
            "Medium Complexity"
        ),
        (
            UserConstraints(
                budget=BudgetTier.ENTERPRISE,
                data_types=[DataType.STOCKS, DataType.CRYPTO, DataType.FOREX, DataType.OPTIONS],
                frequency=FrequencyTier.REALTIME,
                use_case=UseCase.TRADING_BOT
            ),
            "Complex Enterprise"
        ),
        (
            UserConstraints(
                budget=BudgetTier.UNDER_200,
                data_types=[DataType.CRYPTO, DataType.FOREX],
                frequency=FrequencyTier.REALTIME,
                use_case=UseCase.TRADING_BOT
            ),
            "Commercial Use Case"
        ),
        (
            UserConstraints(
                budget=BudgetTier.FREE,
                data_types=[DataType.STOCKS, DataType.CRYPTO, DataType.FOREX, DataType.OPTIONS, DataType.COMMODITIES],
                frequency=FrequencyTier.HISTORICAL,
                use_case=UseCase.EDUCATIONAL
            ),
            "All Data Types"
        ),
    ]
    
    # Run all test scenarios
    results = []
    total_tests = len(test_scenarios)
    passed_tests = 0
    failed_tests = 0
    
    logger.info(f"Running {total_tests} performance test scenarios...")
    print("\n" + "="*80)
    print("PERFORMANCE TEST RESULTS")
    print("="*80)
    
    for constraints, scenario_name in test_scenarios:
        result = run_performance_test(constraints, scenario_name)
        results.append(result)
        
        if result["success"] and result["within_target"]:
            passed_tests += 1
            status_icon = "✅"
        elif result["success"]:
            failed_tests += 1
            status_icon = "⚠️"
        else:
            failed_tests += 1
            status_icon = "❌"
        
        # Print result summary
        if result["success"]:
            print(f"{status_icon} {scenario_name:20} | {result['total_time']:.3f}s | "
                  f"APIs: {result['api_count']} | Target: {PERFORMANCE_TARGET_SECONDS}s")
        else:
            print(f"{status_icon} {scenario_name:20} | ERROR: {result.get('error', 'Unknown')}")
    
    # Calculate summary statistics
    successful_results = [r for r in results if r["success"]]
    if successful_results:
        times = [r["total_time"] for r in successful_results]
        min_time = min(times)
        max_time = max(times)
        avg_time = sum(times) / len(times)
    else:
        min_time = max_time = avg_time = 0.0
    
    pass_rate = (passed_tests / total_tests) * 100
    meets_requirements = pass_rate >= 90  # 90% pass rate threshold
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Tests:     {total_tests}")
    print(f"Passed:          {passed_tests}")
    print(f"Failed:          {failed_tests}")
    print(f"Pass Rate:       {pass_rate:.1f}%")
    print(f"Min Time:        {min_time:.3f}s")
    print(f"Max Time:        {max_time:.3f}s")
    print(f"Average Time:    {avg_time:.3f}s")
    print(f"Target Time:     {PERFORMANCE_TARGET_SECONDS}s")
    print(f"Requirements:    {'✅ MET' if meets_requirements else '❌ NOT MET'}")
    
    # Detailed failure analysis
    failed_results = [r for r in results if not (r["success"] and r["within_target"])]
    if failed_results:
        print("\n" + "="*80)
        print("FAILURE ANALYSIS")
        print("="*80)
        for result in failed_results:
            if not result["success"]:
                print(f"❌ {result['scenario']}: ERROR - {result.get('error', 'Unknown error')}")
            else:
                print(f"⚠️  {result['scenario']}: SLOW - {result['total_time']:.3f}s > {PERFORMANCE_TARGET_SECONDS}s")
    
    # Performance recommendations
    if not meets_requirements:
        print("\n" + "="*80)
        print("RECOMMENDATIONS")
        print("="*80)
        if avg_time > PERFORMANCE_TARGET_SECONDS:
            print("• Consider optimizing the scoring algorithm")
            print("• Review database access patterns")
            print("• Consider caching frequently accessed data")
        if max_time > PERFORMANCE_TARGET_SECONDS * 1.5:
            print("• Investigate worst-case performance scenarios")
            print("• Consider implementing timeout mechanisms")
        print("• Monitor performance in production environment")
        print("• Consider load testing with concurrent users")
    
    print("\n" + "="*80)
    
    # Exit with appropriate code
    if meets_requirements:
        logger.info("✅ All performance requirements met!")
        sys.exit(0)
    else:
        logger.error("❌ Performance requirements not met!")
        sys.exit(1)


if __name__ == "__main__":
    main()