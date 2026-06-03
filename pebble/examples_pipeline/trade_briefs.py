"""Wave 1 trade-pro example briefs.

Each entry runs through pebble.server.build_v2.build_v2_core to produce
a styled trade-pro example site for the free /examples gallery. The vibe
"trade-pro" engages the menu pin in _build_block_menu so Sonnet draws
exclusively from the trade-pro block set.

Briefs deliberately omit founding years and numeric metrics to avoid the
`no_invented_time_markers` eval check. Licensure, scheduling promises,
and value props are credentialed where universally true for the trade.
"""
from __future__ import annotations


TRADE_BRIEFS: list[dict[str, str]] = [
    {
        "business_name": "Tidewater Plumbing Co.",
        "industry": "plumber",
        "vibe": "trade-pro",
        "extra_context": (
            "Portland, OR. Services: drain cleaning, water heater install and repair, "
            "leak detection, repiping, 24/7 emergency calls. Licensed and insured. "
            "Upfront flat-rate pricing — no hourly surprises. Same-day service for most jobs. "
            "Family-run, dispatched from SE Portland, serving the metro and inner suburbs. "
            "Do not state years in business, job counts, or numeric track-record claims unless I provided the number here. "
            "Tone: confident, plain-spoken, neighborly."
        ),
    },
    {
        "business_name": "Brightwire Electric",
        "industry": "electrician",
        "vibe": "trade-pro",
        "extra_context": (
            "Austin, TX. Services: electrical panel upgrades, EV charger installation, "
            "indoor and outdoor lighting design, circuit troubleshooting, whole-home generators. "
            "Licensed master electrician, fully insured, permit-ready for all jurisdictions in Travis County. "
            "Same-day diagnostic visits available. Upfront written estimates before any work begins. "
            "Do not state years in business, job counts, or numeric track-record claims unless I provided the number here. "
            "Tone: technical but approachable, safety-first."
        ),
    },
    {
        "business_name": "Northpeak Heating & Air",
        "industry": "hvac",
        "vibe": "trade-pro",
        "extra_context": (
            "Denver, CO. Services: AC installation and repair, furnace replacement and tune-ups, "
            "heat pumps, indoor air quality testing and filtration, 24/7 emergency HVAC service. "
            "Licensed and insured, NATE-certified technicians. Flat-rate pricing on all service calls. "
            "Maintenance plans available for year-round comfort in Colorado's extreme climate. "
            "Do not state years in business, job counts, or numeric track-record claims unless I provided the number here. "
            "Tone: straightforward, reliable, built-for-altitude rugged."
        ),
    },
    {
        "business_name": "Cedar & Stone Landscapes",
        "industry": "landscaper",
        "vibe": "showcase",
        "extra_context": (
            "Raleigh, NC. Services: landscape design and installation, weekly lawn care, "
            "hardscape construction including patios and retaining walls, irrigation system install and repair, "
            "seasonal cleanups and mulching. Licensed and insured, serving the Triangle area. "
            "Free design consultations. All projects backed by a workmanship warranty. "
            "Do not state years in business, job counts, or numeric track-record claims unless I provided the number here. "
            "Tone: creative, detail-oriented, locally rooted."
        ),
    },
    {
        "business_name": "Sparrow Home Cleaning",
        "industry": "cleaning service",
        "vibe": "trade-pro",
        "extra_context": (
            "Minneapolis, MN. Services: recurring weekly and biweekly home cleaning, "
            "deep cleans, move-in and move-out cleans, small office cleaning. "
            "Fully insured and bonded, background-checked staff. Eco-friendly products available on request. "
            "Online booking in under two minutes, consistent assigned teams, satisfaction guarantee on every visit. "
            "Do not state years in business, job counts, or numeric track-record claims unless I provided the number here. "
            "Tone: warm, trustworthy, detail-obsessed."
        ),
    },
    {
        "business_name": "Ridgeline Builders",
        "industry": "general contractor",
        "vibe": "showcase",
        "extra_context": (
            "Boise, ID. Services: whole-home remodels, room additions, kitchen renovations, "
            "bathroom upgrades, custom decks and outdoor living spaces. "
            "Licensed general contractor, fully insured, all trades in-house or vetted subcontractors. "
            "Fixed-price contracts with no hidden change orders. Free in-home estimates. "
            "Do not state years in business, job counts, or numeric track-record claims unless I provided the number here. "
            "Tone: dependable, craftsman-proud, straightforward."
        ),
    },
    {
        "business_name": "Summit Ridge Roofing",
        "industry": "roofer",
        "vibe": "showcase",
        "extra_context": (
            "Kansas City, MO. Services: full roof replacement, storm damage repair, "
            "insurance claim assistance, residential inspections, gutter installation and cleaning. "
            "Licensed and insured, certified by major shingle manufacturers for warranty eligibility. "
            "Free storm inspections and written estimates. Works directly with insurance adjusters. "
            "Do not state years in business, job counts, or numeric track-record claims unless I provided the number here. "
            "Tone: direct, dependable, storm-ready."
        ),
    },
    {
        "business_name": "Gearworks Auto Service",
        "industry": "auto repair",
        "vibe": "showcase",
        "extra_context": (
            "Columbus, OH. Services: computerized diagnostics, brake service, oil and filter changes, "
            "AC recharge and repair, tire sales and alignment, fleet maintenance contracts. "
            "ASE-certified technicians, fully insured shop. Transparent digital inspection reports "
            "with photos sent to your phone before approval. Loaner cars available. "
            "Do not state years in business, job counts, or numeric track-record claims unless I provided the number here. "
            "Tone: no-nonsense, knowledgeable, customer-first."
        ),
    },
]
