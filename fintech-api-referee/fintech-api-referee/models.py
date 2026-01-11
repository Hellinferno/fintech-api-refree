"""
Data models for the FinTech API Referee application.
Defines core data structures for user constraints, API information, and scoring.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List
from datetime import datetime
import logging
import time

# Configure logging for error handling
logger = logging.getLogger(__name__)


class BudgetTier(Enum):
    """Budget constraint options for API selection."""
    FREE = "Free"
    UNDER_50 = "Under $50/month"
    UNDER_200 = "Under $200/month"
    ENTERPRISE = "Enterprise"


class DataType(Enum):
    """Types of financial data available from APIs."""
    STOCKS = "Stocks"
    CRYPTO = "Crypto"
    FOREX = "Forex"
    OPTIONS = "Options"
    COMMODITIES = "Commodities"


class FrequencyTier(Enum):
    """Data frequency options for API selection."""
    REALTIME = "Real-time"
    DELAYED = "Delayed (15-20 min)"
    EOD = "End-of-day"
    HISTORICAL = "Historical only"


class UseCase(Enum):
    """Use case categories for API selection."""
    RESEARCH = "Research/Analysis"
    TRADING_BOT = "Trading Bot"
    PORTFOLIO = "Portfolio Tracking"
    EDUCATIONAL = "Educational"


@dataclass
class UserConstraints:
    """User-provided constraints for API recommendation."""
    budget: BudgetTier
    data_types: List[DataType]
    frequency: FrequencyTier
    use_case: UseCase


@dataclass
class APIInfo:
    """Comprehensive information about a financial data API."""
    name: str
    pricing: Dict[BudgetTier, bool]  # Tier compatibility
    data_coverage: List[DataType]
    frequency_support: List[FrequencyTier]
    rate_limits: Dict[str, int]  # e.g., {"requests_per_minute": 5}
    strengths: List[str]
    limitations: List[str]
    tos_restrictions: List[str]
    reliability_score: float  # 0.0 to 1.0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class APIScore:
    """Scoring result for an API against user constraints."""
    api: APIInfo
    total_score: float  # 0.0 to 100.0
    category_scores: Dict[str, float]  # Scores by category
    compatibility_percentage: int  # 0 to 100
    recommendation_rank: int  # 1 = best match


@dataclass
class Verdict:
    """
    Holds the intelligent recommendation verdict with human-readable explanations.
    
    Requirements: 4.1
    """
    recommendation_text: str  # Main recommendation with bold formatting
    trade_offs: List[str]  # List of trade-off explanations in plain language
    next_steps: List[str]  # Actionable next steps for the recommended API
    alternative_api: str = ""  # Alternative recommendation if top choice has limitations
    alternative_reason: str = ""  # Reason for suggesting alternative


# Scoring weights for each category
SCORING_WEIGHTS = {
    "budget": 0.30,
    "data_types": 0.30,
    "frequency": 0.25,
    "use_case": 0.15,
}


def score_budget_compatibility(api: APIInfo, constraints: UserConstraints) -> float:
    """
    Score how well an API matches the user's budget tier.
    
    Returns 100.0 if API supports the budget tier, 0.0 otherwise.
    
    Requirements: 2.1, 2.2
    """
    if api.pricing.get(constraints.budget, False):
        return 100.0
    return 0.0


def score_data_type_coverage(api: APIInfo, constraints: UserConstraints) -> float:
    """
    Score how many of the user's requested data types the API supports.
    
    Returns percentage of requested data types that are covered (0-100).
    
    Requirements: 2.1, 2.2
    """
    if not constraints.data_types:
        return 100.0  # No data types requested means any API is fine
    
    covered = sum(1 for dt in constraints.data_types if dt in api.data_coverage)
    return (covered / len(constraints.data_types)) * 100.0


def score_frequency_availability(api: APIInfo, constraints: UserConstraints) -> float:
    """
    Score whether the API supports the user's requested data frequency.
    
    Returns 100.0 if frequency is supported, 0.0 otherwise.
    
    Requirements: 2.1, 2.2
    """
    if constraints.frequency in api.frequency_support:
        return 100.0
    return 0.0


def score_use_case_suitability(api: APIInfo, constraints: UserConstraints) -> float:
    """
    Score how suitable the API is for the user's use case.
    
    Considers TOS restrictions for commercial use cases (Trading Bot).
    Returns a score from 0-100 based on suitability.
    
    Requirements: 2.1, 2.2
    """
    # Check for commercial use restrictions
    commercial_use_cases = [UseCase.TRADING_BOT]
    
    if constraints.use_case in commercial_use_cases:
        # Check TOS restrictions for commercial use
        commercial_restricted_keywords = [
            "commercial use explicitly prohibited",
            "non-commercial use only",
            "personal/educational use only",
            "free tier for non-commercial use only",
        ]
        
        for restriction in api.tos_restrictions:
            restriction_lower = restriction.lower()
            for keyword in commercial_restricted_keywords:
                if keyword in restriction_lower:
                    return 25.0  # Heavily penalize but don't completely exclude
        
        # Check if commercial use is allowed
        commercial_allowed_keywords = [
            "commercial use allowed",
            "commercial use included",
        ]
        for restriction in api.tos_restrictions:
            restriction_lower = restriction.lower()
            for keyword in commercial_allowed_keywords:
                if keyword in restriction_lower:
                    return 100.0
        
        # Default score for commercial use when not explicitly mentioned
        return 75.0
    
    # For non-commercial use cases, most APIs are suitable
    return 100.0


def calculate_category_scores(api: APIInfo, constraints: UserConstraints) -> Dict[str, float]:
    """
    Calculate individual category scores for an API against user constraints.
    
    Returns a dictionary with scores for each category (0-100 scale).
    
    Requirements: 2.1, 2.2
    """
    return {
        "budget": score_budget_compatibility(api, constraints),
        "data_types": score_data_type_coverage(api, constraints),
        "frequency": score_frequency_availability(api, constraints),
        "use_case": score_use_case_suitability(api, constraints),
    }


def calculate_total_score(category_scores: Dict[str, float], weights: Dict[str, float] = None) -> float:
    """
    Calculate weighted total score from category scores.
    
    Args:
        category_scores: Dictionary of category name to score (0-100)
        weights: Optional custom weights, defaults to SCORING_WEIGHTS
        
    Returns:
        Weighted total score (0-100)
        
    Requirements: 2.2, 2.5
    """
    if weights is None:
        weights = SCORING_WEIGHTS
    
    total = 0.0
    for category, score in category_scores.items():
        weight = weights.get(category, 0.0)
        total += score * weight
    
    return total


def calculate_compatibility_percentage(total_score: float) -> int:
    """
    Convert total score to compatibility percentage (0-100).
    
    Requirements: 2.5
    """
    return max(0, min(100, int(round(total_score))))


def score_apis(constraints: UserConstraints, apis: List[APIInfo] = None) -> List[APIScore]:
    """
    Score all APIs against user constraints and return ranked results.
    
    Args:
        constraints: User's requirements and constraints
        apis: Optional list of APIs to score, defaults to all APIs
        
    Returns:
        List of APIScore objects sorted by total score (highest first)
        
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """
    start_time = time.time()
    
    try:
        if apis is None:
            apis = get_all_apis()
        
        logger.info(f"Scoring {len(apis)} APIs against constraints")
        
        scored_apis = []
        
        for api in apis:
            try:
                api_start_time = time.time()
                
                # Calculate category scores
                category_scores = calculate_category_scores(api, constraints)
                
                # Calculate total weighted score
                total_score = calculate_total_score(category_scores)
                
                # Calculate compatibility percentage
                compatibility = calculate_compatibility_percentage(total_score)
                
                scored_apis.append(APIScore(
                    api=api,
                    total_score=total_score,
                    category_scores=category_scores,
                    compatibility_percentage=compatibility,
                    recommendation_rank=0,  # Will be set after sorting
                ))
                
                api_time = time.time() - api_start_time
                logger.debug(f"Scored {api.name}: total={total_score:.2f}, compatibility={compatibility}% in {api_time:.4f}s")
                
            except Exception as e:
                logger.error(f"Error scoring API {api.name}: {str(e)}", exc_info=True)
                # Continue with other APIs rather than failing completely
                continue
        
        if not scored_apis:
            logger.error("No APIs were successfully scored")
            raise ValueError("Unable to score any APIs - all scoring attempts failed")
        
        # Sort by total score (highest first)
        sort_start_time = time.time()
        scored_apis.sort(key=lambda x: x.total_score, reverse=True)
        sort_time = time.time() - sort_start_time
        
        # Assign ranks (1 = best/winner)
        for rank, scored_api in enumerate(scored_apis, start=1):
            scored_api.recommendation_rank = rank
        
        total_time = time.time() - start_time
        logger.info(f"Successfully scored and ranked {len(scored_apis)} APIs in {total_time:.3f} seconds (sort: {sort_time:.4f}s)")
        
        # Performance monitoring - Requirements 7.1, 7.3
        if total_time > 2.0:
            logger.warning(f"Scoring performance issue: {total_time:.3f}s exceeds 2-second requirement")
        elif total_time > 1.0:
            logger.info(f"Scoring performance acceptable but slow: {total_time:.3f}s")
        else:
            logger.debug(f"Scoring performance good: {total_time:.3f}s")
        
        return scored_apis
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"Critical error in score_apis after {total_time:.3f}s: {str(e)}", exc_info=True, extra={
            'constraints': {
                'budget': constraints.budget.value if constraints else None,
                'data_types': [dt.value for dt in constraints.data_types] if constraints else None,
                'frequency': constraints.frequency.value if constraints else None,
                'use_case': constraints.use_case.value if constraints else None
            },
            'api_count': len(apis) if apis else 0,
            'execution_time': total_time
        })
        raise


def get_all_apis() -> List[APIInfo]:
    """
    Returns the complete API database with comprehensive information
    for major financial data providers.
    
    Requirements: 5.1, 5.2, 5.3, 5.4
    """
    return [
        APIInfo(
            name="Alpha Vantage",
            pricing={
                BudgetTier.FREE: True,
                BudgetTier.UNDER_50: True,
                BudgetTier.UNDER_200: True,
                BudgetTier.ENTERPRISE: True,
            },
            data_coverage=[DataType.STOCKS, DataType.CRYPTO, DataType.FOREX, DataType.COMMODITIES],
            frequency_support=[FrequencyTier.REALTIME, FrequencyTier.DELAYED, FrequencyTier.EOD, FrequencyTier.HISTORICAL],
            rate_limits={
                "requests_per_minute": 5,
                "requests_per_day": 500,
            },
            strengths=[
                "Generous free tier with 500 requests/day",
                "Excellent documentation and community support",
                "Wide data coverage including stocks, crypto, forex",
                "Technical indicators built-in",
                "Stable and reliable service",
            ],
            limitations=[
                "Strict rate limits on free tier (5 req/min)",
                "No options data available",
                "Real-time data requires premium subscription",
                "Limited historical depth on free tier",
            ],
            tos_restrictions=[
                "Attribution required for free tier usage",
                "Commercial use allowed with proper licensing",
                "No redistribution of raw data without permission",
            ],
            reliability_score=0.85,
            last_updated=datetime(2025, 1, 10),
        ),
        APIInfo(
            name="Polygon.io",
            pricing={
                BudgetTier.FREE: True,
                BudgetTier.UNDER_50: True,
                BudgetTier.UNDER_200: True,
                BudgetTier.ENTERPRISE: True,
            },
            data_coverage=[DataType.STOCKS, DataType.CRYPTO, DataType.FOREX, DataType.OPTIONS],
            frequency_support=[FrequencyTier.REALTIME, FrequencyTier.DELAYED, FrequencyTier.EOD, FrequencyTier.HISTORICAL],
            rate_limits={
                "requests_per_minute": 5,
                "requests_per_day": 1000,
            },
            strengths=[
                "Institutional-grade data quality",
                "Excellent real-time streaming capabilities",
                "Comprehensive options data",
                "WebSocket support for live data",
                "Strong API design and documentation",
            ],
            limitations=[
                "Free tier has limited features",
                "Premium pricing for full real-time access",
                "Some advanced features require enterprise plan",
                "Learning curve for WebSocket integration",
            ],
            tos_restrictions=[
                "Free tier for personal/non-commercial use only",
                "Commercial use requires paid subscription",
                "Data redistribution prohibited without license",
                "Must comply with exchange data policies",
            ],
            reliability_score=0.92,
            last_updated=datetime(2025, 1, 10),
        ),
        APIInfo(
            name="Yahoo Finance",
            pricing={
                BudgetTier.FREE: True,
                BudgetTier.UNDER_50: False,
                BudgetTier.UNDER_200: False,
                BudgetTier.ENTERPRISE: False,
            },
            data_coverage=[DataType.STOCKS, DataType.CRYPTO, DataType.FOREX, DataType.OPTIONS, DataType.COMMODITIES],
            frequency_support=[FrequencyTier.DELAYED, FrequencyTier.EOD, FrequencyTier.HISTORICAL],
            rate_limits={
                "requests_per_minute": 100,
                "requests_per_day": 2000,
            },
            strengths=[
                "Completely free to use",
                "Wide coverage of global markets",
                "Good historical data depth",
                "Options chain data available",
                "Easy to use with yfinance library",
            ],
            limitations=[
                "Unofficial API - may break without notice",
                "No official support or SLA",
                "Data quality can be inconsistent",
                "No real-time data available",
                "Rate limiting can be unpredictable",
            ],
            tos_restrictions=[
                "Commercial use explicitly prohibited",
                "No redistribution allowed",
                "Personal/educational use only",
                "Terms may change without notice",
                "Scraping may violate TOS",
            ],
            reliability_score=0.60,
            last_updated=datetime(2025, 1, 10),
        ),
        APIInfo(
            name="Finnhub",
            pricing={
                BudgetTier.FREE: True,
                BudgetTier.UNDER_50: True,
                BudgetTier.UNDER_200: True,
                BudgetTier.ENTERPRISE: True,
            },
            data_coverage=[DataType.STOCKS, DataType.CRYPTO, DataType.FOREX],
            frequency_support=[FrequencyTier.REALTIME, FrequencyTier.DELAYED, FrequencyTier.EOD, FrequencyTier.HISTORICAL],
            rate_limits={
                "requests_per_minute": 60,
                "requests_per_day": 1500,
            },
            strengths=[
                "Strong alternative data (news, sentiment)",
                "Good free tier with 60 req/min",
                "Real-time WebSocket support",
                "Company fundamentals and financials",
                "Developer-friendly API design",
            ],
            limitations=[
                "No options data",
                "No commodities data",
                "Limited historical depth on free tier",
                "Some features US-market focused",
            ],
            tos_restrictions=[
                "Free tier allows commercial use with attribution",
                "Data redistribution requires enterprise license",
                "Must display Finnhub attribution in apps",
            ],
            reliability_score=0.88,
            last_updated=datetime(2025, 1, 10),
        ),
        APIInfo(
            name="EODHD",
            pricing={
                BudgetTier.FREE: True,
                BudgetTier.UNDER_50: True,
                BudgetTier.UNDER_200: True,
                BudgetTier.ENTERPRISE: True,
            },
            data_coverage=[DataType.STOCKS, DataType.CRYPTO, DataType.FOREX, DataType.OPTIONS, DataType.COMMODITIES],
            frequency_support=[FrequencyTier.DELAYED, FrequencyTier.EOD, FrequencyTier.HISTORICAL],
            rate_limits={
                "requests_per_minute": 20,
                "requests_per_day": 1000,
            },
            strengths=[
                "Excellent historical data (30+ years)",
                "Global market coverage (70+ exchanges)",
                "Comprehensive fundamental data",
                "Good value for price",
                "Options and commodities included",
            ],
            limitations=[
                "No real-time streaming data",
                "API can be slower than competitors",
                "Documentation could be improved",
                "Limited free tier features",
            ],
            tos_restrictions=[
                "Commercial use allowed on paid plans",
                "Free tier for evaluation only",
                "Data redistribution requires special license",
                "Must comply with exchange agreements",
            ],
            reliability_score=0.82,
            last_updated=datetime(2025, 1, 10),
        ),
        APIInfo(
            name="Quandl",
            pricing={
                BudgetTier.FREE: False,
                BudgetTier.UNDER_50: False,
                BudgetTier.UNDER_200: True,
                BudgetTier.ENTERPRISE: True,
            },
            data_coverage=[DataType.STOCKS, DataType.FOREX, DataType.COMMODITIES],
            frequency_support=[FrequencyTier.EOD, FrequencyTier.HISTORICAL],
            rate_limits={
                "requests_per_minute": 300,
                "requests_per_day": 50000,
            },
            strengths=[
                "Premium institutional-grade data",
                "Extensive alternative datasets",
                "High data quality and accuracy",
                "Excellent for quantitative research",
                "Strong data governance and compliance",
            ],
            limitations=[
                "No free tier available",
                "Premium pricing (starts ~$100/month)",
                "No real-time data",
                "No crypto data",
                "No options data",
            ],
            tos_restrictions=[
                "Commercial use included in subscription",
                "Data redistribution strictly prohibited",
                "Must comply with Nasdaq data policies",
                "Audit rights reserved by provider",
            ],
            reliability_score=0.95,
            last_updated=datetime(2025, 1, 10),
        ),
        APIInfo(
            name="Marketstack",
            pricing={
                BudgetTier.FREE: True,
                BudgetTier.UNDER_50: True,
                BudgetTier.UNDER_200: True,
                BudgetTier.ENTERPRISE: True,
            },
            data_coverage=[DataType.STOCKS],
            frequency_support=[FrequencyTier.DELAYED, FrequencyTier.EOD, FrequencyTier.HISTORICAL],
            rate_limits={
                "requests_per_minute": 10,
                "requests_per_day": 100,
            },
            strengths=[
                "Simple REST API design",
                "Good for beginners",
                "Global stock market coverage",
                "Easy integration",
                "Clear documentation",
            ],
            limitations=[
                "Stocks only - no crypto, forex, options",
                "Very limited free tier (100 req/day)",
                "No real-time data",
                "Basic feature set compared to competitors",
                "Limited technical indicators",
            ],
            tos_restrictions=[
                "Free tier for non-commercial use only",
                "Commercial use requires paid plan",
                "No data redistribution",
                "Attribution appreciated but not required",
            ],
            reliability_score=0.78,
            last_updated=datetime(2025, 1, 10),
        ),
    ]


# Constants for verdict generation
LOW_RELIABILITY_THRESHOLD = 0.70
SIGNIFICANT_LIMITATION_KEYWORDS = [
    "commercial use explicitly prohibited",
    "non-commercial use only",
    "personal/educational use only",
    "unofficial api",
    "may break without notice",
]


def get_fallback_recommendations(constraints: UserConstraints) -> List[APIScore]:
    """
    Provide fallback recommendations based on reliability scores when primary scoring fails.
    
    Returns default recommendations sorted by reliability score to ensure users
    always receive guidance even when the main scoring system encounters errors.
    
    Args:
        constraints: User's constraints for basic filtering
        
    Returns:
        List of APIScore objects with basic scoring based on reliability
        
    Requirements: 7.5
    """
    try:
        logger.info("Generating fallback recommendations based on reliability scores")
        
        apis = get_all_apis()
        fallback_scores = []
        
        for api in apis:
            # Basic compatibility check - only include APIs that support the user's budget
            budget_compatible = api.pricing.get(constraints.budget, False)
            
            # Basic data type check - only include APIs that support at least one requested data type
            data_compatible = any(dt in api.data_coverage for dt in constraints.data_types)
            
            # Skip APIs that are completely incompatible
            if not budget_compatible or not data_compatible:
                continue
            
            # Use reliability score as the primary fallback metric
            # Scale reliability (0.0-1.0) to compatibility percentage (0-100)
            fallback_compatibility = int(api.reliability_score * 100)
            
            # Create basic category scores based on simple heuristics
            category_scores = {
                "budget": 100.0 if budget_compatible else 0.0,
                "data_types": 100.0 if data_compatible else 0.0,
                "frequency": 75.0,  # Assume most APIs support most frequencies
                "use_case": 75.0,   # Assume most APIs work for most use cases
            }
            
            # Use reliability score as total score (scaled to 0-100)
            total_score = api.reliability_score * 100
            
            fallback_scores.append(APIScore(
                api=api,
                total_score=total_score,
                category_scores=category_scores,
                compatibility_percentage=fallback_compatibility,
                recommendation_rank=0,  # Will be set after sorting
            ))
        
        # Sort by reliability score (highest first)
        fallback_scores.sort(key=lambda x: x.api.reliability_score, reverse=True)
        
        # Assign ranks
        for rank, scored_api in enumerate(fallback_scores, start=1):
            scored_api.recommendation_rank = rank
        
        # Ensure we have at least some recommendations
        if not fallback_scores:
            logger.warning("No compatible APIs found even for fallback recommendations")
            # Return the most reliable APIs regardless of compatibility
            all_apis = get_all_apis()
            all_apis.sort(key=lambda x: x.reliability_score, reverse=True)
            
            for rank, api in enumerate(all_apis[:3], start=1):  # Top 3 most reliable
                fallback_scores.append(APIScore(
                    api=api,
                    total_score=api.reliability_score * 100,
                    category_scores={
                        "budget": 50.0,
                        "data_types": 50.0,
                        "frequency": 50.0,
                        "use_case": 50.0,
                    },
                    compatibility_percentage=int(api.reliability_score * 100),
                    recommendation_rank=rank,
                ))
        
        logger.info(f"Generated {len(fallback_scores)} fallback recommendations")
        return fallback_scores
        
    except Exception as e:
        logger.error(f"Error generating fallback recommendations: {str(e)}", exc_info=True)
        
        # Last resort: return hardcoded reliable APIs
        try:
            apis = get_all_apis()
            # Find Alpha Vantage and Polygon.io as they are generally reliable
            reliable_apis = []
            for api in apis:
                if api.name in ["Alpha Vantage", "Polygon.io", "Finnhub"]:
                    reliable_apis.append(api)
            
            if not reliable_apis:
                reliable_apis = apis[:3]  # Take first 3 APIs as last resort
            
            hardcoded_scores = []
            for rank, api in enumerate(reliable_apis, start=1):
                hardcoded_scores.append(APIScore(
                    api=api,
                    total_score=75.0,  # Default reasonable score
                    category_scores={
                        "budget": 75.0,
                        "data_types": 75.0,
                        "frequency": 75.0,
                        "use_case": 75.0,
                    },
                    compatibility_percentage=75,
                    recommendation_rank=rank,
                ))
            
            logger.info(f"Using hardcoded fallback with {len(hardcoded_scores)} APIs")
            return hardcoded_scores
            
        except Exception as final_error:
            logger.critical(f"Complete failure in fallback system: {str(final_error)}", exc_info=True)
            return []


def generate_fallback_verdict(constraints: UserConstraints) -> Verdict:
    """
    Generate a fallback verdict when primary verdict generation fails.
    
    Args:
        constraints: User's constraints
        
    Returns:
        Basic verdict with general guidance
        
    Requirements: 7.5
    """
    try:
        logger.info("Generating fallback verdict")
        
        # Get fallback recommendations
        fallback_apis = get_fallback_recommendations(constraints)
        
        if fallback_apis:
            winner = fallback_apis[0]
            recommendation_text = (
                f"**{winner.api.name}** is recommended based on reliability "
                f"(system is operating in fallback mode). "
                f"This API has a **{int(winner.api.reliability_score * 100)}% reliability score** "
                f"and should meet your basic requirements."
            )
            
            next_steps = [
                f"Visit {winner.api.name}'s website to learn more about their offerings",
                "Review their pricing and terms of service carefully",
                "Test their API with a small sample before full implementation",
                "Consider trying the system again later for detailed analysis"
            ]
        else:
            recommendation_text = (
                "**Unable to provide specific recommendations** due to system issues. "
                "Please try again later or consider these general options."
            )
            
            next_steps = [
                "Try refreshing the page and submitting your constraints again",
                "Consider Alpha Vantage for free tier usage",
                "Consider Polygon.io for professional/commercial use",
                "Contact support if issues persist"
            ]
        
        return Verdict(
            recommendation_text=recommendation_text,
            trade_offs=["System is operating in fallback mode - detailed analysis unavailable"],
            next_steps=next_steps,
            alternative_api="",
            alternative_reason="",
        )
        
    except Exception as e:
        logger.error(f"Error in fallback verdict generation: {str(e)}", exc_info=True)
        
        # Absolute last resort verdict
        return Verdict(
            recommendation_text="**System temporarily unavailable** - please try again later.",
            trade_offs=["All recommendation systems are currently experiencing issues"],
            next_steps=[
                "Please try again in a few minutes",
                "Check your internet connection",
                "Contact support if the problem persists"
            ],
        )


def has_tos_restrictions_for_use_case(api: APIInfo, use_case: UseCase) -> bool:
    """
    Check if an API has TOS restrictions that conflict with the user's use case.
    
    Args:
        api: The API to check
        use_case: The user's intended use case
        
    Returns:
        True if there are conflicting TOS restrictions
        
    Requirements: 4.4
    """
    commercial_use_cases = [UseCase.TRADING_BOT]
    
    if use_case in commercial_use_cases:
        commercial_restricted_keywords = [
            "commercial use explicitly prohibited",
            "non-commercial use only",
            "personal/educational use only",
            "free tier for non-commercial use only",
            "free tier for personal/non-commercial use only",
        ]
        
        for restriction in api.tos_restrictions:
            restriction_lower = restriction.lower()
            for keyword in commercial_restricted_keywords:
                if keyword in restriction_lower:
                    return True
    
    return False


def has_significant_limitations(api_score: APIScore, constraints: UserConstraints) -> bool:
    """
    Detect if the top API choice has significant limitations.
    
    Significant limitations include:
    - Low reliability score (below threshold)
    - TOS restrictions that conflict with use case
    - Known instability issues
    
    Args:
        api_score: The scored API to check
        constraints: User's constraints to check against
        
    Returns:
        True if the API has significant limitations
        
    Requirements: 4.4
    """
    api = api_score.api
    
    # Check reliability score
    if api.reliability_score < LOW_RELIABILITY_THRESHOLD:
        return True
    
    # Check TOS restrictions for use case
    if has_tos_restrictions_for_use_case(api, constraints.use_case):
        return True
    
    # Check for known instability keywords in limitations
    for limitation in api.limitations:
        limitation_lower = limitation.lower()
        for keyword in SIGNIFICANT_LIMITATION_KEYWORDS:
            if keyword in limitation_lower:
                return True
    
    return False


def get_limitation_reasons(api_score: APIScore, constraints: UserConstraints) -> List[str]:
    """
    Get specific reasons why an API has significant limitations.
    
    Args:
        api_score: The scored API to analyze
        constraints: User's constraints
        
    Returns:
        List of limitation reasons in plain language
        
    Requirements: 4.4
    """
    reasons = []
    api = api_score.api
    
    if api.reliability_score < LOW_RELIABILITY_THRESHOLD:
        reasons.append(f"lower reliability score ({int(api.reliability_score * 100)}%)")
    
    if has_tos_restrictions_for_use_case(api, constraints.use_case):
        reasons.append("TOS restrictions that may conflict with your use case")
    
    for limitation in api.limitations:
        limitation_lower = limitation.lower()
        if "unofficial api" in limitation_lower or "may break without notice" in limitation_lower:
            reasons.append("potential stability concerns (unofficial API)")
            break
    
    return reasons


def generate_next_steps(api: APIInfo, constraints: UserConstraints) -> List[str]:
    """
    Generate actionable next steps for the recommended API.
    
    Args:
        api: The recommended API
        constraints: User's constraints
        
    Returns:
        List of actionable next steps
        
    Requirements: 4.5
    """
    next_steps = []
    
    # Step 1: Sign up / Get API key
    if constraints.budget == BudgetTier.FREE:
        next_steps.append(f"Sign up for a free {api.name} account and get your API key")
    else:
        next_steps.append(f"Visit {api.name}'s pricing page and select the {constraints.budget.value} plan")
    
    # Step 2: Review documentation
    next_steps.append(f"Review {api.name}'s API documentation for {', '.join(dt.value for dt in constraints.data_types)} endpoints")
    
    # Step 3: Rate limits awareness
    if api.rate_limits:
        rpm = api.rate_limits.get("requests_per_minute", "N/A")
        next_steps.append(f"Plan your request strategy around the {rpm} requests/minute rate limit")
    
    # Step 4: TOS compliance
    if api.tos_restrictions:
        if constraints.use_case == UseCase.TRADING_BOT:
            next_steps.append("Review the Terms of Service to ensure compliance with commercial use requirements")
        else:
            next_steps.append("Review the Terms of Service for any attribution or usage requirements")
    
    return next_steps


def generate_trade_offs(top_api: APIScore, runner_up: APIScore, constraints: UserConstraints) -> List[str]:
    """
    Generate plain language trade-off explanations between top APIs.
    
    Args:
        top_api: The top recommended API
        runner_up: The second-best API for comparison
        constraints: User's constraints
        
    Returns:
        List of trade-off explanations
        
    Requirements: 4.3
    """
    trade_offs = []
    top = top_api.api
    second = runner_up.api
    
    # Compare reliability
    if top.reliability_score < second.reliability_score:
        trade_offs.append(
            f"Choose **{second.name}** if you need higher reliability "
            f"({int(second.reliability_score * 100)}% vs {int(top.reliability_score * 100)}%)"
        )
    
    # Compare rate limits
    top_rpm = top.rate_limits.get("requests_per_minute", 0)
    second_rpm = second.rate_limits.get("requests_per_minute", 0)
    if second_rpm > top_rpm:
        trade_offs.append(
            f"Choose **{second.name}** if you need higher rate limits "
            f"({second_rpm} vs {top_rpm} requests/minute)"
        )
    
    # Compare data coverage
    top_coverage = set(top.data_coverage)
    second_coverage = set(second.data_coverage)
    second_only = second_coverage - top_coverage
    if second_only:
        missing_types = ", ".join(dt.value for dt in second_only)
        trade_offs.append(
            f"Choose **{second.name}** if you also need {missing_types} data"
        )
    
    # Compare pricing
    if constraints.budget == BudgetTier.FREE:
        if top.pricing.get(BudgetTier.FREE) and not second.pricing.get(BudgetTier.FREE):
            trade_offs.append(
                f"**{top.name}** offers a free tier while **{second.name}** requires payment"
            )
    
    # Add a strength-based trade-off
    if top.strengths and second.strengths:
        trade_offs.append(
            f"**{top.name}** excels at: {top.strengths[0].lower()}"
        )
    
    return trade_offs


def generate_verdict(top_apis: List[APIScore], constraints: UserConstraints) -> Verdict:
    """
    Generate an intelligent recommendation verdict with human-readable explanations.
    
    Uses bold formatting (markdown **text**) for key decision points.
    Explains trade-offs in plain language.
    Includes actionable next steps for the recommended API.
    Provides alternative recommendations when top choice has significant limitations.
    
    Args:
        top_apis: List of APIScore objects sorted by score (best first)
        constraints: User's constraints
        
    Returns:
        Verdict object with recommendation, trade-offs, and next steps
        
    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
    """
    start_time = time.time()
    
    try:
        logger.info(f"Generating verdict for {len(top_apis)} APIs")
        
        if not top_apis:
            logger.warning("No APIs provided for verdict generation")
            return Verdict(
                recommendation_text="No APIs available for evaluation.",
                trade_offs=[],
                next_steps=["Please check your constraints and try again."],
            )
        
        winner = top_apis[0]
        runner_up = top_apis[1] if len(top_apis) > 1 else None
        
        logger.debug(f"Winner: {winner.api.name} ({winner.compatibility_percentage}%)")
        if runner_up:
            logger.debug(f"Runner-up: {runner_up.api.name} ({runner_up.compatibility_percentage}%)")
        
        # Build recommendation text with bold formatting
        recommendation_parts = []
        recommendation_parts.append(
            f"**{winner.api.name}** is your best match with a "
            f"**{winner.compatibility_percentage}% compatibility score**."
        )
        
        # Add key strengths
        if winner.api.strengths:
            top_strength = winner.api.strengths[0]
            recommendation_parts.append(f"Key advantage: {top_strength}")
        
        # Add budget context
        if constraints.budget == BudgetTier.FREE:
            if winner.api.pricing.get(BudgetTier.FREE):
                recommendation_parts.append("This API offers a **free tier** that meets your budget requirements.")
        else:
            recommendation_parts.append(
                f"This API supports your **{constraints.budget.value}** budget tier."
            )
        
        recommendation_text = " ".join(recommendation_parts)
        
        # Generate trade-offs
        trade_offs = []
        if runner_up:
            try:
                trade_offs_start_time = time.time()
                trade_offs = generate_trade_offs(winner, runner_up, constraints)
                trade_offs_time = time.time() - trade_offs_start_time
                logger.debug(f"Generated trade-offs in {trade_offs_time:.4f}s")
            except Exception as e:
                logger.error(f"Error generating trade-offs: {str(e)}", exc_info=True)
                # Continue without trade-offs rather than failing
                trade_offs = []
        
        # Generate next steps
        try:
            next_steps_start_time = time.time()
            next_steps = generate_next_steps(winner.api, constraints)
            next_steps_time = time.time() - next_steps_start_time
            logger.debug(f"Generated next steps in {next_steps_time:.4f}s")
        except Exception as e:
            logger.error(f"Error generating next steps: {str(e)}", exc_info=True)
            # Provide basic fallback next steps
            next_steps = [
                f"Sign up for a {winner.api.name} account and get your API key",
                f"Review {winner.api.name}'s documentation for your data needs",
                "Test the API with a small sample before full implementation"
            ]
        
        # Check for significant limitations and suggest alternative
        alternative_api = ""
        alternative_reason = ""
        
        try:
            alternative_start_time = time.time()
            if has_significant_limitations(winner, constraints) and runner_up:
                limitation_reasons = get_limitation_reasons(winner, constraints)
                if limitation_reasons:
                    alternative_api = runner_up.api.name
                    reasons_text = " and ".join(limitation_reasons)
                    alternative_reason = (
                        f"Consider **{runner_up.api.name}** as an alternative due to {winner.api.name}'s "
                        f"{reasons_text}. {runner_up.api.name} has a {runner_up.compatibility_percentage}% "
                        f"compatibility score and {int(runner_up.api.reliability_score * 100)}% reliability."
                    )
            alternative_time = time.time() - alternative_start_time
            logger.debug(f"Checked for alternatives in {alternative_time:.4f}s")
        except Exception as e:
            logger.error(f"Error checking for alternative recommendations: {str(e)}", exc_info=True)
            # Continue without alternative recommendation
            pass
        
        verdict = Verdict(
            recommendation_text=recommendation_text,
            trade_offs=trade_offs,
            next_steps=next_steps,
            alternative_api=alternative_api,
            alternative_reason=alternative_reason,
        )
        
        total_time = time.time() - start_time
        logger.info(f"Successfully generated verdict in {total_time:.3f} seconds")
        
        # Performance monitoring - Requirements 7.1, 7.3
        if total_time > 1.0:
            logger.warning(f"Verdict generation performance issue: {total_time:.3f}s is slow")
        else:
            logger.debug(f"Verdict generation performance good: {total_time:.3f}s")
        
        return verdict
        
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"Critical error in generate_verdict after {total_time:.3f}s: {str(e)}", exc_info=True, extra={
            'api_count': len(top_apis) if top_apis else 0,
            'winner': top_apis[0].api.name if top_apis else None,
            'constraints': {
                'budget': constraints.budget.value if constraints else None,
                'use_case': constraints.use_case.value if constraints else None
            },
            'execution_time': total_time
        })
        
        # Return a basic fallback verdict
        return Verdict(
            recommendation_text="**Unable to generate detailed recommendation** due to a system error. Please try again.",
            trade_offs=["System encountered an error during analysis"],
            next_steps=[
                "Try refreshing the page and submitting your constraints again",
                "If the problem persists, consider manually reviewing the API options",
                "Contact support if you continue to experience issues"
            ],
        )
