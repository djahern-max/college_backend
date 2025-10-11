# scripts/scholarship_image_mappings.py
"""
Complete mapping of image filenames to scholarship titles
"""

# BATCH 9 - LEADERSHIP (the 9 you have images for)
BATCH_9_MAPPINGS = {
    "lowes-scholarship.jpg": "Lowe's Educational Scholarship",
    "target-community.jpg": "Target Community Scholarship",
    "bonner-scholars.jpg": "Bonner Scholars Program",
    "violet-richardson.jpg": "Violet Richardson Award",
    "gloria-barron-prize.jpg": "Gloria Barron Prize for Young Heroes",
    "samuel-huntington.jpg": "Samuel Huntington Public Service Award",
    "newman-civic-fellowship.jpg": "Newman Civic Fellowship",
    "do-something-awards.jpg": "Do Something Awards",
    "horatio-alger-state.jpg": "Horatio Alger State Scholarship",
}

# For now, only process the 9 we have
ALL_MAPPINGS = BATCH_9_MAPPINGS

PRIORITY_SCHOLARSHIPS = [
    "Bonner Scholars Program",
    "Gloria Barron Prize for Young Heroes",
    "Samuel Huntington Public Service Award",
]

def get_priority_mappings():
    return {k: v for k, v in ALL_MAPPINGS.items() if v in PRIORITY_SCHOLARSHIPS}
