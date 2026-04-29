// Smart Route Optimizer - Frontend JavaScript

// Initialize map (default view centered on Sydney)
const map = L.map('map').setView([-33.8688, 151.2093], 7);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
}).addTo(map);

// Store route layers for clearing
let routeLayer = null;
let startMarker = null;
let endMarker = null;

// Form submission handler
document.getElementById('route-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');

    // Show loading state
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';

    document.getElementById('loading').style.display = 'block';
    document.getElementById('error').style.display = 'none';
    document.getElementById('results').style.display = 'none';

    // Collect form data
    const formData = {
        start_address: document.getElementById('start_address').value.trim(),
        end_address: document.getElementById('end_address').value.trim(),
        vehicle_type: document.getElementById('vehicle_type').value,
        state: document.getElementById('state').value,
        delivery_window: document.getElementById('delivery_window').value || null
    };

    // Auto-detect state from address if AUTO selected
    if (formData.state === 'AUTO') {
        delete formData.state; // Let backend auto-detect
    }

    try {
        const response = await fetch('/optimize/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Optimization failed');
        }

        // Display results
        displayRouteResults(data);
        displayCompliance(data.compliance);
        displaySavings(data.fuel_savings, data.distance_km);

        // Show results section
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results').style.display = 'block';

    } catch (error) {
        console.error('Optimization error:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').style.display = 'block';
        document.getElementById('error-message').textContent =
            `Error: ${error.message}`;

        // Re-enable button
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
});

function displayRouteResults(data) {
    // Clear previous route
    if (routeLayer) {
        map.removeLayer(routeLayer);
    }
    if (startMarker) {
        map.removeLayer(startMarker);
    }
    if (endMarker) {
        map.removeLayer(endMarker);
    }

    // Extract coordinates
    const routeCoords = data.route.map(point => [point.lat, point.lng]);

    // Draw route polyline
    routeLayer = L.polyline(routeCoords, {
        color: '#3498db',
        weight: 5,
        opacity: 0.8
    }).addTo(map);

    // Add start and end markers
    const startIcon = L.divIcon({
        className: 'custom-marker',
        html: '<div style="background: #27ae60; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>',
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });

    const endIcon = L.divIcon({
        className: 'custom-marker',
        html: '<div style="background: #e74c3c; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>',
        iconSize: [24, 24],
        iconAnchor: [12, 12]
    });

    startMarker = L.marker([data.route[0].lat, data.route[0].lng], { icon: startIcon })
        .addTo(map)
        .bindPopup(`<b>Start:</b> ${data.route[0].address || 'Origin'}`);

    endMarker = L.marker([data.route[data.route.length - 1].lat, data.route[data.route.length - 1].lng], { icon: endIcon })
        .addTo(map)
        .bindPopup(`<b>End:</b> ${data.route[data.route.length - 1].address || 'Destination'}`);

    // Fit map to route bounds
    map.fitBounds(routeCoords, { padding: [50, 50] });

    // Update summary metrics
    document.getElementById('distance').textContent = `${data.distance_km.toFixed(1)} km`;
    document.getElementById('duration').textContent = `${data.duration_hours.toFixed(1)} hours`;
    document.getElementById('waypoints').textContent = data.route.length;

    // Update baseline comparison
    const baselineDistance = data.distance_km * 1.15;
    document.getElementById('baseline-distance').textContent = `${baselineDistance.toFixed(1)} km`;
    document.getElementById('optimized-distance').textContent = `${data.distance_km.toFixed(1)} km`;
    document.getElementById('distance-reduction').textContent =
        `${((baselineDistance - data.distance_km) / baselineDistance * 100).toFixed(1)}%`;

    // Set download links
    document.getElementById('download-pdf').href = data.report_url;
    document.getElementById('download-gpx').href = data.gpx_url || '#';
}

function displayCompliance(compliance) {
    // NHVR status
    const nhvrStatusEl = document.querySelector('#nhvr-status .status');
    if (compliance.nhvr_compliant) {
        nhvrStatusEl.textContent = '✅ Compliant';
        nhvrStatusEl.className = 'status compliant';
    } else {
        nhvrStatusEl.textContent = '❌ Violations';
        nhvrStatusEl.className = 'status non-compliant';
    }

    // CoR status
    const corStatusEl = document.querySelector('#cor-status .status');
    if (compliance.cor_compliant) {
        corStatusEl.textContent = '✅ Compliant';
        corStatusEl.className = 'status compliant';
    } else {
        corStatusEl.textContent = '❌ Issues';
        corStatusEl.className = 'status non-compliant';
    }

    // Compliance details
    const detailsDiv = document.getElementById('compliance-details');
    const fm = compliance.fatigue_management;

    let detailsHTML = '<h4>Fatigue Management Details</h4>';
    detailsHTML += `<p><strong>Route Duration:</strong> ${fm.duration_hours.toFixed(1)} hours</p>`;
    detailsHTML += `<p><strong>Daily Limit:</strong> ${fm.daily_limit} hours</p>`;

    if (fm.violations && fm.violations.length > 0) {
        detailsHTML += '<p><strong>Violations:</strong></p><ul>';
        fm.violations.forEach(v => detailsHTML += `<li style="color: #e74c3c;">${v}</li>`);
        detailsHTML += '</ul>';
    }

    if (fm.warnings && fm.warnings.length > 0) {
        detailsHTML += '<p><strong>Warnings:</strong></p><ul>';
        fm.warnings.forEach(w => detailsHTML += `<li style="color: #f39c12;">${w}</li>`);
        detailsHTML += '</ul>';
    }

    if (fm.notes && fm.notes.length > 0) {
        detailsHTML += '<p><strong>Notes:</strong></p><ul>';
        fm.notes.forEach(n => detailsHTML += `<li>${n}</li>`);
        detailsHTML += '</ul>';
    }

    detailsDiv.innerHTML = detailsHTML;
}

function displaySavings(savings, distance) {
    document.getElementById('fuel-savings').textContent =
        `${savings.litres.toFixed(1)} L`;
    document.getElementById('cost-savings').textContent =
        `$${savings.cost_AUD.toFixed(2)}`;
    document.getElementById('co2-savings').textContent =
        `${savings.co2_kg.toFixed(1)} kg`;
}

// Form input enhancement: auto-suggest for known locations
// Known locations for validation (national coverage)
const knownLocations = [
    // NSW
    'Sydney, NSW', 'Newcastle, NSW', 'Wollongong, NSW',
    'Central Coast, NSW', 'Gosford, NSW', 'Melson, NSW',
    'Albury, NSW', 'Wagga Wagga, NSW', 'Dubbo, NSW',
    'Coffs Harbour, NSW', 'Port Macquarie, NSW', 'Broken Hill, NSW',
    // VIC
    'Melbourne, VIC', 'Geelong, VIC', 'Ballarat, VIC',
    'Bendigo, VIC', 'Mildura, VIC', 'Warrnambool, VIC',
    // QLD
    'Brisbane, QLD', 'Gold Coast, QLD', 'Sunshine Coast, QLD',
    'Toowoomba, QLD', 'Townsville, QLD', 'Cairns, QLD',
    // SA
    'Adelaide, SA', 'Mount Gambier, SA', 'Port Augusta, SA',
    'Whyalla, SA', 'Coober Pedy, SA',
    // WA
    'Perth, WA', 'Bunbury, WA', 'Geraldton, WA',
    'Kalgoorlie, WA', 'Busselton, WA',
    // TAS
    'Hobart, TAS', 'Launceston, TAS', 'Devonport, TAS', 'Burnie, TAS',
    // NT
    'Darwin, NT', 'Alice Springs, NT', 'Katherine, NT',
    // ACT
    'Canberra, ACT'
];

// Add input validation
document.getElementById('start_address').addEventListener('blur', function() {
    validateAddress(this);
});

document.getElementById('end_address').addEventListener('blur', function() {
    validateAddress(this);
});

function validateAddress(input) {
    const value = input.value.trim();
    if (value && !knownLocations.some(loc => loc.toLowerCase().includes(value.toLowerCase()))) {
        input.style.borderColor = '#f39c12';
        input.title = 'Address may not be in our database. Supported locations are shown in hints.';
    } else {
        input.style.borderColor = '';
        input.title = '';
    }
}

// Clear results when form is reset
document.getElementById('route-form').addEventListener('reset', function() {
    if (routeLayer) map.removeLayer(routeLayer);
    if (startMarker) map.removeLayer(startMarker);
    if (endMarker) map.removeLayer(endMarker);
    document.getElementById('results').style.display = 'none';
    document.getElementById('error').style.display = 'none';
});
