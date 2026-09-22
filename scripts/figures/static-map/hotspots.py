"""Where each of the 48 nodes sits on the reproduced flowchart image.

The article reproduces the chart itself, credited to its source, at
``docs/assets/images/static-flowchart/flowchart.webp`` (1284x2137). The page needs to know which
part of that picture belongs to which node so hovering a node can raise this site's own figure for
it.

The boxes were not typed by hand. Each of the chart's five node colours was segmented out of the
image, the connected regions of each colour were taken as that kind's nodes, and their bounding
boxes were written to ``hotspots_raw.json`` grouped by kind and sorted top to bottom. The counts
came out exactly as the chart has them: 4 techniques, 14 issues, 8 symptoms, 11 results and
11 scenarios. Segmentation finds boxes, not meaning, so each box was then read off the image and
matched to the node whose words sit there. That reading is what this file records.

Values are ``(left, top, width, height)`` as percentages of the image, not pixels, because the
article renders the chart responsively: a percentage box stays over its node at every width, and
survives the image being re-encoded at a different size.

The keys are the ones in ``nodes.py``. Every key appears exactly once and every segmented box is
used exactly once; ``build.py`` and the page both rely on that.
"""

HOTSPOTS: dict[str, tuple[float, float, float, float]] = {
    # ---- Techniques, the four green nodes -------------------------------------------------
    "sc-flick": (23.05, 3.56, 14.33, 3.93),
    "sc-fluid-transition": (60.75, 46.79, 10.28, 3.18),
    "sc-continuous-flicking": (59.19, 63.27, 13.40, 3.37),
    "sc-controlled-bursts": (25.86, 77.49, 13.71, 4.68),

    # ---- Issues, the red diamonds and rounded boxes ----------------------------------------
    "sc-overflick": (39.56, 9.17, 14.33, 4.87),
    "sc-arm-too-relaxed": (16.51, 10.86, 20.25, 4.68),
    "sc-arm-too-tense": (57.01, 11.61, 15.26, 4.68),
    "sc-too-little-control": (47.66, 16.10, 17.45, 5.43),
    "sc-too-much-force": (29.28, 16.66, 17.45, 4.87),
    "sc-too-smooth": (4.67, 26.77, 14.33, 4.49),
    "sc-dragging-initial-flick": (25.55, 30.88, 14.02, 5.24),
    "sc-decelerating-too-early": (52.34, 31.07, 14.33, 5.05),
    "sc-inconsistent-confirmation": (12.46, 50.35, 15.58, 4.68),
    "sc-mind-too-little-tension": (77.26, 52.60, 19.00, 4.87),
    "sc-no-micro-adjustments": (3.43, 53.16, 14.64, 4.68),
    "sc-pacing-keeps-dropping": (40.19, 68.51, 15.26, 3.56),
    "sc-missing-wider-flicks": (41.74, 73.00, 12.15, 3.18),
    "sc-disrupted-pacing": (4.67, 77.68, 12.46, 4.49),

    # ---- Visible symptoms, the purple clouds -----------------------------------------------
    "sc-push-flick-speed": (68.54, 17.22, 20.87, 5.43),
    "sc-smooth-means-pacing": (40.50, 27.52, 12.46, 4.68),
    "sc-clicking-too-fast": (2.49, 36.87, 16.20, 4.68),
    "sc-crosshair-lingers": (25.23, 46.79, 23.36, 5.05),
    "sc-wider-flicks-ruin-pacing": (27.10, 65.51, 15.58, 3.74),
    "sc-cluster-approach": (18.38, 69.82, 13.40, 3.37),
    "sc-target-priorities": (75.39, 77.30, 19.31, 5.43),
    "sc-create-clusters": (63.86, 91.53, 23.05, 5.43),

    # ---- Practice results, the blue boxes --------------------------------------------------
    "sc-cleaner-landings": (15.26, 23.40, 9.97, 2.81),
    "sc-shortens-deceleration": (68.54, 32.01, 13.71, 3.56),
    "sc-faster-starts": (36.76, 43.05, 9.97, 2.81),
    "sc-better-tension-control": (54.52, 43.05, 9.97, 2.81),
    "sc-faster-transitions": (60.75, 59.52, 10.28, 2.62),
    "sc-improved-overall-pacing": (27.10, 61.21, 10.59, 2.99),
    "sc-preemptive-confirmation": (44.86, 63.45, 10.90, 2.62),
    "sc-proper-flicking-motion": (5.61, 68.51, 10.59, 2.81),
    "sc-improved-fluidity": (60.75, 78.43, 10.28, 2.99),
    "sc-improved-pacing-control": (45.79, 85.17, 10.28, 2.62),
    "sc-active-cluster-farming": (27.41, 92.84, 10.90, 2.62),

    # ---- Practice scenarios, the orange boxes ----------------------------------------------
    "sc-scen-wide-small": (48.60, 21.90, 15.26, 4.87),
    "sc-scen-multi-target": (28.04, 22.46, 17.76, 4.31),
    "sc-scen-pressure-flick": (23.68, 36.69, 17.76, 5.05),
    "sc-scen-wide-varying": (49.53, 36.69, 20.25, 5.05),
    "sc-scen-stabilise-landing": (56.39, 51.47, 18.69, 7.11),
    "sc-scen-long-large": (24.30, 54.66, 16.20, 5.80),
    "sc-scen-long-small": (3.12, 59.15, 15.26, 7.11),
    "sc-scen-cluster-many": (64.80, 70.00, 17.76, 5.24),
    "sc-scen-hard-pressure": (1.87, 84.04, 18.38, 4.68),
    "sc-scen-mid-cluster": (23.99, 83.48, 17.45, 5.99),
    "sc-scen-varying-sizes": (60.12, 83.86, 19.63, 5.24),
}


# The box a reader actually points at.
#
# HOTSPOTS above bounds the whole node, which is wrong for the shapes that are not rectangles. A
# diamond fills half of its own bounding box, so its corners are empty chart, and pointing at one
# would open a node the reader can see they are not over. A cloud is worse.
#
# The text inside a node is rectangular, and it is what a reader aims at. These boxes are the
# bright pixels inside each shape, padded slightly, and then grown from their own centre to a
# floor of 6.0 by 2.4 percent so a one-word node stays big enough to tap once the image has scaled
# to a phone. Growth is clamped to the shape, so a box can never escape the node it belongs to.
TEXT_BOXES: dict[str, tuple[float, float, float, float]] = {
    "sc-flick": (25.62, 4.37, 8.96, 2.4),
    "sc-fluid-transition": (61.92, 47.4, 7.87, 2.4),
    "sc-continuous-flicking": (61.21, 63.73, 9.89, 2.71),
    "sc-controlled-bursts": (28.35, 78.57, 8.88, 2.71),
    "sc-overflick": (43.73, 10.36, 6.0, 2.4),
    "sc-arm-too-relaxed": (19.16, 11.7, 13.55, 2.85),
    "sc-arm-too-tense": (59.35, 12.4, 9.97, 2.81),
    "sc-too-much-force": (33.64, 18.01, 9.42, 2.4),
    "sc-too-little-control": (52.34, 17.82, 8.33, 2.4),
    "sc-too-smooth": (8.1, 27.65, 8.57, 2.4),
    "sc-dragging-initial-flick": (30.06, 32.54, 6.0, 2.4),
    "sc-decelerating-too-early": (56.23, 32.34, 7.71, 2.71),
    "sc-mind-too-little-tension": (78.04, 53.21, 16.9, 3.42),
    "sc-inconsistent-confirmation": (16.28, 51.47, 8.1, 2.71),
    "sc-no-micro-adjustments": (6.7, 53.3, 9.58, 3.28),
    "sc-pacing-keeps-dropping": (44.78, 69.04, 6.78, 2.4),
    "sc-missing-wider-flicks": (45.09, 73.48, 6.07, 2.4),
    "sc-disrupted-pacing": (8.29, 78.68, 6.0, 2.4),
    "sc-push-flick-speed": (72.74, 18.69, 12.85, 2.4),
    "sc-smooth-means-pacing": (42.37, 28.26, 8.88, 3.51),
    "sc-clicking-too-fast": (6.39, 38.0, 9.58, 2.57),
    "sc-crosshair-lingers": (29.28, 47.96, 13.47, 2.71),
    "sc-wider-flicks-ruin-pacing": (30.69, 66.23, 8.49, 2.4),
    "sc-cluster-approach": (21.81, 70.19, 6.85, 2.57),
    "sc-target-priorities": (81.07, 78.71, 9.66, 2.67),
    "sc-create-clusters": (68.77, 92.89, 13.01, 2.71),
    "sc-cleaner-landings": (16.43, 23.51, 7.87, 2.4),
    "sc-shortens-deceleration": (69.63, 32.05, 12.31, 3.51),
    "sc-faster-starts": (38.47, 43.25, 6.46, 2.4),
    "sc-better-tension-control": (56.15, 43.21, 7.48, 2.4),
    "sc-improved-overall-pacing": (27.96, 61.5, 8.8, 2.4),
    "sc-preemptive-confirmation": (46.5, 63.45, 8.26, 2.4),
    "sc-faster-transitions": (61.45, 59.74, 8.96, 2.4),
    "sc-proper-flicking-motion": (7.01, 68.69, 7.63, 2.4),
    "sc-improved-fluidity": (61.53, 78.77, 9.03, 2.4),
    "sc-improved-pacing-control": (46.73, 85.3, 8.64, 2.4),
    "sc-active-cluster-farming": (29.44, 93.06, 7.24, 2.4),
    "sc-scen-multi-target": (28.74, 23.21, 16.74, 2.85),
    "sc-scen-wide-small": (49.38, 22.18, 14.17, 3.65),
    "sc-scen-pressure-flick": (23.99, 37.34, 17.21, 3.74),
    "sc-scen-wide-varying": (49.53, 36.92, 19.78, 4.63),
    "sc-scen-long-large": (25.0, 55.4, 14.64, 4.4),
    "sc-scen-long-small": (3.27, 60.13, 15.03, 5.24),
    "sc-scen-stabilise-landing": (57.17, 52.04, 17.13, 6.08),
    "sc-scen-cluster-many": (64.95, 70.38, 17.29, 4.4),
    "sc-scen-hard-pressure": (2.73, 84.28, 16.9, 4.26),
    "sc-scen-mid-cluster": (26.09, 84.23, 13.63, 4.4),
    "sc-scen-varying-sizes": (60.51, 84.32, 18.54, 4.4),
}
