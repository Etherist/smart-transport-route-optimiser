# Compliance: NHVR & Chain of Responsibility

## Overview

Australian transport operators must comply with the **National Heavy Vehicle Regulator (NHVR)** fatigue management rules and the **Chain of Responsibility (CoR)** laws. Non-compliance can result in significant fines, legal liabilities, and operational disruptions.

This document outlines how the Smart Route Optimizer enforces these regulations.

---

## NHVR Fatigue Management Rules

The NHVR sets national standards for heavy vehicle driver fatigue management. Key rules include:

### Standard Hours (Standard Rules)

| Rule | Limit |
|------|-------|
| Maximum work hours per day | **12 hours** |
| Maximum work hours per week | **72 hours** (in any 7-day period) |
| Minimum continuous rest period | **7 hours** |
| Maximum consecutive work days | **7 days** |

### Heavy Vehicle Rules

For vehicles over a certain GVM (Gross Vehicle Mass), stricter rules may apply. Our system incorporates these as configurable per-vehicle constraints.

**Source:** [NHVR Fatigue Management](https://www.nhvr.gov.au/safety-compliance/fatigue-management)

---

## Chain of Responsibility (CoR)

CoR laws allocate shared responsibility for compliance across all parties in the transport supply chain:

### Parties in the Chain
- **Consignor** (sender of goods)
- **Consignee** (receiver)
- **Loader** (person loading the vehicle)
- **Driver**
- **Operator** (vehicle owner/manager)
- **Scheduler** (person planning trips)

### Primary Duties

Each party must take reasonable steps to prevent:
1. **Breaches of mass/dimension limits**
2. **Speed limit violations**
3. **Driving while fatigued**
4. **Load restraint failures**
5. **Vehicle maintenance lapses**

**Source:** [NHVR Chain of Responsibility](https://www.nhvr.gov.au/safety-compliance/chain-of-responsibility)

---

## How the Smart Route Optimizer Enforces Compliance

### 1. Route Duration Validation

The Compliance Validator agent checks the optimized route's total driving time against NHVR limits.

**Example:** A route taking 13 hours violates the 12-hour daily limit:
```json
{
    "nhvr_compliant": false,
    "cor_compliant": false,
    "fatigue_management": {
        "violations": [
            "Route duration (13.0h) exceeds daily limit of 12h"
        ]
    }
}
```

### 2. Weekly Accumulation Check

If the user provides current weekly hours (`driver_hours_week`), the system also validates that adding this route's duration won't exceed the 72-hour weekly cap.

**Example:** Driver already worked 65h; a 10h route would total 75h → violation:
```json
"Weekly total (75.0h) exceeds limit of 72h"
```

### 3. Rest Period Recommendations

For routes approaching the daily limit (≥11 hours or remaining < 2 hours), the system advises the required minimum rest (7 hours) before the next shift.

**Example Note:**
```
"After 11.5h shift, minimum 7h rest required"
```

### 4. Vehicle-Specific Rules

Different vehicle types have different constraints (e.g., B-Doubles may have additional requirements). The system loads these from `vehicle_constraints.json`:

- **Truck**: standard 12h daily limit
- **B-Double**: 12h limit, higher fuel consumption
- **Semi-Trailer**: 12h limit

### 5. Compliance Reporting

Every optimization response includes a `compliance` object with:
- `nhvr_compliant`: boolean
- `cor_compliant`: boolean (mirrors NHVR status in simplified model)
- `fatigue_management`: detailed breakdown (duration, limits, violations, notes)

---

## Example Compliance Scenarios

### Scenario 1: Short Haul (Compliant)

**Route:** Sydney → Central Coast (2.5 hours)  
**Vehicle:** Truck  
**Result:**
- NHVR Compliant: ✅
- CoR Compliant: ✅
- Notes: `["Compliance: OK", "Daily hours: 2.5/12h (9.5h remaining)"]`

---

### Scenario 2: Long Haul Violation

**Route:** Sydney → Brisbane (14 hours driving)  
**Vehicle:** Semi-Trailer  
**Result:**
- NHVR Compliant: ❌
- CoR Compliant: ❌
- Violations: `["Route duration (14.0h) exceeds daily limit of 12h"]`
- Required Action: Split route into two shifts with overnight rest

---

### Scenario 3: Weekly Limit Exceeded

**Current Weekly Hours:** 68h  
**New Route Duration:** 5h  
**Total:** 73h → exceeds 72h  
**Result:** Non-compliant; system advises postponing or reassigning driver.

---

## Auditing & Record-Keeping

The system automatically generates:
- **PDF Reports** containing route details, compliance status, and driver sign-off fields
- **GPX Files** for GPS tracking during transit
- **Savings Metrics** for sustainability reporting

These documents can serve as evidence of compliance in audits.

---

## Limitations & Disclaimers

This demo tool **does not** replace certified compliance management systems. Real-world deployment requires:

- Integration with official NHVR APIs for real-time rule updates
- Electronic Work Diary (EWD) synchronization
- accredited training and record-keeping procedures
- Legal review of all compliance logic

Always consult with a accredited compliance officer for regulatory decisions.

---

## Further Reading

- [NHVR Official Website](https://www.nhvr.gov.au)
- [Heavy Vehicle National Law (HVNL)](https://www.nhvr.gov.au/laws-and-regulations/hvnl)
- [Chain of Responsibility Guidelines](https://www.nhvr.gov.au/safety-compliance/chain-of-responsibility/cor-effectiveness)
- [Australian Government - Transport Safety](https://www.infrastructure.gov.au/transport/safety/index.aspx)
