# Vehicle Fleet Guide

Comprehensive reference for all supported heavy vehicle types in the Smart Route Optimizer.

## Overview

This guide provides technical specifications, typical use cases, and NHVR compliance considerations for each vehicle class. Use this information to select the correct vehicle type when creating route optimization requests.

## Vehicle Types Summary

| Vehicle Class | Max Speed (km/h) | Fuel (L/km) | Max Mass (kg) | Length (m) | Typical Use |
|---------------|-----------------|-------------|---------------|------------|-------------|
| Rigid | 100 | 0.12 | 22,000 | 12.0 | Urban delivery, refuse |
| Truck | 100 | 0.15 | 40,000 | 12.0 | General freight |
| Semi-Trailer | 100 | 0.18 | 50,000 | 16.0 | Long haul |
| B-Double | 90 | 0.20 | 60,000 | 19.0 | Heavy intercity |
| B-Triple | 90 | 0.23 | 80,000 | 28.0 | Outback road trains |
| Tautliner | 100 | 0.19 | 42,000 | 16.5 | General freight, curtaining |
| Reefer | 95 | 0.22 | 38,000 | 16.0 | Refrigerated goods |
| Flatbed | 100 | 0.16 | 45,000 | 16.5 | Construction, steel |
| Dump Truck | 80 | 0.25 | 35,000 | 10.0 | Quarry, mining |
| Tanker | 90 | 0.21 | 38,000 | 14.5 | Fuel, chemicals |
| Livestock Carrier | 90 | 0.19 | 40,000 | 16.0 | Animals |
| Car Carrier | 95 | 0.18 | 45,000 | 18.0 | Vehicle transport |
| Container Hauler | 100 | 0.20 | 42,000 | 16.5 | Shipping containers |

---

## Detailed Vehicle Profiles

### 1. Rigid (2-axle truck)

**Characteristics:**
- Single rigid chassis with 2 axles
- Compact size for urban environments
- High fuel efficiency

**Typical Applications:**
- Local parcel delivery
- Refuse collection
- Small-scale construction
- Service vehicles

**NHVR Class:** Rigid vehicle (under 12t GVM typically)

**Advantages:**
- Access to narrow streets
- Lower fuel consumption
- Easy maneuverability

**Limitations:**
- Lower payload capacity
- Not suitable for long-haul

---

### 2. Standard Truck (3-axle)

**Characteristics:**
- Three-axle configuration
- Common general freight vehicle
- Balanced performance

**Typical Applications:**
- Regional distribution
- General palletized freight
- Refrigerated variants (see Reefer)

**NHVR Class:** Heavy vehicle (>12t GVM)

**Advantages:**
- Good payload-to-size ratio
- Widespread availability
- Compliant on most roads

**Limitations:**
- Limited to 12m length
- Lower capacity than combos

---

### 3. Semi-Trailer

**Characteristics:**
- Prime mover + single trailer
- 16m overall length
- Standard Australian road train building block

**Typical Applications:**
- Interstate freight
- General cargo
- Tautliner/curtain-sided variants
- Refrigerated variants

**NHVR Class:** Heavy combination vehicle

**Advantages:**
- Good payload capacity
- Versatile body types
- Access to most major highways

**Limitations:**
- Some urban restrictions
- Requires higher skill license

---

### 4. B-Double

**Characteristics:**
- Two trailers connected via fifth wheel on first trailer
- 19m overall length
- Higher mass limit than semi

**Typical Applications:**
- High-volume intercity freight
- Bulk goods (grain, freight)
- Industrial supply chain

**NHVR Class:** B-Double (restricted access vehicle)

**Advantages:**
- Increased payload (up to 60t)
- Better fuel per tonne-km
- Common in major freight corridors

**Limitations:**
- Requires specific route permits in some states
- Not permitted on all roads
- Lower speed limit (90 km/h typical)

**Route Restrictions:** Some urban areas and minor highways prohibit B-Doubles. Always check state RAV (Restricted Access Vehicle) networks.

---

### 5. B-Triple

**Characteristics:**
- Three trailers in a B configuration
- 28.5m overall length
- Largest legal road vehicle on normal roads (excluding road trains)

**Typical Applications:**
- Bulk haulage (grain, ore, livestock)
- Remote area supply
- Outback freight routes

**NHVR Class:** B-Triple (heavy combination)

**Advantages:**
- Maximum payload (up to 80t)
- Most efficient for high-volume bulk

**Limitations:**
- Very restricted access (dedicated routes only)
- Requires special permits and escorts
- Lower speed (typically 90 km/h)
- Not urban compatible

**Route Restrictions:** Only operates on approved heavy vehicle routes; typically limited to remote and designated highways. NOT permitted in major cities.

---

### 6. Tautliner (Curtain-Sider)

**Characteristics:**
- Curtain-sided trailer for side loading
- Flexible for various cargo types
- Often used with semi-trailer or B-double

**Typical Applications:**
- Palletized goods
- Machinery transport
- Mixed freight
- Weather-protected but not fully enclosed

**NHVR Class:** Heavy combination or rigid

**Advantages:**
- Fast side loading/unloading
- Flexibility for various cargo heights
- Secure with curtains

**Limitations:**
- Not suitable for very high-value goods (security)
- Some cargo types require covering

---

### 7. Reefer (Refrigerated)

**Characteristics:**
- Integrated refrigeration unit powered by diesel or electric
- Temperature-controlled environment
- Higher fuel consumption

**Typical Applications:**
- Perishable food transport
- Pharmaceuticals
- Flowers
- Frozen goods

**NHVR Class:** Refrigerated heavy vehicle

**Advantages:**
- Temperature stability
- Compliance for cold chain
- Range of temperature zones (-30°C to +30°C)

**Limitations:**
- Additional fuel consumption (reefer unit)
- Higher maintenance costs
- Requires pre-cooling

**Fuel Note:** Add approx. 2–4 L/h for refrigeration operation depending on setpoint and ambient temperature.

---

### 8. Flatbed

**Characteristics:**
- Open flat platform
- No sides or roof
- Quick loading/unloading from any side

**Typical Applications:**
- Construction materials (steel, timber)
- Machinery
- Containers (via twist locks)
- Oversized loads (with permits)

**NHVR Class:** Heavy rigid or combination

**Advantages:**
- Maximum flexibility for cargo dimensions
- Fast loading
- Easy securing with chains/straps

**Limitations:**
- Cargo exposed to elements
- Requires additional securing effort
- Height restrictions apply

---

### 9. Dump Truck (Tipper)

**Characteristics:**
- Hydraulic lifting bed for unloading
- Typically 3-axle rigid
- High ground clearance

**Typical Applications:**
- Quarry operations
- Construction aggregates
- Mining site haulage
- Bulk material delivery

**NHVR Class:** Heavy rigid

**Advantages:**
- Self-unloading – no extra labor
- Robust off-highway capability
- High payload for weight

**Limitations:**
- Lower on-road speed (80 km/h)
- Not suitable for general freight
- Usually operates regionally

---

### 10. Tanker

**Characteristics:**
- Cylindrical liquid-carrying vessel
- compartments for multiple liquids
- fittings for pump operation

**Typical Applications:**
- Fuel distribution (petrol, diesel)
- Chemical transport
- Food-grade liquids (milk, water)
- Hazardous materials (with additional compliance)

**NHVR Class:** Tanker (dangerous goods classification if applicable)

**Advantages:**
- Efficient bulk liquid movement
- Specialized compartments

**Limitations:**
- Requires dangerous goods endorsement if carrying hazardous loads
- Lower speed due to center of gravity
- Route restrictions for certain placards

**Note:** Dangerous goods require separate ADG Code compliance, not covered by this tool.

---

### 11. Livestock Carrier

**Characteristics:**
- Multi-deck compartments
- Ventilation systems
- Animal welfare amenities

**Typical Applications:**
- Transport of cattle, sheep, pigs
- Live animal sales
- Farm-to-market movement

**NHVR Class:** Livestock vehicle (specific permit category)

**Advantages:**
- Purpose-built for animal welfare
- High capacity (multiple decks)

**Limitations:**
- Restricted routes (some tunnels/bridges)
- Special permit needed
- Driver accreditation required

---

### 12. Car Carrier

**Characteristics:**
- Multi-level decks with ramps
- Tie-down points for vehicles
- Often tilt-deck or enclosed

**Typical Applications:**
- New car delivery from ports to dealers
- Vehicle relocations
- Auto auctions transport

**NHVR Class:** Vehicle transporter

**Advantages:**
- Efficient batch vehicle movement
- Fast loading via ramps

**Limitations:**
- Height restrictions (low clearance zones)
- Some urban road restrictions

---

### 13. Container Hauler

**Characteristics:**
- Designed to carry 20ft / 40ft shipping containers
- Twist-lock securing system
- Often semi-trailer format

**Typical Applications:**
- Port-to-warehouse
- Intermodal freight
- International supply chain

**NHVR Class:** Combination vehicle (often with container twist locks)

**Advantages:**
- Global standard – easy interchange
- Secure for cargo
- Versatile for various container sizes

**Limitations:**
- Container weight limits apply (max 30t for 40")
- Port access restrictions

---

## Selecting the Right Vehicle Type

When using the Smart Route Optimizer, consider:

1. **Match your actual fleet** – choosing a larger vehicle than needed inflates fuel consumption
2. **Route restrictions** – some vehicles cannot use certain roads due to size/weight
3. **License class** – driver must hold appropriate licence (e.g., HC for semi-trailer, MC for B-Double/B-Triple)
4. **Permit requirements** – B-Doubles/B-Triples often require state permits

### Vehicle Selection Decision Tree

```
Need to carry < 22t? → Rigid
Need 22-40t and urban access? → Truck
Need 40-50t long haul? → Semi-Trailer
Need 50-60t high volume? → B-Double
Need >60t or bulk? → B-Triple (on approved routes only)
Need temperature control? → Reefer
Need side loading? → Tautliner
Need open platform? → Flatbed
Need liquid bulk? → Tanker
Need to move livestock? → Livestock Carrier
Need to transport cars? → Car Carrier
Moving shipping containers? → Container Hauler
```

---

## NHVR Fatigue Rules (Recap)

All vehicles are subject to the same NHVR fatigue limits (unless under a different accreditation model):

| Limit | Hours |
|-------|-------|
| Max work per day | 12 |
| Max work per week | 72 |
| Minimum continuous rest | 7 |
| Consecutive work days max | 7 |

After 12 hours on duty, a minimum 7-hour break is mandatory. After 72 hours weekly, a 24-hour break is required.

---

## Chain of Responsibility (CoR)

Regardless of vehicle type, all parties in the transport chain share legal duty to prevent breaches:

- **Driver** – must not drive while fatigued
- **Operator** – must not pressure driver to breach limits
- **Loader** – must not overload vehicle beyond legal mass
- **Scheduler** – must plan realistic timetables

The optimizer flags potential fatigue violations before dispatch.

---

## State-Specific Vehicle Restrictions

| State | B-Double Restrictions | B-Triple Restrictions |
|-------|---------------------|----------------------|
| NSW | RAV network required; prohibited in CBD | Not permitted in Sydney metropolitan area |
| VIC | Must comply with Notice Vehicle 2.2 | Restricted to designated routes only |
| QLD | RAV map mandatory; may require escorts | Very limited – outback routes only |
| SA | Some highways permit; local council bans | Outback only |
| WA | Road trains authorized only on specific routes | Not applicable (road train class) |
| TAS | Limited – mainly urban access denied | Not permitted |
| NT | Permitted on many highways with permits | Allowed on approved routes |
| ACT | Generally prohibited in urban area | Prohibited |

Always verify current road access permits before operating. Rules may change; consult NHVR or state heavy vehicle agencies for latest maps.

---

## Maintenance & Compliance Tips

- Keep vehicle dimensions and weight records up to date in your fleet management system
- Ensure drivers hold correct licence class (HC, MC, etc.)
- Maintain a current NHVR accreditation if operating under the HCVS
- Schedule regular calibrations for temperature sensors (reefers)
- Document all maintenance in vehicle logs (CoR requirement)
- Check state-specific road closures before each trip

---

For detailed regulatory information, visit:

- NHVR: https://www.nhvr.gov.au
- Transport for NSW: https://www.transport.nsw.gov.au
- VicRoads: https://www.vicroads.vic.gov.au
- TMR QLD: https://www.tmr.qld.gov.au
