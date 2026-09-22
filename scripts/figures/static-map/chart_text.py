"""What each of the 48 nodes says on the chart itself, transcribed word for word.

These are the chart's words, not this site's. The article reproduces the chart at
``docs/assets/images/static-flowchart/flowchart.webp`` with its source credited, and every string
below was read off that image and copied exactly: its spelling, its capitalisation and its
abbreviations, including "scens", "cA", "AVOID" and "NOT". Nothing was corrected or tidied. Where a
node wraps over several lines, the line breaks are single spaces here; the wording is untouched.

``nodes.py`` holds a shortened paraphrase in its ``label`` field, which is what the figures are
drawn to fit. This file is what the page leads with, so a reader sees the chart's own description
of a node first and this site's material second.

Labels that sit on the arrows between nodes ("Leads back to", "Possible issues", "Chokes",
"AVOID", "Otherwise" and the rest) are edge text, not node text, and are deliberately absent.

The keys are the ones in ``nodes.py``. Every key appears exactly once.
"""

CHART_TEXT: dict[str, str] = {
    # ---- Techniques, the four green nodes -------------------------------------------------
    "sc-flick": "Flick (move crosshair)",
    "sc-fluid-transition": "Fluid transition",
    "sc-continuous-flicking": "Continuous flicking (dynamic click pacing)",
    "sc-controlled-bursts": "Controlled bursts with consistent pacing",

    # ---- Issues, the red diamonds and rounded boxes ----------------------------------------
    "sc-overflick": "Overflick",
    "sc-arm-too-relaxed": "Arm is too relaxed, with a lot of room for micro adjustments",
    "sc-arm-too-tense": "Arm is too tense, very inaccurate micro adjustments",
    "sc-too-little-control": "Too little control (common in wider flicks)",
    "sc-too-much-force": "Using too much force (decelerating too late)",
    "sc-too-smooth": "Too smooth (Two possibilities)",
    "sc-dragging-initial-flick": "Dragging initial flick",
    "sc-decelerating-too-early": "Decelerating too early (long deceleration)",
    "sc-inconsistent-confirmation": "Inconsistent hit confirmation speed",
    "sc-mind-too-little-tension": (
        "Be mindful not to apply too little arm tension. Try to actively maintain control for "
        "fast flicks and short decelerations"
    ),
    "sc-no-micro-adjustments": "Not doing micro adjustments",
    "sc-pacing-keeps-dropping": "Pacing keeps dropping",
    "sc-missing-wider-flicks": "Missing wider flicks",
    "sc-disrupted-pacing": "Disrupted pacing",

    # ---- Visible symptoms, the purple clouds -----------------------------------------------
    "sc-push-flick-speed": "To push initial flick speed (increase explosiveness)",
    "sc-smooth-means-pacing": (
        "Remember: smooth flicks and landings mean consistent pacing, NOT slow aiming"
    ),
    "sc-clicking-too-fast": "Clicking too fast without proper hit confirmation",
    "sc-crosshair-lingers": (
        "Crosshair lingers around target for too long without making micro adjustments"
    ),
    "sc-wider-flicks-ruin-pacing": "Wider flicks ruin pacing",
    "sc-cluster-approach": "Using cluster approach for wider flicks",
    "sc-target-priorities": "Improving target selection priorities during pathing",
    "sc-create-clusters": (
        "Actively go after or create cluster opportunities in order to speed up faster"
    ),

    # ---- Practice results, the blue boxes --------------------------------------------------
    "sc-cleaner-landings": "Cleaner landings",
    "sc-shortens-deceleration": (
        "Shortens deceleration phase (The transition between initial flick and deceleration)"
    ),
    "sc-faster-starts": "Faster starts",
    "sc-better-tension-control": "Better tension control",
    "sc-faster-transitions": "Faster transitions",
    "sc-improved-overall-pacing": "Improved overall pacing",
    "sc-preemptive-confirmation": "Pre-emptive hit confirmation",
    "sc-proper-flicking-motion": "Proper flicking motion",
    "sc-improved-fluidity": "Improved fluidity",
    "sc-improved-pacing-control": "Improved pacing control",
    "sc-active-cluster-farming": "Active cluster farming",

    # ---- Practice scenarios, the orange boxes ----------------------------------------------
    "sc-scen-wide-small": (
        "Practice wider, smaller target scens such as 1w1ts, 1w4ts and cA 4ts horizontal to "
        "strengthen micro adjustments and hit confirmation"
    ),
    "sc-scen-multi-target": (
        "Practice multi-target scens such as 6ts hipfire and pokeball type scens. AVOID "
        "overflicking"
    ),
    "sc-scen-pressure-flick": (
        "Practice pressure flicking scens like fuglaapressure and cA 7ts pressure. Strengthens "
        "initial flick speed and relieves tension"
    ),
    "sc-scen-wide-varying": (
        "Practice scens with wide flicks of varying distances like ww3ts, ww2ts, cA x-axis, "
        "y-axis, 2ts. Focus on maintaining arm tension control when doing wide flicks"
    ),
    "sc-scen-stabilise-landing": (
        "Practice pokeball scenarios to stabilize flicking and landing motions, focus on faster "
        "flicks and shorter decelerations. Learn to transition smoothly between each flick and "
        "subsequent micro adjustment"
    ),
    "sc-scen-long-large": (
        "Practice long distance large target scens such as cA 3ts precise and cA 4ts horizontal. "
        "Maintain consistent landing and hit confirmation speed."
    ),
    "sc-scen-long-small": (
        "Practice long distance, small target scens like cA 1ts ruohong and cA 4ts horizontal. "
        "Maintain proper flicking technique with a specific focus on micro adjustments"
    ),
    "sc-scen-cluster-many": (
        "Practice multi target cluster scens such as 1wall9000targets and cA 900targets. Focus "
        "on cluster pacing and consistency, as well as cluster pathing"
    ),
    "sc-scen-hard-pressure": (
        "Practice fuglaapressure related or any hard pressure scens. Focus on regaining your "
        "pacing after a miss instead of completely eliminating mistakes"
    ),
    "sc-scen-mid-cluster": (
        "Practice mid-range cluster scens like sixshot. Focus on slowly building speed for "
        "repetitive flicking motions upon each successful flick"
    ),
    "sc-scen-varying-sizes": (
        "Practice scenarios with targets of varying distances and sizes like voxTS static. Make "
        "sure to actively practice dynamic pacing to maintain consistency"
    ),
}
