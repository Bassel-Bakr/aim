"""Every node of the static clicking chart, as data.

The chart has 48 nodes and each one gets its own animated figure. Writing 48 generators by hand
would be 6000 lines nobody could keep true, so the drawing lives in five renderers, one per node
type, and the difference between nodes lives here.

That split is not only about size. Eleven of these nodes are practice scenarios, and what actually
separates them is target count, spread and size. A table says that in one line each. Eleven
hand-drawn lanes would say it eleven times and drift apart the first time one was edited.

The figures are this site's own drawings of the same mechanics. They do not trace the chart's
layout, which is someone else's work and carries no licence. See the Third-party assets section of
AGENTS.md, and the article, which reproduces the chart itself with its source credited.

Fields
------
key     the published figure name, also the page's marker. Prefixed sc- so 48 names cannot collide
        with the 109 already in docs/figures.
kind    which renderer draws it: issue, symptom, technique, scenario or result.
label   the node's words, shortened to what fits a figure.
params  what that renderer needs. Each kind reads its own keys and ignores the rest.

params by kind
--------------
issue, symptom
    peak    how far the crosshair travels, 1.0 being the target. Over 1 overshoots, under 1 falls
            short and never arrives.
    brake   when deceleration starts: "late", "early", "none".
    jitter  0 to 1, how much the crosshair shakes once it is near.
    shot    fraction of the travel at which the trigger goes. 1.0 is a settled shot.
technique
    peak    as above, near 1.0 for a motion that lands.
    phases  how many sub-motions the drawing separates: a flick, a transition, a settle.
    hold    how long the crosshair rests before the next motion, 0 to 1.
scenario
    targets how many targets on the wall.
    spread  "narrow", "mid" or "wide", how far apart they sit.
    size    "small", "mid" or "large".
    cluster whether the targets group, which changes pathing rather than flicking.
result
    before  the metric before practice, 0 to 1, where lower is better.
    after   the metric after.
    metric  what is being measured, for the label.
"""
from typing import Any, NamedTuple


class Node(NamedTuple):
    key: str
    kind: str
    label: str
    params: dict[str, Any]


# The chart's own branches, kept so the page can group by them rather than by node type. A reader
# arrives with a symptom, not with a taxonomy.
BRANCHES = {
    "root": "Where it starts",
    "overflick": "Overflicking",
    "smooth": "Flicks that will not commit",
    "pacing": "Pacing that falls apart",
    "cluster": "Clusters and pathing",
}

NODES: list[Node] = [
    # ---- Techniques, the four green nodes -------------------------------------------------
    Node("sc-flick", "technique", "Flick, move the crosshair",
         {"peak": 1.0, "phases": 2, "hold": 0.2, "branch": "root"}),
    Node("sc-fluid-transition", "technique", "Fluid transition",
         {"peak": 1.0, "phases": 3, "hold": 0.1, "branch": "smooth"}),
    Node("sc-continuous-flicking", "technique", "Continuous flicking",
         {"peak": 1.0, "phases": 4, "hold": 0.05, "branch": "pacing"}),
    Node("sc-controlled-bursts", "technique", "Controlled bursts",
         {"peak": 1.0, "phases": 4, "hold": 0.3, "branch": "cluster"}),

    # ---- Issues, the red diamonds and rounded boxes ----------------------------------------
    Node("sc-overflick", "issue", "Overflick",
         {"peak": 1.22, "brake": "late", "jitter": 0.0, "shot": 1.0, "branch": "overflick"}),
    Node("sc-arm-too-relaxed", "issue", "Arm too relaxed, loose micros",
         {"peak": 0.88, "brake": "early", "jitter": 0.1, "shot": 1.0, "branch": "overflick"}),
    Node("sc-arm-too-tense", "issue", "Arm too tense, bad micros",
         {"peak": 1.18, "brake": "late", "jitter": 0.55, "shot": 1.0, "branch": "overflick"}),
    Node("sc-too-much-force", "issue", "Too much force, brakes late",
         {"peak": 1.30, "brake": "late", "jitter": 0.15, "shot": 1.0, "branch": "overflick"}),
    Node("sc-too-little-control", "issue", "Too little control",
         {"peak": 1.15, "brake": "none", "jitter": 0.45, "shot": 1.0, "branch": "overflick"}),
    Node("sc-too-smooth", "issue", "Too smooth, two possibilities",
         {"peak": 0.94, "brake": "early", "jitter": 0.0, "shot": 1.0, "branch": "smooth"}),
    Node("sc-dragging-initial-flick", "issue", "Dragging the initial flick",
         {"peak": 0.90, "brake": "early", "jitter": 0.0, "shot": 1.0, "branch": "smooth"}),
    Node("sc-decelerating-too-early", "issue", "Decelerating too early",
         {"peak": 0.92, "brake": "early", "jitter": 0.05, "shot": 1.0, "branch": "smooth"}),
    Node("sc-mind-too-little-tension", "issue", "Too little arm tension",
         {"peak": 0.86, "brake": "early", "jitter": 0.2, "shot": 1.0, "branch": "smooth"}),
    Node("sc-inconsistent-confirmation", "issue", "Inconsistent confirmation",
         {"peak": 1.0, "brake": "late", "jitter": 0.3, "shot": 0.82, "branch": "pacing"}),
    Node("sc-no-micro-adjustments", "issue", "Not doing micro adjustments",
         {"peak": 0.93, "brake": "none", "jitter": 0.0, "shot": 0.93, "branch": "pacing"}),
    Node("sc-pacing-keeps-dropping", "issue", "Pacing keeps dropping",
         {"peak": 1.0, "brake": "late", "jitter": 0.2, "shot": 0.9, "branch": "pacing"}),
    Node("sc-missing-wider-flicks", "issue", "Missing wider flicks",
         {"peak": 1.24, "brake": "none", "jitter": 0.35, "shot": 1.0, "branch": "cluster"}),
    Node("sc-disrupted-pacing", "issue", "Disrupted pacing",
         {"peak": 1.0, "brake": "late", "jitter": 0.5, "shot": 0.7, "branch": "cluster"}),

    # ---- Visible symptoms, the purple clouds -----------------------------------------------
    Node("sc-push-flick-speed", "symptom", "Push the initial flick speed",
         {"peak": 1.0, "brake": "late", "jitter": 0.0, "shot": 1.0, "branch": "overflick"}),
    Node("sc-smooth-means-pacing", "symptom", "Smooth means steady pacing",
         {"peak": 1.0, "brake": "early", "jitter": 0.0, "shot": 1.0, "branch": "smooth"}),
    Node("sc-clicking-too-fast", "symptom", "Clicking before confirming",
         {"peak": 1.0, "brake": "none", "jitter": 0.1, "shot": 0.78, "branch": "pacing"}),
    Node("sc-crosshair-lingers", "symptom", "Crosshair lingers, no micros",
         {"peak": 0.97, "brake": "early", "jitter": 0.05, "shot": 1.0, "branch": "pacing"}),
    Node("sc-wider-flicks-ruin-pacing", "symptom", "Wider flicks ruin pacing",
         {"peak": 1.2, "brake": "late", "jitter": 0.25, "shot": 1.0, "branch": "cluster"}),
    Node("sc-cluster-approach", "symptom", "Cluster approach, wide flicks",
         {"peak": 1.0, "brake": "late", "jitter": 0.1, "shot": 1.0, "branch": "cluster"}),
    Node("sc-target-priorities", "symptom", "Better target order",
         {"peak": 1.0, "brake": "late", "jitter": 0.0, "shot": 1.0, "branch": "cluster"}),
    Node("sc-create-clusters", "symptom", "Create cluster chances",
         {"peak": 1.0, "brake": "late", "jitter": 0.0, "shot": 1.0, "branch": "cluster"}),

    # ---- Practice results, the blue boxes --------------------------------------------------
    Node("sc-cleaner-landings", "result", "Cleaner landings",
         {"before": 0.62, "after": 0.12, "metric": "overshoot", "branch": "overflick"}),
    Node("sc-shortens-deceleration", "result", "Shortens the deceleration phase",
         {"before": 0.70, "after": 0.24, "metric": "braking distance", "branch": "smooth"}),
    Node("sc-faster-starts", "result", "Faster starts",
         {"before": 0.66, "after": 0.22, "metric": "initial flick speed", "branch": "smooth"}),
    Node("sc-better-tension-control", "result", "Better tension control",
         {"before": 0.58, "after": 0.18, "metric": "shake near the target", "branch": "smooth"}),
    Node("sc-improved-overall-pacing", "result", "Improved overall pacing",
         {"before": 0.64, "after": 0.20, "metric": "gap between shots", "branch": "pacing"}),
    Node("sc-preemptive-confirmation", "result", "Pre-emptive hit confirmation",
         {"before": 0.60, "after": 0.16, "metric": "confirm lag", "branch": "pacing"}),
    Node("sc-faster-transitions", "result", "Faster transitions",
         {"before": 0.68, "after": 0.22, "metric": "dead time between targets", "branch": "pacing"}),
    Node("sc-proper-flicking-motion", "result", "Proper flicking motion",
         {"before": 0.55, "after": 0.14, "metric": "wasted movement", "branch": "pacing"}),
    Node("sc-improved-fluidity", "result", "Improved fluidity",
         {"before": 0.61, "after": 0.17, "metric": "stalls per run", "branch": "cluster"}),
    Node("sc-improved-pacing-control", "result", "Improved pacing control",
         {"before": 0.57, "after": 0.19, "metric": "pace drift", "branch": "cluster"}),
    Node("sc-active-cluster-farming", "result", "Active cluster farming",
         {"before": 0.72, "after": 0.26, "metric": "path length", "branch": "cluster"}),

    # ---- Practice scenarios, the orange boxes ----------------------------------------------
    # Scenario names are deliberately absent from the drawings. The article argues they rot, and a
    # generated figure is the worst place to bury one. The shape is what survives.
    Node("sc-scen-multi-target", "scenario", "Many large targets",
         {"targets": 6, "spread": "mid", "size": "large", "cluster": False, "branch": "overflick"}),
    Node("sc-scen-wide-small", "scenario", "Wide wall, few small targets",
         {"targets": 4, "spread": "wide", "size": "small", "cluster": False,
          "branch": "overflick"}),
    Node("sc-scen-pressure-flick", "scenario", "Pressure flicking, one target",
         {"targets": 1, "spread": "narrow", "size": "mid", "cluster": False, "branch": "smooth"}),
    Node("sc-scen-wide-varying", "scenario", "Wide flicks of varying distance",
         {"targets": 3, "spread": "wide", "size": "mid", "cluster": False, "branch": "smooth"}),
    Node("sc-scen-long-large", "scenario", "Long distance, large targets",
         {"targets": 3, "spread": "wide", "size": "large", "cluster": False, "branch": "pacing"}),
    Node("sc-scen-long-small", "scenario", "Long distance, small targets",
         {"targets": 2, "spread": "wide", "size": "small", "cluster": False, "branch": "pacing"}),
    Node("sc-scen-stabilise-landing", "scenario", "Stabilise flick and landing",
         {"targets": 2, "spread": "mid", "size": "mid", "cluster": False, "branch": "smooth"}),
    Node("sc-scen-cluster-many", "scenario", "Many clustered targets, pathing",
         {"targets": 9, "spread": "narrow", "size": "small", "cluster": True, "branch": "cluster"}),
    Node("sc-scen-hard-pressure", "scenario", "Recover after a miss",
         {"targets": 1, "spread": "narrow", "size": "small", "cluster": False, "branch": "cluster"}),
    Node("sc-scen-mid-cluster", "scenario", "Mid-range cluster, build speed",
         {"targets": 6, "spread": "mid", "size": "mid", "cluster": True, "branch": "cluster"}),
    Node("sc-scen-varying-sizes", "scenario", "Varying distance and size",
         {"targets": 5, "spread": "wide", "size": "mid", "cluster": False, "branch": "cluster"}),
]


def by_kind(kind: str) -> list[Node]:
    """Every node one renderer is responsible for."""
    return [n for n in NODES if n.kind == kind]


def by_branch(branch: str) -> list[Node]:
    """Every node under one of the chart's branches, in table order."""
    return [n for n in NODES if n.params.get("branch") == branch]
