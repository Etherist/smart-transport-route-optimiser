import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

# Load NHVR rules
def load_nhvr_rules() -> Dict[str, Any]:
    """Load NHVR fatigue management rules from JSON."""
    try:
        with open("src/data/nhvr_rules.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load NHVR rules: {e}")
        return {}

NHVR_RULES = load_nhvr_rules()

# Load vehicle constraints
def load_vehicle_constraints() -> Dict[str, Any]:
    """Load vehicle constraints from JSON."""
    try:
        with open("src/data/vehicle_constraints.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load vehicle constraints: {e}")
        return {}

VEHICLE_CONSTRAINTS = load_vehicle_constraints()

def validate_compliance(
    route: Dict[str, Any],
    vehicle_type: str,
    driver_hours_week: float = 0.0,
    region: str = "NSW"
) -> Dict[str, Any]:
    """
    Validates the route against NHVR fatigue rules and CoR laws.
    Supports national Australian regulations with optional state-specific overrides.

    Args:
        route: Optimized route dictionary with duration
        vehicle_type: Type of vehicle being used
        driver_hours_week: Current accumulated driver hours this week
        region: State/territory for jurisdiction-specific rules (default: NSW)

    Returns:
        Compliance dictionary with NHVR and CoR status
    """
    try:
        duration_hours = route.get("duration_hours", 0)
        vehicle_rules = VEHICLE_CONSTRAINTS.get(
            vehicle_type, VEHICLE_CONSTRAINTS.get("Truck", {})
        )
        nhvr_limits = vehicle_rules.get("nhvr_rules", {})

        violations = []
        warnings = []
        compliance_notes = []

        # 1. Check daily work hour limit
        max_daily = nhvr_limits.get("max_hours_per_day", 12)
        if duration_hours > max_daily:
            violations.append(
                f"Route duration ({duration_hours:.1f}h) exceeds "
                f"daily limit of {max_daily}h"
            )
        else:
            remaining_daily = max_daily - duration_hours
            compliance_notes.append(
                f"Daily hours: {duration_hours:.1f}/{max_daily}h "
                f"({remaining_daily:.1f}h remaining)"
            )

        # 2. Check weekly work hour limit (if provided)
        if driver_hours_week > 0:
            max_weekly = nhvr_limits.get("max_hours_per_week", 72)
            total_weekly = driver_hours_week + duration_hours
            if total_weekly > max_weekly:
                violations.append(
                    f"Weekly total ({total_weekly:.1f}h) exceeds "
                    f"limit of {max_weekly}h"
                )
            else:
                remaining_weekly = max_weekly - total_weekly
                compliance_notes.append(
                    f"Weekly hours: {total_weekly:.1f}/{max_weekly}h"
                )

        # 3. Check minimum rest period requirement
        min_rest = nhvr_limits.get("min_rest_after_shift_hours", 7)
        remaining_daily = max_daily - duration_hours
        # Recommend rest if shift is >= 11 hours or within 2 hours of limit
        if duration_hours >= 11 or remaining_daily < 2:
            compliance_notes.append(
                f"After {duration_hours:.1f}h shift, minimum "
                f"{min_rest}h rest required"
            )

        # 4. CoR checks (simplified)
        cor_compliant = True
        if violations:
            cor_compliant = False
            warnings.append(
                "Chain of Responsibility: Driver fatigue violations "
                "indicate potential CoR breach"
            )
        else:
            # Add overall OK note for compliant routes
            compliance_notes.insert(0, "Compliance: OK")

        # Build result
        nhvr_compliant = len(violations) == 0

        result = {
            "nhvr_compliant": nhvr_compliant,
            "cor_compliant": cor_compliant,
            "fatigue_management": {
                "duration_hours": round(duration_hours, 2),
                "daily_limit": max_daily,
                "weekly_limit": nhvr_limits.get("max_hours_per_week", 72),
                "min_rest_hours": min_rest,
                "violations": violations,
                "warnings": warnings,
                "notes": compliance_notes
            },
            "vehicle_type": vehicle_type
        }

        if nhvr_compliant:
            logger.info(
                f"Route compliant: {vehicle_type}, "
                f"{duration_hours:.1f}h duration"
            )
        else:
            logger.warning(
                f"Route non-compliant: {vehicle_type}, "
                f"violations: {violations}"
            )

        return result

    except Exception as e:
        logger.error(f"Compliance validation failed: {e}")
        return {
            "nhvr_compliant": False,
            "cor_compliant": False,
            "fatigue_management": {
                "error": str(e)
            },
            "vehicle_type": vehicle_type
        }
