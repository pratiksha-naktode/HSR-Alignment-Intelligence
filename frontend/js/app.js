/* =========================================================
   HSR ALIGNMENT INTELLIGENCE
   Frontend Application
   ========================================================= */

let routeData = [];
let criterionChart = null;
let selectedCriterion = "forest";


/* =========================================================
   CRITERIA CONFIGURATION
   ========================================================= */

const criteriaConfig = {

    forest: {
        title: "Forest Area",
        unit: "km²",
        field: "C1_Forest Area_raw",
        calculation:
            "3.5 m ground footprint intersected with forest polygons.",
        assumption:
            "Total ground-impact width = 3.5 m; 1.75 m on each side of the HSR centerline.",
        interpretation:
            "Direct forest area intersected by the permanent ground footprint.",
        decimals: 6
    },

    agriculture: {
        title: "Agriculture Area",
        unit: "km²",
        field: "C2_Agriculture Area_raw",
        calculation:
            "3.5 m ground footprint intersected with agriculture polygons.",
        assumption:
            "Agricultural impact is calculated using the 3.5 m permanent ground footprint.",
        interpretation:
            "Direct agricultural area intersected by the permanent ground footprint.",
        decimals: 6
    },

    builtup: {
        title: "Built-up Area",
        unit: "km²",
        field: "C3_Built-up Area_raw",
        calculation:
            "3.5 m ground footprint intersected with built-up polygons.",
        assumption:
            "Built-up impact represents the permanent ground footprint intersecting built-up land.",
        interpretation:
            "Direct built-up area intersected by the permanent ground footprint.",
        decimals: 6
    },

    education: {
        title: "Educational Sector",
        unit: "facilities",
        field: "C4_Educational Sector_raw",
        calculation:
            "Educational facilities located within 100 m of the HSR centerline.",
        assumption:
            "The education analysis uses a 100 m centerline distance threshold.",
        interpretation:
            "Education facilities identified within the defined 100 m analysis distance.",
        decimals: 0
    },

    wetland: {
        title: "Wetland Impact",
        unit: "km²",
        field: "C5_Wetland Impact_raw",
        calculation:
            "3.5 m ground footprint intersected with wetland polygons.",
        assumption:
            "Wetland area is calculated from the permanent 3.5 m ground footprint.",
        interpretation:
            "Direct wetland area intersected by the permanent ground footprint.",
        decimals: 6
    },

    waterbody: {
        title: "Waterbody Intersections",
        unit: "features",
        field: "C6_Bhuvan Waterbody Polygon Intersections_raw",
        calculation:
            "Bhuvan waterbody polygon features intersected by the HSR analysis.",
        assumption:
            "This counts intersected Bhuvan polygon features, not verified unique waterbodies.",
        interpretation:
            "Number of intersected Bhuvan waterbody polygon features.",
        decimals: 0
    },

    esz: {
        title: "Nearest ESZ",
        unit: "km",
        field: "C7_Nearest ESZ_raw",
        calculation:
            "Closest perpendicular distance from the HSR centerline to the nearest identified ESZ.",
        assumption:
            "Route intersection and nearest-distance analysis are treated separately.",
        interpretation:
            "Distance from the route centerline to the nearest identified ESZ.",
        decimals: 6
    },

    length: {
        title: "Route Length",
        unit: "km",
        field: "C8_Route Length_raw",
        calculation:
            "Length of the HSR route centerline alignment.",
        assumption:
            "The supplied alignment geometry is used to calculate route length.",
        interpretation:
            "Calculated centerline alignment length.",
        decimals: 3
    },

    highway: {
        title: "Highway Interaction",
        unit: "interactions",
        field: "C9_Highway Intersection_raw",
        calculation:
            "Count of identified highway and major-road interactions.",
        assumption:
            "NH, SH and MDR are conceptually distinct. MDR is reported as not separately identifiable where unsupported by the supplied dataset.",
        interpretation:
            "Identified highway and major-road interactions.",
        decimals: 0
    }

};


/* =========================================================
   NAVIGATION
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const navItems = document.querySelectorAll(".nav-item");
    const sections = document.querySelectorAll(".page-section");
    const sectionLinks =
        document.querySelectorAll("[data-section-link]");


    function showSection(sectionId) {

        sections.forEach(section => {
            section.classList.remove("active");
        });

        navItems.forEach(item => {
            item.classList.remove("active");
        });


        const selectedSection =
            document.getElementById(sectionId);

        if (selectedSection) {
            selectedSection.classList.add("active");
        }


        const selectedNav = document.querySelector(
            `.nav-item[data-section="${sectionId}"]`
        );

        if (selectedNav) {
            selectedNav.classList.add("active");
        }


        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    }


    navItems.forEach(item => {

        item.addEventListener("click", () => {

            const sectionId = item.dataset.section;

            if (sectionId) {
                showSection(sectionId);
            }

        });

    });


    sectionLinks.forEach(link => {

        link.addEventListener("click", () => {

            const sectionId =
                link.dataset.sectionLink;

            if (sectionId) {
                showSection(sectionId);
            }

        });

    });


    /* Criterion buttons */

    const criterionButtons =
        document.querySelectorAll(".criterion-btn");


    criterionButtons.forEach(button => {

        button.addEventListener("click", () => {

            const criterionKey =
                button.dataset.criterion;


            criterionButtons.forEach(item => {
                item.classList.remove("active");
            });

            button.classList.add("active");


            updateCriterionAnalysis(criterionKey);

        });

    });


    console.log(
        "HSR Alignment Intelligence frontend initialized."
    );


    loadRouteData();

});


/* =========================================================
   LOAD REAL ROUTE DATA
   ========================================================= */

async function loadRouteData() {

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/api/routes"
        );


        if (!response.ok) {

            throw new Error(
                `API request failed: ${response.status}`
            );

        }


        const result = await response.json();

       routeData = result.data;

        updateOverviewKPIs();
        updateRouteExplorer("Route_1");
updateImpactAnalysis();  
        updateCriterionAnalysis("forest");


        console.log(
            "Verified route data loaded:",
            routeData
        );


    } catch (error) {

        console.error(
            "Route data loading failed:",
            error
        );

    }

}


/* =========================================================
   OVERVIEW KPIs
   ========================================================= */

function updateOverviewKPIs() {

    if (!routeData || routeData.length === 0) {
        return;
    }


    const routeCount = routeData.length;


    const routeNames = routeData
        .map(route => route.route)
        .join(" · ");


    const routesElement =
        document.getElementById("kpi-routes");

    const routeListElement =
        document.getElementById("kpi-route-list");


    if (routesElement) {
        routesElement.textContent = routeCount;
    }


    if (routeListElement) {
        routeListElement.textContent = routeNames;
    }


    const highwayTotal = routeData.reduce(
        (total, route) =>
            total + Number(
                route.highway_interactions || 0
            ),
        0
    );


    const highwayElement =
        document.getElementById("kpi-highways");


    if (highwayElement) {

        highwayElement.textContent =
            highwayTotal.toLocaleString();

    }

}


/* =========================================================
   GET CRITERION VALUES
   ========================================================= */

function getCriterionValues(criterionKey) {

    const criterion =
        criteriaConfig[criterionKey];


    if (!criterion || !routeData.length) {
        return [];
    }


    return routeData.map(route => ({

        route: route.route,

        value: Number(
            route[criterion.field]
        )

    }));

}


/* =========================================================
   FORMAT VALUES
   ========================================================= */

function formatCriterionValue(
    value,
    decimals
) {

    if (!Number.isFinite(value)) {
        return "—";
    }


    return value.toLocaleString(
        "en-IN",
        {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }
    );

}


/* =========================================================
   UPDATE CRITERION ANALYSIS
   ========================================================= */

function updateCriterionAnalysis(criterionKey) {

    const criterion =
        criteriaConfig[criterionKey];


    if (!criterion || !routeData.length) {
        return;
    }


    selectedCriterion = criterionKey;


    /* -----------------------------------------
       Text information
       ----------------------------------------- */

    const title =
        document.getElementById("criterion-title");

    const unit =
        document.getElementById("criterion-unit");

    const calculation =
        document.getElementById("criterion-calculation");

    const assumption =
        document.getElementById("criterion-assumption");

    const chartTitle =
        document.getElementById("criterion-chart-title");


    if (title) {
        title.textContent = criterion.title;
    }

    if (unit) {
        unit.textContent = criterion.unit;
    }

    if (calculation) {
        calculation.textContent =
            criterion.calculation;
    }

    if (assumption) {
        assumption.textContent =
            criterion.assumption;
    }

    if (chartTitle) {
        chartTitle.textContent =
            `${criterion.title} by Route`;
    }


    /* -----------------------------------------
       Route values
       ----------------------------------------- */

    const values =
        getCriterionValues(criterionKey);


    const r1 =
        values.find(item => item.route === "R1");

    const r2 =
        values.find(item => item.route === "R2");

    const r3 =
        values.find(item => item.route === "R3");


    const r1Element =
        document.getElementById("criterion-r1");

    const r2Element =
        document.getElementById("criterion-r2");

    const r3Element =
        document.getElementById("criterion-r3");


    if (r1Element) {
        r1Element.textContent =
            r1
                ? formatCriterionValue(
                    r1.value,
                    criterion.decimals
                )
                : "—";
    }


    if (r2Element) {
        r2Element.textContent =
            r2
                ? formatCriterionValue(
                    r2.value,
                    criterion.decimals
                )
                : "—";
    }


    if (r3Element) {
        r3Element.textContent =
            r3
                ? formatCriterionValue(
                    r3.value,
                    criterion.decimals
                )
                : "—";
    }


    document
        .querySelectorAll(
            "[id$='-unit']"
        )
        .forEach(element => {

            if (
                element.id === "criterion-unit" ||
                element.id.includes(
                    "criterion-r1-unit"
                ) ||
                element.id.includes(
                    "criterion-r2-unit"
                ) ||
                element.id.includes(
                    "criterion-r3-unit"
                )
            ) {
                element.textContent =
                    criterion.unit;
            }

        });


    /* -----------------------------------------
       Detailed table
       ----------------------------------------- */

    const tableBody =
        document.getElementById(
            "criterion-table-body"
        );


    if (tableBody) {

        tableBody.innerHTML = "";


        values.forEach(item => {

            const row =
                document.createElement("tr");


            row.innerHTML = `
                <td>${item.route}</td>

                <td>
                    ${formatCriterionValue(
                        item.value,
                        criterion.decimals
                    )}
                </td>

                <td>${criterion.unit}</td>

                <td>${criterion.interpretation}</td>
            `;


            tableBody.appendChild(row);

        });

    }


    /* -----------------------------------------
       Chart
       ----------------------------------------- */

    updateCriterionChart(criterionKey);

}


/* =========================================================
   CRITERION BAR CHART
   ========================================================= */

function updateCriterionChart(criterionKey) {

    const criterion =
        criteriaConfig[criterionKey];


    if (!criterion || !routeData.length) {
        return;
    }


    const canvas =
        document.getElementById(
            "criterionChart"
        );


    if (!canvas) {
        return;
    }


    const values =
        getCriterionValues(criterionKey);


    const labels =
        values.map(item => item.route);


    const data =
        values.map(item => item.value);


    const context =
        canvas.getContext("2d");


    if (criterionChart) {
        criterionChart.destroy();
    }


    criterionChart = new Chart(
        context,
        {

            type: "bar",


            data: {

                labels: labels,

                datasets: [

                    {
                        label:
                            `${criterion.title} (${criterion.unit})`,

                        data: data,

                        borderWidth: 1,

                        borderRadius: 3,

                        backgroundColor: [
                            "#1769AA",
                            "#2F80ED",
                            "#4E8B57"
                        ],

                        borderColor: [
                            "#1769AA",
                            "#2F80ED",
                            "#4E8B57"
                        ]

                    }

                ]

            },


            options: {

                responsive: true,

                maintainAspectRatio: false,


                plugins: {

                    legend: {
                        display: true
                    },


                    tooltip: {

                        callbacks: {

                            label: function(context) {

                                return `${context.dataset.label}: ${
                                    formatCriterionValue(
                                        context.raw,
                                        criterion.decimals
                                    )
                                }`;

                            }

                        }

                    }

                },


                scales: {

                    y: {

                        beginAtZero: true,

                        title: {

                            display: true,

                            text: criterion.unit

                        }

                    },


                    x: {

                        title: {

                            display: true,

                            text: "HSR Route"

                        }

                    }

                }

            }

        }
    );

}

/* =========================================================
   ROUTE EXPLORER
   ========================================================= */

    /* =========================================================
   ROUTE EXPLORER
   ========================================================= */

function updateRouteExplorer(routeId) {

    if (!routeData || routeData.length === 0) {
        console.warn("Route data not loaded");
        return;
    }

    const normalizedId = String(routeId)
        .replace("Route_", "R")
        .replace("Route ", "R")
        .trim();

    const route = routeData.find(item => {

        const id = String(item.route)
            .replace("Route_", "R")
            .replace("Route ", "R")
            .trim();

        return id === normalizedId;
    });

    if (!route) {
        console.warn(
            "Route not found:",
            routeId,
            normalizedId,
            routeData
        );
        return;
    }


    /* ============================
       SELECTED ROUTE
       ============================ */

    const routeName =
        document.getElementById("selected-route-name");

    if (routeName) {
        routeName.textContent =
            `Route ${normalizedId.replace("R", "")} — ${normalizedId}`;
    }


    /* ============================
       ROUTE LENGTH
       ============================ */

    const length =
        document.getElementById("route-length");

    if (length) {
        length.textContent =
            `${Number(
                route["C8_Route Length_raw"] || 0
            ).toFixed(3)} km`;
    }


    /* ============================
       ENVIRONMENT
       ============================ */

    const forest =
        document.getElementById("route-forest");

    const agriculture =
        document.getElementById("route-agriculture");

    const builtup =
        document.getElementById("route-builtup");

    const wetland =
        document.getElementById("route-wetland");

    const education =
        document.getElementById("route-education");

    const waterbody =
        document.getElementById("route-waterbody");


    if (forest) {
        forest.textContent =
            `${Number(
                route["C1_Forest Area_raw"] || 0
            ).toFixed(6)} km²`;
    }

    if (agriculture) {
        agriculture.textContent =
            `${Number(
                route["C2_Agriculture Area_raw"] || 0
            ).toFixed(6)} km²`;
    }

    if (builtup) {
        builtup.textContent =
            `${Number(
                route["C3_Built-up Area_raw"] || 0
            ).toFixed(6)} km²`;
    }

    if (wetland) {
        wetland.textContent =
            `${Number(
                route["C5_Wetland Impact_raw"] || 0
            ).toFixed(6)} km²`;
    }

    if (education) {
        education.textContent =
            `${Number(
                route["C4_Educational Sector_raw"] || 0
            )} facilities`;
    }

    if (waterbody) {
        waterbody.textContent =
            `${Number(
                route[
                    "C6_Bhuvan Waterbody Polygon Intersections_raw"
                ] || 0
            )} features`;
    }


    /* ============================
       ESZ
       ============================ */

    const eszDistance =
        document.getElementById("route-esz-distance");

    const eszName =
        document.getElementById("route-esz-name");

    if (eszDistance) {
        eszDistance.textContent =
            `${Number(
                route["C7_Nearest ESZ_raw"] || 0
            ).toFixed(3)} km`;
    }

    if (eszName) {
        eszName.textContent =
            route.nearest_esz_name ||
            "Nearest identified ESZ";
    }


    /* ============================
       HIGHWAY COUNTERS
       ============================ */

    const infrastructureFields = {

        "route-nh":
            "nh_count",

        "route-sh":
            "sh_count",

        "route-expressway":
            "state_expressway_count",

        "route-major-road":
            "other_major_road_count",

        "route-mdr":
            "mdr_count",

        "route-highway-total":
            "highway_interactions"
    };


    Object.entries(
        infrastructureFields
    ).forEach(([elementId, field]) => {

        const element =
            document.getElementById(elementId);

        if (element) {

            element.textContent =
                Number(
                    route[field] || 0
                ).toLocaleString();
        }
    });


    /* ============================
       ESZ METER
       ============================ */

    const meter =
        document.getElementById("esz-meter-fill");

    if (meter) {

        const esz =
            Number(
                route["C7_Nearest ESZ_raw"] || 0
            );

        meter.style.width =
            `${Math.min((esz / 5) * 100, 100)}%`;
    }


    /* ============================
       UPDATE CHARTS
       ============================ */

    updateRouteExplorerCharts(
        normalizedId
    );


    console.log(
        "Route Explorer switched to:",
        normalizedId,
        route
    );
}
/* =========================================================
   ROUTE EXPLORER CHARTS
   ========================================================= */

let routeEnvironmentalChart = null;
let routeHighwayChart = null;
let routeIntersectionChart = null;


/* ---------------------------------------------------------
   UPDATE ALL ROUTE EXPLORER CHARTS
   --------------------------------------------------------- */

/* =========================================================
   ROUTE EXPLORER CHARTS
   Native Canvas Renderer
   ========================================================= */

function updateRouteExplorerCharts(routeId) {

    const route = routeData.find(item => {
        const id = String(item.route)
            .replace("Route_", "R")
            .replace("Route ", "R")
            .trim();

        return id === routeId;
    });

    if (!route) {
        console.warn("Route not found for charts:", routeId);
        return;
    }

    function setupCanvas(id) {

        const canvas = document.getElementById(id);

        if (!canvas) {
            console.error("Canvas not found:", id);
            return null;
        }

        const parent = canvas.parentElement;

        const width = parent.clientWidth || 600;
        const height = parent.clientHeight || 300;

        canvas.width = width;
        canvas.height = height;

        canvas.style.width = "100%";
        canvas.style.height = "100%";

        const ctx = canvas.getContext("2d");

        ctx.clearRect(0, 0, width, height);

        return {
            canvas,
            ctx,
            width,
            height
        };
    }


    function drawBarChart(id, labels, values, title) {

        const chart = setupCanvas(id);

        if (!chart) return;

        const {ctx, width, height} = chart;

        const left = 65;
        const right = 25;
        const top = 35;
        const bottom = 55;

        const chartWidth = width - left - right;
        const chartHeight = height - top - bottom;

        const maxValue = Math.max(...values, 1);

        ctx.font = "12px Arial";
        ctx.fillStyle = "#667085";
        ctx.textAlign = "center";

        const barWidth =
            chartWidth / values.length * 0.55;

        values.forEach((value, index) => {

            const x =
                left +
                (index + 0.5) *
                (chartWidth / values.length);

            const barHeight =
                (value / maxValue) * chartHeight;

            const y =
                top +
                chartHeight -
                barHeight;

            ctx.fillStyle = [
                "#4E8B57",
                "#C88719",
                "#7656A6",
                "#4A90C2",
                "#1769AA"
            ][index] || "#1769AA";

            ctx.fillRect(
                x - barWidth / 2,
                y,
                barWidth,
                barHeight
            );

            ctx.fillStyle = "#172033";
            ctx.font = "bold 12px Arial";

            ctx.fillText(
                Number(value).toFixed(3),
                x,
                y - 8
            );

            ctx.fillStyle = "#667085";
            ctx.font = "11px Arial";

            ctx.fillText(
                labels[index],
                x,
                height - 20
            );
        });


        ctx.fillStyle = "#172033";
        ctx.font = "bold 12px Arial";
        ctx.textAlign = "left";

        ctx.fillText(
            title,
            10,
            18
        );
    }


    /* ============================
       ENVIRONMENTAL CHART
       ============================ */

    drawBarChart(
        "routeEnvironmentalChart",

        [
            "Forest",
            "Agriculture",
            "Built-up",
            "Wetland"
        ],

        [
            Number(route["C1_Forest Area_raw"]) || 0,
            Number(route["C2_Agriculture Area_raw"]) || 0,
            Number(route["C3_Built-up Area_raw"]) || 0,
            Number(route["C5_Wetland Impact_raw"]) || 0
        ],

        "Impact Area (km²)"
    );


    /* ============================
       HIGHWAY CHART
       ============================ */

    drawBarChart(
        "routeHighwayChart",

        [
            "NH",
            "SH",
            "Expressway",
            "Major Road",
            "MDR"
        ],

        [
            Number(route.nh_count) || 0,
            Number(route.sh_count) || 0,
            Number(route.state_expressway_count) || 0,
            Number(route.other_major_road_count) || 0,
            Number(route.mdr_count) || 0
        ],

        "Highway Interactions"
    );


    /* ============================
       CENTERLINE INTERSECTION
       ============================ */

    drawBarChart(
        "routeIntersectionChart",

        [
            "Forest",
            "Agriculture",
            "Built-up",
            "Wetland",
            "Water"
        ],

        [
            Number(route.forest_intersection_length_km) || 0,
            Number(route.agriculture_intersection_length_km) || 0,
            Number(route.builtup_intersection_length_km) || 0,
            Number(route.wetland_intersection_length_km) || 0,
            Number(route.waterbody_intersection_length_km) || 0
        ],

        "Centerline Intersection Length (km)"
    );


    /* ============================
       DOUGHNUT / COMPOSITION
       ============================ */

    const doughnut = setupCanvas(
        "routeImpactDoughnut"
    );

    if (doughnut) {

        const values = [

            Number(route["C1_Forest Area_raw"]) || 0,

            Number(route["C2_Agriculture Area_raw"]) || 0,

            Number(route["C3_Built-up Area_raw"]) || 0,

            Number(route["C5_Wetland Impact_raw"]) || 0
        ];

        const labels = [
            "Forest",
            "Agriculture",
            "Built-up",
            "Wetland"
        ];

        const colors = [
            "#4E8B57",
            "#C88719",
            "#7656A6",
            "#4A90C2"
        ];

        const total =
            values.reduce(
                (sum, value) => sum + value,
                0
            );

        const cx =
            doughnut.width / 2;

        const cy =
            doughnut.height / 2;

        const radius =
            Math.min(
                doughnut.width,
                doughnut.height
            ) * 0.32;

        let startAngle = -Math.PI / 2;

        values.forEach(
            (value, index) => {

                const angle =
                    total > 0
                        ? (value / total) *
                          Math.PI * 2
                        : 0;

                doughnut.ctx.beginPath();

                doughnut.ctx.moveTo(
                    cx,
                    cy
                );

                doughnut.ctx.arc(
                    cx,
                    cy,
                    radius,
                    startAngle,
                    startAngle + angle
                );

                doughnut.ctx.closePath();

                doughnut.ctx.fillStyle =
                    colors[index];

                doughnut.ctx.fill();

                startAngle += angle;
            }
        );


        /* centre */

        doughnut.ctx.beginPath();

        doughnut.ctx.arc(
            cx,
            cy,
            radius * 0.55,
            0,
            Math.PI * 2
        );

        doughnut.ctx.fillStyle = "#FFFFFF";

        doughnut.ctx.fill();


        doughnut.ctx.fillStyle =
            "#172033";

        doughnut.ctx.font =
            "bold 14px Arial";

        doughnut.ctx.textAlign =
            "center";

        doughnut.ctx.fillText(
            "Impact",
            cx,
            cy + 5
        );


        /* legend */

        doughnut.ctx.textAlign =
            "left";

        doughnut.ctx.font =
            "11px Arial";

        labels.forEach(
            (label, index) => {

                const x = 15;

                const y =
                    20 + index * 20;

                doughnut.ctx.fillStyle =
                    colors[index];

                doughnut.ctx.fillRect(
                    x,
                    y - 9,
                    10,
                    10
                );

                doughnut.ctx.fillStyle =
                    "#667085";

                doughnut.ctx.fillText(
                    label,
                    x + 16,
                    y
                );
            }
        );
    }


    console.log(
        "Route Explorer native charts rendered:",
        routeId
    );
}

/* Redraw when the route page becomes visible or the viewport changes. */
window.addEventListener('resize', () => {
    const select = document.getElementById('routeSelect');
    if (select && routeData.length) {
        window.requestAnimationFrame(() => updateRouteExplorerCharts(select.value));
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const routeNav = document.querySelector('.nav-item[data-section="routes"]');
    if (routeNav) {
        routeNav.addEventListener('click', () => {
            window.setTimeout(() => {
                const select = document.getElementById('routeSelect');
                if (select && routeData.length) {
                    updateRouteExplorerCharts(select.value);
                }
            }, 80);
        });
    }
});

/* =========================================================
   IMPACT ANALYSIS
   ========================================================= */

let impactComparisonChart = null;
let educationImpactChart = null;
let waterImpactChart = null;


function updateImpactAnalysis() {

    if (!routeData || routeData.length === 0) {
        return;
    }

    const routes = routeData.map(route => route.route);

    const forest = routeData.map(route =>
        Number(route["C1_Forest Area_raw"] || 0)
    );

    const agriculture = routeData.map(route =>
        Number(route["C2_Agriculture Area_raw"] || 0)
    );

    const builtup = routeData.map(route =>
        Number(route["C3_Built-up Area_raw"] || 0)
    );

    const wetland = routeData.map(route =>
        Number(route["C5_Wetland Impact_raw"] || 0)
    );

    const education = routeData.map(route =>
        Number(route["C4_Educational Sector_raw"] || 0)
    );

    const waterbody = routeData.map(route =>
        Number(
            route["C6_Bhuvan Waterbody Polygon Intersections_raw"] || 0
        )
    );

    const esz = routeData.map(route =>
        Number(route["C7_Nearest ESZ_raw"] || 0)
    );


    /* -----------------------------------------
       SUMMARY CARDS
       ----------------------------------------- */

    document.getElementById("impact-forest-value").textContent =
        Math.min(...forest).toFixed(6);

    document.getElementById("impact-agriculture-value").textContent =
        Math.min(...agriculture).toFixed(6);

    document.getElementById("impact-builtup-value").textContent =
        Math.min(...builtup).toFixed(6);

    document.getElementById("impact-wetland-value").textContent =
        Math.min(...wetland).toFixed(6);


    /* -----------------------------------------
       ENVIRONMENTAL CHART
       ----------------------------------------- */

    const impactCanvas =
        document.getElementById("impactComparisonChart");

    if (impactCanvas) {

        if (impactComparisonChart) {
            impactComparisonChart.destroy();
        }

        impactComparisonChart = new Chart(
            impactCanvas.getContext("2d"),
            {
                type: "bar",

                data: {
                    labels: routes,

                    datasets: [
                        {
                            label: "Forest",
                            data: forest,
                            backgroundColor: "#4E8B57"
                        },
                        {
                            label: "Agriculture",
                            data: agriculture,
                            backgroundColor: "#C88719"
                        },
                        {
                            label: "Built-up",
                            data: builtup,
                            backgroundColor: "#7656A6"
                        },
                        {
                            label: "Wetland",
                            data: wetland,
                            backgroundColor: "#4A90C2"
                        }
                    ]
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

                    plugins: {
                        legend: {
                            position: "bottom"
                        }
                    },

                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Area (km²)"
                            }
                        },

                        x: {
                            title: {
                                display: true,
                                text: "HSR Route"
                            }
                        }
                    }
                }
            }
        );
    }


    /* -----------------------------------------
       EDUCATION CHART
       ----------------------------------------- */

    const educationCanvas =
        document.getElementById("educationImpactChart");

    if (educationCanvas) {

        if (educationImpactChart) {
            educationImpactChart.destroy();
        }

        educationImpactChart = new Chart(
            educationCanvas.getContext("2d"),
            {
                type: "bar",

                data: {
                    labels: routes,

                    datasets: [
                        {
                            label: "Educational Facilities within 100 m",
                            data: education,
                            backgroundColor: "#1769AA"
                        }
                    ]
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

                    plugins: {
                        legend: {
                            display: false
                        }
                    },

                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Facilities"
                            }
                        }
                    }
                }
            }
        );
    }


    /* -----------------------------------------
       WATERBODY CHART
       ----------------------------------------- */

    const waterCanvas =
        document.getElementById("waterImpactChart");

    if (waterCanvas) {

        if (waterImpactChart) {
            waterImpactChart.destroy();
        }

        waterImpactChart = new Chart(
            waterCanvas.getContext("2d"),
            {
                type: "bar",

                data: {
                    labels: routes,

                    datasets: [
                        {
                            label: "Bhuvan Waterbody Polygon Intersections",
                            data: waterbody,
                            backgroundColor: "#4A90C2"
                        }
                    ]
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

                    plugins: {
                        legend: {
                            display: false
                        }
                    },

                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Features"
                            }
                        }
                    }
                }
            }
        );
    }


    /* -----------------------------------------
       TABLE
       ----------------------------------------- */

    routeData.forEach(route => {

        const suffix = route.route.toLowerCase().replace("_", "");

        const routeNumber =
            route.route.replace("Route_", "").toLowerCase();

        const r = route.route
            .replace("Route_", "r")
            .toLowerCase();


        document.getElementById(
            `impact-table-forest-${r}`
        ).textContent =
            Number(route["C1_Forest Area_raw"] || 0).toFixed(6);

        document.getElementById(
            `impact-table-agriculture-${r}`
        ).textContent =
            Number(route["C2_Agriculture Area_raw"] || 0).toFixed(6);

        document.getElementById(
            `impact-table-builtup-${r}`
        ).textContent =
            Number(route["C3_Built-up Area_raw"] || 0).toFixed(6);

        document.getElementById(
            `impact-table-wetland-${r}`
        ).textContent =
            Number(route["C5_Wetland Impact_raw"] || 0).toFixed(6);

        document.getElementById(
            `impact-table-education-${r}`
        ).textContent =
            Number(route["C4_Educational Sector_raw"] || 0);

        document.getElementById(
            `impact-table-water-${r}`
        ).textContent =
            Number(
                route[
                    "C6_Bhuvan Waterbody Polygon Intersections_raw"
                ] || 0
            );

        document.getElementById(
            `impact-table-esz-${r}`
        ).textContent =
            Number(route["C7_Nearest ESZ_raw"] || 0).toFixed(3);

    });

}
/* =========================================================
   ROUTE EXPLORER SELECTOR
   ========================================================= */

/* =========================================================
   CLEAN EXISTING GIS MAP PANELS
   Keep Station Search, remove Route Summary + AHP/TOPSIS
   ========================================================= */

function cleanGISMapPanels() {

    const iframe = document.getElementById("hsrMap");

    if (!iframe) {
        return;
    }

    function removeUnwantedPanels() {

        let mapDocument;

        try {
            mapDocument =
                iframe.contentDocument ||
                iframe.contentWindow.document;
        } catch (error) {
            console.warn(
                "Cannot access GIS map document:",
                error
            );
            return;
        }

        if (!mapDocument) {
            return;
        }


        /* -----------------------------------------
           Find elements containing specific headings
           ----------------------------------------- */

        const elements =
            mapDocument.querySelectorAll("div, section, aside");

        elements.forEach(element => {

            const text =
                element.textContent
                    .replace(/\s+/g, " ")
                    .trim();

            if (!text) {
                return;
            }


            /* HSR Route Summary */

            if (
                text.includes("HSR Route Summary") &&
                !text.includes("Station Candidate Search")
            ) {

                const panel =
                    findFloatingPanel(element);

                if (panel) {
                    panel.style.display = "none";
                }

            }


            /* AHP / TOPSIS Decision Analysis */

            if (
                (
                    text.includes("AHP") &&
                    text.includes("TOPSIS")
                ) &&
                !text.includes("Station Candidate Search")
            ) {

                const panel =
                    findFloatingPanel(element);

                if (panel) {
                    panel.style.display = "none";
                }

            }

        });

    }


    function findFloatingPanel(element) {

        let current = element;

        for (let i = 0; i < 8 && current; i++) {

            const style =
                mapDocument.defaultView.getComputedStyle(current);

            const rect =
                current.getBoundingClientRect();

            const position =
                style.position;

            /*
             * Folium/custom GIS panels are normally
             * positioned absolute/fixed.
             */

            if (
                (position === "absolute" ||
                 position === "fixed") &&
                rect.width > 250 &&
                rect.height > 80
            ) {

                return current;
            }

            current = current.parentElement;
        }

        return element;
    }


    /* Run once */

    removeUnwantedPanels();


    /*
     * Run again because some map controls/panels
     * may be created after the iframe loads.
     */

    setTimeout(removeUnwantedPanels, 500);
    setTimeout(removeUnwantedPanels, 1500);
    setTimeout(removeUnwantedPanels, 3000);

}


/* Run when existing GIS map finishes loading */

const hsrMap = document.getElementById("hsrMap");

if (hsrMap) {

    hsrMap.addEventListener(
        "load",
        cleanGISMapPanels
    );

}
/* =========================================================
   AHP / TOPSIS CHARTS
   ========================================================= */

function createDecisionCharts() {

    const weights = [
        16.94, 10.20, 9.44, 5.87, 20.02,
        6.63, 14.99, 8.74, 7.16
    ];

    const criteria = [
        "Forest",
        "Agriculture",
        "Built-up",
        "Education",
        "Wetland",
        "Waterbody",
        "ESZ",
        "Route Length",
        "Highway"
    ];


    const ahpCanvas = document.getElementById("ahpWeightChart");

    if (ahpCanvas) {

        new Chart(ahpCanvas.getContext("2d"), {
            type: "bar",

            data: {
                labels: criteria,

                datasets: [{
                    label: "AHP Weight (%)",
                    data: weights,
                    backgroundColor: "#1769AA"
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: "Weight (%)"
                        }
                    }
                }
            }
        });

    }


    const topsisCanvas =
        document.getElementById("topsisChart");

    if (topsisCanvas) {

        new Chart(topsisCanvas.getContext("2d"), {

            type: "bar",

            data: {

                labels: [
                    "Route 1",
                    "Route 2",
                    "Route 3"
                ],

                datasets: [{
                    label: "TOPSIS Score",

                    data: [
                        0.612012,
                        0.419965,
                        0.420054
                    ],

                    backgroundColor: [
                        "#1769AA",
                        "#2F80ED",
                        "#4E8B57"
                    ]
                }]

            },

            options: {

                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true,
                        max: 0.7,
                        title: {
                            display: true,
                            text: "TOPSIS Score"
                        }
                    }
                }

            }

        });

    }

}

createDecisionCharts();

/* =========================================================
   SENSITIVITY ANALYSIS
   ========================================================= */

const sensitivityData = {

    baseline: {
        name: "Baseline AHP",
        r1: 0.612012,
        r2: 0.419965,
        r3: 0.420054
    },

    equal: {
        name: "Equal Weights",
        r1: 0.540434,
        r2: 0.521867,
        r3: 0.390529
    },

    environmental: {
        name: "Environmental Focus",
        r1: 0.623205,
        r2: 0.387451,
        r3: 0.444094
    },

    agriculture: {
        name: "Agriculture Focus",
        r1: 0.627658,
        r2: 0.401517,
        r3: 0.401890
    },

    social: {
        name: "Social Development Focus",
        r1: 0.579886,
        r2: 0.459028,
        r3: 0.396266
    },

    infrastructure: {
        name: "Infrastructure Focus",
        r1: 0.604688,
        r2: 0.455733,
        r3: 0.424041
    },

    water: {
        name: "Water Environment Focus",
        r1: 0.666638,
        r2: 0.356767,
        r3: 0.428961
    },

    forest: {
        name: "Forest Focus",
        r1: 0.687211,
        r2: 0.346309,
        r3: 0.327491
    }

};


let sensitivityChart = null;


function updateSensitivityAnalysis(scenarioKey) {

    const scenario =
        sensitivityData[scenarioKey];

    if (!scenario) {
        return;
    }


    document.getElementById(
        "selectedScenarioName"
    ).textContent = scenario.name;


    document.getElementById(
        "selectedR1Score"
    ).textContent = scenario.r1.toFixed(6);


    document.getElementById(
        "selectedR2Score"
    ).textContent = scenario.r2.toFixed(6);


    document.getElementById(
        "selectedR3Score"
    ).textContent = scenario.r3.toFixed(6);


    const canvas =
        document.getElementById("sensitivityChart");

    if (!canvas) {
        return;
    }


    if (sensitivityChart) {
        sensitivityChart.destroy();
    }


    sensitivityChart = new Chart(
        canvas.getContext("2d"),
        {
            type: "bar",

            data: {

                labels: [
                    "Route 1",
                    "Route 2",
                    "Route 3"
                ],

                datasets: [{
                    label: "TOPSIS Score",

                    data: [
                        scenario.r1,
                        scenario.r2,
                        scenario.r3
                    ],

                    backgroundColor: [
                        "#1769AA",
                        "#2F80ED",
                        "#4E8B57"
                    ]
                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    },

                    tooltip: {

                        callbacks: {

                            label: function(context) {

                                return (
                                    "TOPSIS Score: " +
                                    context.raw.toFixed(6)
                                );

                            }

                        }

                    }

                },

                scales: {

                    y: {

                        beginAtZero: true,

                        max: 0.75,

                        title: {
                            display: true,
                            text: "TOPSIS Score"
                        }

                    },

                    x: {

                        title: {
                            display: true,
                            text: "HSR Route"
                        }

                    }

                }

            }

        }
    );

}


/* Scenario selector */

const sensitivitySelector =
    document.getElementById(
        "sensitivityScenario"
    );

if (sensitivitySelector) {

    sensitivitySelector.addEventListener(
        "change",
        function () {

            updateSensitivityAnalysis(
                this.value
            );

        }
    );

}


/* Initial scenario */

updateSensitivityAnalysis("baseline");

/* =========================================================
   ROUTE COMPARISON CHARTS
   ========================================================= */

function createComparisonCharts() {

    const routes = [
        "Route 1",
        "Route 2",
        "Route 3"
    ];


    /* -----------------------------------------
       ENVIRONMENT
       ----------------------------------------- */

    const environmentCanvas =
        document.getElementById(
            "environmentComparisonChart"
        );

    if (environmentCanvas) {

        new Chart(
            environmentCanvas.getContext("2d"),
            {
                type: "bar",

                data: {

                    labels: routes,

                    datasets: [

                        {
                            label: "Forest",
                            data: [
                                0.048307,
                                0.055493,
                                0.056215
                            ],
                            backgroundColor: "#4E8B57"
                        },

                        {
                            label: "Agriculture",
                            data: [
                                0.878612,
                                1.571022,
                                1.532198
                            ],
                            backgroundColor: "#C88719"
                        },

                        {
                            label: "Built-up",
                            data: [
                                0.781871,
                                0.736322,
                                0.793088
                            ],
                            backgroundColor: "#7656A6"
                        },

                        {
                            label: "Wetland",
                            data: [
                                0.024743,
                                0.063228,
                                0.044774
                            ],
                            backgroundColor: "#4A90C2"
                        }

                    ]

                },

                options: {

                    responsive: true,
                    maintainAspectRatio: false,

                    plugins: {
                        legend: {
                            position: "bottom"
                        }
                    },

                    scales: {

                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Area (km²)"
                            }
                        }

                    }

                }

            }
        );

    }


    /* -----------------------------------------
       HIGHWAYS
       ----------------------------------------- */

    const highwayCanvas =
        document.getElementById(
            "highwayComparisonChart"
        );

    if (highwayCanvas) {

        new Chart(
            highwayCanvas.getContext("2d"),
            {
                type: "bar",

                data: {

                    labels: routes,

                    datasets: [{
                        label: "Highway Interactions",

                        data: [
                            60,
                            55,
                            55
                        ],

                        backgroundColor: "#C62828"
                    }]

                },

                options: {

                    responsive: true,
                    maintainAspectRatio: false,

                    plugins: {
                        legend: {
                            display: false
                        }
                    },

                    scales: {

                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Interactions"
                            }
                        }

                    }

                }

            }
        );

    }


    /* -----------------------------------------
       EDUCATION
       ----------------------------------------- */

    const educationCanvas =
        document.getElementById(
            "educationComparisonChart"
        );

    if (educationCanvas) {

        new Chart(
            educationCanvas.getContext("2d"),
            {
                type: "bar",

                data: {

                    labels: routes,

                    datasets: [{
                        label: "Education Facilities",

                        data: [
                            39,
                            31,
                            39
                        ],

                        backgroundColor: "#1769AA"
                    }]

                },

                options: {

                    responsive: true,
                    maintainAspectRatio: false,

                    plugins: {
                        legend: {
                            display: false
                        }
                    },

                    scales: {

                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Facilities within 100 m"
                            }
                        }

                    }

                }

            }
        );

    }

}


createComparisonCharts();

/* =========================================================
   REPORTS & EXPORT
   ========================================================= */

/**
 * Convert an array of objects into CSV.
 */
function convertToCSV(data) {

    if (!data || data.length === 0) {
        return "";
    }

    const headers = Object.keys(data[0]);

    const rows = data.map(row => {
        return headers.map(header => {

            let value = row[header];

            if (value === null || value === undefined) {
                value = "";
            }

            value = String(value);

            if (
                value.includes(",") ||
                value.includes('"') ||
                value.includes("\n")
            ) {
                value = '"' + value.replace(/"/g, '""') + '"';
            }

            return value;

        }).join(",");
    });

    return [headers.join(","), ...rows].join("\n");
}


/**
 * Download locally generated data.
 */
function downloadFile(content, filename, mimeType) {

    const blob = new Blob(
        [content],
        { type: mimeType }
    );

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = filename;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    setTimeout(() => {
        URL.revokeObjectURL(url);
    }, 1000);
}


/**
 * Export complete route comparison.
 */
function exportRouteComparison() {

    if (!routeData || routeData.length === 0) {
        alert("Route data is not available.");
        return;
    }

    const csv = convertToCSV(routeData);

    downloadFile(
        csv,
        "HSR_Route_Comparison.csv",
        "text/csv;charset=utf-8;"
    );
}


/**
 * Export AHP + TOPSIS results.
 */
function exportDecisionResults() {

    const decisionData = [

        {
            route: "R1",
            topsis_score: 0.612012,
            topsis_rank: 1
        },

        {
            route: "R2",
            topsis_score: 0.419965,
            topsis_rank: 3
        },

        {
            route: "R3",
            topsis_score: 0.420054,
            topsis_rank: 2
        }

    ];

    const csv = convertToCSV(decisionData);

    downloadFile(
        csv,
        "HSR_AHP_TOPSIS_Results.csv",
        "text/csv;charset=utf-8;"
    );
}


/**
 * Export sensitivity scenarios.
 */
function exportSensitivityResults() {

    const sensitivityRows = [

        {
            scenario: "Baseline AHP",
            R1: 0.612012,
            R2: 0.419965,
            R3: 0.420054
        },

        {
            scenario: "Equal Weights",
            R1: 0.540434,
            R2: 0.521867,
            R3: 0.390529
        },

        {
            scenario: "Environmental Focus",
            R1: 0.623205,
            R2: 0.387451,
            R3: 0.444094
        },

        {
            scenario: "Agriculture Focus",
            R1: 0.627658,
            R2: 0.401517,
            R3: 0.401890
        },

        {
            scenario: "Social Development Focus",
            R1: 0.579886,
            R2: 0.459028,
            R3: 0.396266
        },

        {
            scenario: "Infrastructure Focus",
            R1: 0.604688,
            R2: 0.455733,
            R3: 0.424041
        },

        {
            scenario: "Water Environment Focus",
            R1: 0.666638,
            R2: 0.356767,
            R3: 0.428961
        },

        {
            scenario: "Forest Focus",
            R1: 0.687211,
            R2: 0.346309,
            R3: 0.327491
        }

    ];

    const csv = convertToCSV(sensitivityRows);

    downloadFile(
        csv,
        "HSR_Sensitivity_Analysis.csv",
        "text/csv;charset=utf-8;"
    );
}


/**
 * Export engineering assumptions.
 */
function exportEngineeringParameters() {

    const parameters = [

        {
            parameter: "Ground Footprint",
            value: 3.5,
            unit: "m"
        },

        {
            parameter: "Offset Each Side",
            value: 1.75,
            unit: "m"
        },

        {
            parameter: "Track Gauge",
            value: 1.435,
            unit: "m"
        },

        {
            parameter: "Planning ROW Width",
            value: 17.5,
            unit: "m"
        },

        {
            parameter: "Education Search Distance",
            value: 100,
            unit: "m"
        },

        {
            parameter: "Spatial CRS",
            value: "EPSG:32643",
            unit: ""
        }

    ];

    const csv = convertToCSV(parameters);

    downloadFile(
        csv,
        "HSR_Engineering_Parameters.csv",
        "text/csv;charset=utf-8;"
    );
}


/**
 * Export a consolidated JSON decision-support package.
 */
function exportCompleteReport() {

    const report = {

        project: {
            name: "HSR Alignment Intelligence",
            description:
                "GIS-Based Route Evaluation & Decision Support System"
        },

        routes: routeData || [],

        engineering_parameters: {
            ground_footprint_m: 3.5,
            buffer_each_side_m: 1.75,
            track_gauge_m: 1.435,
            planning_row_width_m: 17.5,
            education_search_distance_m: 100,
            crs: "EPSG:32643"
        },

        ahp_weights: {
            forest_area: 0.1694,
            agriculture_area: 0.1020,
            builtup_area: 0.0944,
            education: 0.0587,
            wetland: 0.2002,
            waterbody: 0.0663,
            esz: 0.1499,
            route_length: 0.0874,
            highway_intersection: 0.0716
        },

        topsis_results: [
            {
                route: "R1",
                score: 0.612012,
                rank: 1
            },
            {
                route: "R2",
                score: 0.419965,
                rank: 3
            },
            {
                route: "R3",
                score: 0.420054,
                rank: 2
            }
        ],

        sensitivity_analysis: [
            {
                scenario: "Baseline AHP",
                R1: 0.612012,
                R2: 0.419965,
                R3: 0.420054
            },
            {
                scenario: "Equal Weights",
                R1: 0.540434,
                R2: 0.521867,
                R3: 0.390529
            },
            {
                scenario: "Environmental Focus",
                R1: 0.623205,
                R2: 0.387451,
                R3: 0.444094
            },
            {
                scenario: "Agriculture Focus",
                R1: 0.627658,
                R2: 0.401517,
                R3: 0.401890
            },
            {
                scenario: "Social Development Focus",
                R1: 0.579886,
                R2: 0.459028,
                R3: 0.396266
            },
            {
                scenario: "Infrastructure Focus",
                R1: 0.604688,
                R2: 0.455733,
                R3: 0.424041
            },
            {
                scenario: "Water Environment Focus",
                R1: 0.666638,
                R2: 0.356767,
                R3: 0.428961
            },
            {
                scenario: "Forest Focus",
                R1: 0.687211,
                R2: 0.346309,
                R3: 0.327491
            }
        ]

    };

    downloadFile(
        JSON.stringify(report, null, 2),
        "HSR_Alignment_Intelligence_Report.json",
        "application/json;charset=utf-8;"
    );
}

window.exportRouteComparison = exportRouteComparison;
window.exportDecisionResults = exportDecisionResults;
window.exportSensitivityResults = exportSensitivityResults;
window.exportEngineeringParameters = exportEngineeringParameters;
window.exportCompleteReport = exportCompleteReport;