import logging
import os
import json
from typing import Dict, Optional, Any
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from ..utils.config import Config

logger = logging.getLogger(__name__)

def generate_report(
    route: Dict[str, Any],
    baseline_route: Dict[str, Any],
    vehicle_type: str,
    output_path: Optional[str] = None,
    region: str = "NSW",
    traffic_incidents: Optional[list] = None,
    weather_alerts: Optional[list] = None
) -> Dict[str, Any]:
    """
    Calculates savings (fuel, CO2) and generates a detailed PDF report.
    Enhanced with regional context, traffic incidents, and weather alerts.

    Args:
        route: Optimized route dictionary
        baseline_route: Baseline/manual route dictionary
        vehicle_type: Type of vehicle
        output_path: Optional path to save PDF report
        region: State/territory for context
        traffic_incidents: List of traffic incidents affecting route
        weather_alerts: List of weather alerts along route

    Returns:
        Dictionary with savings metrics
    """
    try:
        # Load vehicle constraints for fuel consumption
        with open("src/data/vehicle_constraints.json", "r") as f:
            import json
            vehicle_data = json.load(f)

        vehicle_info = vehicle_data.get(vehicle_type, vehicle_data.get("Truck", {}))
        fuel_rate = vehicle_info.get("fuel_consumption_L_per_km", 0.15)

        # Calculate fuel consumption for both routes
        route_fuel = route["distance_km"] * fuel_rate
        baseline_fuel = baseline_route["distance_km"] * fuel_rate

        fuel_savings_litres = baseline_fuel - route_fuel
        fuel_savings_cost = fuel_savings_litres * Config.FUEL_PRICE_AUD_PER_LITRE

        # Calculate CO2 emissions
        route_co2 = route_fuel * Config.CO2_PER_LITRE
        baseline_co2 = baseline_fuel * Config.CO2_PER_LITRE
        co2_savings = baseline_co2 - route_co2

        # Generate PDF if path provided
        report_path = None
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            report_path = _generate_pdf_report(
                route, baseline_route, fuel_savings_litres,
                fuel_savings_cost, co2_savings, vehicle_type, output_path,
                region=region, traffic_incidents=traffic_incidents or [],
                weather_alerts=weather_alerts or []
            )

        result = {
            "fuel_savings": {
                "litres": round(fuel_savings_litres, 2),
                "cost_AUD": round(fuel_savings_cost, 2),
                "co2_kg": round(co2_savings, 2)
            },
            "route_fuel_litres": round(route_fuel, 2),
            "route_co2_kg": round(route_co2, 2),
            "baseline_fuel_litres": round(baseline_fuel, 2),
            "baseline_co2_kg": round(baseline_co2, 2),
            "report_path": report_path
        }

        logger.info(
            f"Report generated: {fuel_savings_litres:.1f}L saved, "
            f"${fuel_savings_cost:.2f} cost savings"
        )

        return result

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return {"error": str(e)}

def _generate_pdf_report(
    route: Dict[str, Any],
    baseline_route: Dict[str, Any],
    fuel_savings: float,
    cost_savings: float,
    co2_savings: float,
    vehicle_type: str,
    output_path: str,
    region: str = "NSW",
    traffic_incidents: List[Dict[str, Any]] = [],
    weather_alerts: List[Dict[str, Any]] = []
) -> str:
    """
    Generates a comprehensive PDF report with route details, savings analysis, and situational awareness.

    Args:
        route: Optimized route dictionary
        baseline_route: Baseline/manual route dictionary
        fuel_savings: Litres saved
        cost_savings: Cost saved in AUD
        co2_savings: CO₂ reduction in kg
        vehicle_type: Vehicle class
        output_path: Path to save PDF file
        region: State/territory for jurisdictional context
        traffic_incidents: List of traffic incidents affecting route
        weather_alerts: List of weather alerts along route

    Returns:
        Path to generated PDF file
    """
    try:
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from datetime import datetime

        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Load vehicle constraints for fuel rate and CO2 calculations
        with open("src/data/vehicle_constraints.json", "r") as f:
            vehicle_data = json.load(f)
        vehicle_info = vehicle_data.get(vehicle_type, vehicle_data.get("Truck", {}))
        fuel_rate = vehicle_info.get("fuel_consumption_L_per_km", 0.15)

        # Derive CO2 numbers for table
        route_fuel = route["distance_km"] * fuel_rate
        baseline_fuel = baseline_route["distance_km"] * fuel_rate
        route_co2 = route_fuel * Config.CO2_PER_LITRE
        baseline_co2 = baseline_fuel * Config.CO2_PER_LITRE

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # center
        )
        story.append(Paragraph("🚛 Smart Route Optimizer Report", title_style))
        story.append(Paragraph(f"<i>Generated for {region} Region</i>", styles['Normal']))
        story.append(Spacer(1, 20))

        # Executive summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Spacer(1, 10))
        summary_text = f"""
        This report details an optimized heavy vehicle route calculated by the Smart Route Optimizer.
        The route was planned for a <b>{vehicle_type}</b> operating in <b>{region}</b>, taking into account
        real-time traffic conditions, weather alerts, and NHVR compliance requirements.
        <br/><br/>
        The optimized route achieves <b>{((baseline_route['distance_km'] - route['distance_km']) / baseline_route['distance_km'] * 100):.1f}%</b>
        distance reduction compared to typical manual routing, resulting in significant fuel, cost, and emissions savings.
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))

        # Route comparison table
        story.append(Paragraph("Route Performance", styles['Heading2']))
        story.append(Spacer(1, 12))

        pct_shorter = ((baseline_route['distance_km'] - route['distance_km']) / baseline_route['distance_km']) * 100
        summary_data = [
            ["Metric", "Optimized Route", "Baseline Route", "Improvement"],
            ["Distance (km)", f"{route['distance_km']:.1f}", f"{baseline_route['distance_km']:.1f}", f"{pct_shorter:.1f}%"],
            ["Duration (h)", f"{route['duration_hours']:.1f}", f"{baseline_route['duration_hours']:.1f}", ""],
        ]

        table = Table(summary_data, colWidths=[1.8*inch, 2*inch, 2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 20))

        # Savings breakdown
        story.append(Paragraph("Environmental & Financial Impact", styles['Heading2']))
        story.append(Spacer(1, 12))
        savings_text = f"""
        <b>Fuel Savings:</b> {fuel_savings:.1f} litres<br/>
        <b>Cost Savings:</b> ${cost_savings:.2f} AUD (at ${Config.FUEL_PRICE_AUD_PER_LITRE:.2f}/L)<br/>
        <b>CO₂ Reduction:</b> {co2_savings:.1f} kg<br/>
        <b>Baseline CO₂:</b> {baseline_route['distance_km'] * fuel_rate * Config.CO2_PER_LITRE:.1f} kg |
        <b>Optimized CO₂:</b> {route['distance_km'] * fuel_rate * Config.CO2_PER_LITRE:.1f} kg
        """
        story.append(Paragraph(savings_text, styles['Normal']))
        story.append(Spacer(1, 20))

        # Traffic incidents section
        if traffic_incidents:
            story.append(Paragraph("Traffic Incidents Considered", styles['Heading2']))
            story.append(Spacer(1, 12))
            incident_data = [["Incident Type", "Road", "Severity", "Delay"]]
            for inc in traffic_incidents:
                incident_data.append([
                    inc.get('type', 'N/A').title(),
                    inc.get('road', 'N/A'),
                    inc.get('severity', 'N/A').title(),
                    f"{inc.get('delay_minutes', 0)} min"
                ])
            inc_table = Table(incident_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1*inch])
            inc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(inc_table)
            story.append(Spacer(1, 20))

        # Weather alerts section
        if weather_alerts:
            story.append(Paragraph("Weather Alerts Considered", styles['Heading2']))
            story.append(Spacer(1, 12))
            for alert in weather_alerts:
                weather_text = f"""
                <b>Type:</b> {alert.get('type', 'N/A').title()}<br/>
                <b>Severity:</b> <font color="{'red' if alert.get('severity') in ['high', 'extreme'] else 'black'}">{alert.get('severity', 'N/A').title()}</font><br/>
                <b>Message:</b> {alert.get('message', 'N/A')}<br/><br/>
                """
                story.append(Paragraph(weather_text, styles['Normal']))

        # Route details
        story.append(Paragraph("Route Details", styles['Heading2']))
        story.append(Spacer(1, 12))

        start = route.get('start', {})
        end = route.get('end', {})
        waypoints = route.get('route', [])

        details_text = f"""
        <b>Start Location:</b> {start.get('address', 'N/A')}<br/>
        <b>End Location:</b> {end.get('address', 'N/A')}<br/>
        <b>Vehicle Class:</b> {vehicle_type}<br/>
        <b>Waypoint Count:</b> {len(waypoints)}<br/>
        <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Report ID:</b> {os.path.basename(output_path).replace('.pdf', '')}
        """
        story.append(Paragraph(details_text, styles['Normal']))
        story.append(Spacer(1, 20))

        # Compliance summary
        story.append(Paragraph("Compliance Notes", styles['Heading2']))
        story.append(Spacer(1, 12))
        compliance_text = f"""
        Route calculated in accordance with National Heavy Vehicle Regulator (NHVR) standards.
        Driver fatigue limits have been considered. Please ensure all CoR obligations are met
        including vehicle roadworthiness, load securing, and driver licensing requirements.
        <br/><br/>
        <i>For detailed compliance information, consult the full compliance report or contact a NHVR accredited expert.</i>
        """
        story.append(Paragraph(compliance_text, styles['Normal']))

        doc.build(story)
        logger.info(f"Enhanced PDF report saved to: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise

def generate_gpx_route(route: Dict[str, Any], output_path: str) -> str:
    """
    Generates a GPX file for GPS navigation systems.

    Args:
        route: Optimized route dictionary
        output_path: Path to save GPX file

    Returns:
        Path to generated GPX file
    """
    try:
        waypoints = route.get('route', [])
        if not waypoints:
            raise ValueError("No waypoints in route")

        gpx_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        gpx_content += '<gpx version="1.1" creator="Smart Route Optimizer" '
        gpx_content += 'xmlns="http://www.topografix.com/GPX/1/1">\n'

        for i, point in enumerate(waypoints):
            lat = point['lat']
            lng = point['lng']
            name = point.get('name', f'Waypoint {i+1}')

            gpx_content += f'  <wpt lat="{lat}" lon="{lng}">\n'
            gpx_content += f'    <name>{name}</name>\n'
            gpx_content += '  </wpt>\n'

        # Add route as track
        gpx_content += '  <trk>\n'
        gpx_content += '    <name>Optimized Route</name>\n'
        gpx_content += '    <trkseg>\n'
        for point in waypoints:
            gpx_content += f'      <trkpt lat="{point["lat"]}" lon="{point["lng"]}"></trkpt>\n'
        gpx_content += '    </trkseg>\n'
        gpx_content += '  </trk>\n'

        gpx_content += '</gpx>'

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(gpx_content)

        logger.info(f"GPX file saved to: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"GPX generation failed: {e}")
        raise
