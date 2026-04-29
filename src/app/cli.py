#!/usr/bin/env python3
"""
Smart Route Optimizer - Command Line Interface

Usage:
    python cli.py --start "Sydney, NSW" --end "Newcastle, NSW" --vehicle-type "Truck"
    python cli.py --start "Sydney, NSW" --end "Wollongong, NSW" --vehicle-type "B-Double"
"""

import argparse
import sys
import os
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents.route_planner import plan_route
from src.agents.traffic_monitor import fetch_traffic_incidents
from src.agents.weather_monitor import fetch_weather_alerts
from src.agents.route_optimizer import optimize_route
from src.agents.compliance_validator import validate_compliance
from src.agents.savings_reporter import generate_report, generate_gpx_route
import uuid

def main():
    parser = argparse.ArgumentParser(
        description="🚛 Smart Route Optimizer for Australian Transport",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --start "Sydney, NSW" --end "Newcastle, NSW" --vehicle-type "Truck"
  %(prog)s --start "Melbourne, VIC" --end "Geelong, VIC" --vehicle-type "Semi-Trailer"
  %(prog)s --start "Brisbane, QLD" --end "Gold Coast, QLD" --vehicle-type "B-Double"
        """
    )

    parser.add_argument(
        '--start',
        type=str,
        required=True,
        help='Start address (e.g., "Sydney, NSW")'
    )

    parser.add_argument(
        '--end',
        type=str,
        required=True,
        help='End address (e.g., "Newcastle, NSW")'
    )

    parser.add_argument(
        '--vehicle-type',
        type=str,
        default='Truck',
        choices=[
            'Rigid', 'Truck', 'Semi-Trailer', 'B-Double', 'B-Triple',
            'Tautliner', 'Reefer', 'Flatbed', 'Dump Truck', 'Tanker',
            'Livestock Carrier', 'Car Carrier', 'Container Hauler'
        ],
        help='Vehicle type (default: Truck)'
    )

    parser.add_argument(
        '--delivery-window',
        type=str,
        help='Delivery deadline (ISO format: YYYY-MM-DDTHH:MM:SS)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='reports',
        help='Directory to save reports (default: reports/)'
    )

    parser.add_argument(
        '--no-pdf',
        action='store_true',
        help='Skip PDF report generation'
    )

    parser.add_argument(
        '--no-gpx',
        action='store_true',
        help='Skip GPX file generation'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Parse delivery window
    delivery_window = None
    if args.delivery_window:
        try:
            delivery_window = datetime.fromisoformat(args.delivery_window)
        except ValueError:
            print(f"❌ Invalid date format: {args.delivery_window}")
            print("   Use ISO format: YYYY-MM-DDTHH:MM:SS")
            sys.exit(1)

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    print("=" * 60)
    print("🚛 Smart Route Optimizer for Australian Transport")
    print("=" * 60)
    print(f"\n📋 Optimizing route...")
    print(f"   From: {args.start}")
    print(f"   To:   {args.end}")
    print(f"   Vehicle: {args.vehicle_type}")

    try:
        # Step 1: Plan route
        print("\n📍 Planning route...")
        route_request = plan_route(args.start, args.end, args.vehicle_type, delivery_window)
        print(f"   ✓ Geocoded locations")

        # Step 2: Fetch data
        print("📡 Fetching real-time data...")
        traffic_incidents = fetch_traffic_incidents("NSW")
        print(f"   ✓ {len(traffic_incidents)} traffic incidents")

        mid_lat = (route_request["start"]["lat"] + route_request["end"]["lat"]) / 2
        mid_lng = (route_request["start"]["lng"] + route_request["end"]["lng"]) / 2
        weather_alerts = fetch_weather_alerts(mid_lat, mid_lng)
        print(f"   ✓ {len(weather_alerts)} weather alerts")

        # Step 3: Optimize
        print("🧠 Optimizing route...")
        optimized_route = optimize_route(route_request, traffic_incidents, weather_alerts)

        if "error" in optimized_route:
            raise Exception(optimized_route["error"])

        print(f"   ✓ Calculated optimal path")

        # Step 4: Compliance check
        print("⚖️  Checking compliance...")
        compliance = validate_compliance(optimized_route, args.vehicle_type)
        print(f"   ✓ NHVR Compliant: {'✅ Yes' if compliance['nhvr_compliant'] else '❌ No'}")
        print(f"   ✓ CoR Compliant: {'✅ Yes' if compliance['cor_compliant'] else '❌ No'}")

        # Step 5: Generate reports
        print("📊 Generating reports...")
        baseline_distance = optimized_route["distance_km"] * 1.15
        baseline_route = {
            "distance_km": baseline_distance,
            "duration_hours": baseline_distance / 100
        }

        # Generate unique filenames
        report_id = str(uuid.uuid4())[:8]
        report_filename = f"route_{report_id}.pdf"
        gpx_filename = f"route_{report_id}.gpx"

        report_path = os.path.join(args.output_dir, report_filename) if not args.no_pdf else None
        gpx_path = os.path.join(args.output_dir, gpx_filename) if not args.no_gpx else None

        savings = generate_report(
            optimized_route, baseline_route, args.vehicle_type, report_path
        )

        if not args.no_gpx:
            generate_gpx_route(optimized_route, gpx_path)

        # Print results
        print("\n" + "=" * 60)
        print("✅ OPTIMIZATION COMPLETE")
        print("=" * 60)

        print(f"\n📏 Distance:   {optimized_route['distance_km']:.1f} km")
        print(f"⏱  Duration:   {optimized_route['duration_hours']:.1f} hours")
        print(f"📍 Waypoints:  {len(optimized_route['route'])}")

        print(f"\n💰 Fuel Savings: {savings['fuel_savings']['litres']:.1f} L "
              f"($${savings['fuel_savings']['cost_AUD']:.2f})")
        print(f"🌍 CO₂ Reduced:  {savings['fuel_savings']['co2_kg']:.1f} kg")

        print(f"\n✅ NHVR Compliant: {'Yes' if compliance['nhvr_compliant'] else 'No'}")
        print(f"✅ CoR Compliant:  {'Yes' if compliance['cor_compliant'] else 'No'}")

        if report_path:
            print(f"\n📄 PDF Report:   {report_path}")
        if gpx_path:
            print(f"🗺  GPX File:     {gpx_path}")

        print("\n" + "=" * 60)

        return 0

    except ValueError as e:
        print(f"\n❌ Validation Error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Optimization Failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
