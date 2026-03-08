"""
Seed hyperlocal disease and best practices data for demo
"""

import sys
sys.path.append('../src/hyperlocal')

from disease_tracker import hyperlocal_tracker
import random

print("🌾 Seeding Hyperlocal Disease & Best Practices Data...")
print("=" * 60)

# Sample villages and districts
villages = [
    ("Nandani", "Sangli"),
    ("Walwa", "Sangli"),
    ("Miraj", "Sangli"),
    ("Tasgaon", "Sangli"),
    ("Shirala", "Sangli"),
    ("Vita", "Sangli"),
    ("Khanapur", "Sangli"),
    ("Atpadi", "Sangli"),
]

# Common diseases by crop
diseases_by_crop = {
    "rice": [
        ("Blast Disease", "Brown spots on leaves, wilting", "high"),
        ("Bacterial Leaf Blight", "Yellow to white lesions", "medium"),
        ("Sheath Blight", "Oval lesions on leaf sheaths", "medium"),
    ],
    "wheat": [
        ("Rust Disease", "Orange-red pustules on leaves", "high"),
        ("Powdery Mildew", "White powdery coating", "medium"),
        ("Leaf Blight", "Brown spots spreading rapidly", "high"),
    ],
    "sugarcane": [
        ("Red Rot", "Reddish discoloration of stalks", "high"),
        ("Smut Disease", "Black whip-like growth", "medium"),
        ("Wilt Disease", "Yellowing and drying of leaves", "high"),
    ],
    "cotton": [
        ("Bollworm Infestation", "Holes in bolls, larvae visible", "high"),
        ("Leaf Curl Virus", "Upward curling of leaves", "medium"),
        ("Root Rot", "Wilting, yellowing, root decay", "high"),
    ],
    "tomato": [
        ("Late Blight", "Dark spots on leaves and fruits", "high"),
        ("Leaf Curl", "Curling and yellowing of leaves", "medium"),
        ("Bacterial Wilt", "Sudden wilting of plants", "high"),
    ],
}

# Successful treatments
treatments = {
    "Blast Disease": [
        ("Tricyclazole fungicide spray", 9, 800, 14, "Spray every 7 days, 2-3 applications"),
        ("Carbendazim + Mancozeb", 8, 600, 10, "Mix both and spray in evening"),
    ],
    "Red Rot": [
        ("Remove infected stalks immediately", 8, 0, 7, "Burn infected material, don't compost"),
        ("Copper oxychloride spray", 7, 500, 14, "Preventive spray before monsoon"),
    ],
    "Wilt Disease": [
        ("Drip irrigation with reduced water", 8, 200, 14, "Avoid waterlogging, improves drainage"),
        ("Trichoderma soil treatment", 9, 400, 21, "Apply 5kg/acre mixed with compost"),
        ("Remove and burn infected plants", 7, 0, 3, "Prevent spread to healthy plants"),
    ],
    "Bollworm Infestation": [
        ("Neem oil spray (organic)", 8, 300, 10, "Spray early morning, repeat weekly"),
        ("Bt cotton variety", 9, 0, 0, "Use resistant variety next season"),
        ("Pheromone traps", 7, 400, 21, "Place 10 traps per acre"),
    ],
    "Late Blight": [
        ("Mancozeb spray", 9, 400, 7, "Start at first sign, spray every 5 days"),
        ("Remove infected plants", 7, 0, 3, "Isolate and destroy affected plants"),
    ],
    "Rust Disease": [
        ("Propiconazole spray", 9, 700, 14, "Two sprays at 10-day interval"),
        ("Sulfur dusting", 7, 300, 7, "Dust in early morning"),
    ],
}

# Best practices by crop
best_practices = {
    "rice": [
        ("pest_control", "Neem Cake Application", "Mix 250kg neem cake per acre in soil before planting. Reduces pest attacks by 60%.", "kharif"),
        ("irrigation", "Alternate Wetting and Drying", "Don't keep field flooded continuously. Dry for 2-3 days, then flood again. Saves 30% water.", "all"),
        ("fertilizer", "Green Manure Before Rice", "Grow dhaincha for 45 days, then plow into soil. Reduces fertilizer need by 25%.", "kharif"),
    ],
    "wheat": [
        ("irrigation", "Critical Stage Watering", "Must irrigate at crown root, tillering, flowering, and grain filling stages. Don't miss these!", "rabi"),
        ("pest_control", "Trap Crops for Aphids", "Plant mustard on borders. Aphids attack mustard first, saving wheat.", "rabi"),
    ],
    "sugarcane": [
        ("planting", "Trench Planting Method", "Plant in 30cm deep trenches instead of flat. Increases yield by 20% and saves water.", "all"),
        ("pest_control", "Trash Mulching", "Keep dried leaves as mulch. Reduces weeds and keeps soil moist.", "all"),
    ],
    "cotton": [
        ("pest_control", "Intercropping with Marigold", "Plant marigold every 10 rows. Attracts beneficial insects that eat pests.", "kharif"),
        ("irrigation", "Drip Irrigation for Cotton", "Drip saves 50% water and increases yield. Initial cost high but pays back in 2 years.", "kharif"),
    ],
    "tomato": [
        ("pest_control", "Garlic-Chili Spray", "Blend 100g garlic + 100g chili + 1L water. Spray weekly. Organic pest control.", "all"),
        ("planting", "Staking and Pruning", "Stake plants and remove side shoots. Increases fruit size and reduces disease.", "all"),
    ],
}

print("\n📊 Creating Disease Reports...")
report_ids = []
for village, district in villages[:5]:  # Use first 5 villages
    for crop in ["rice", "wheat", "sugarcane", "cotton", "tomato"]:
        if crop in diseases_by_crop:
            # Report 1-2 diseases per crop per village
            for disease_name, symptoms, severity in random.sample(diseases_by_crop[crop], min(2, len(diseases_by_crop[crop]))):
                user_id = f"91{random.randint(7000000000, 9999999999)}"
                report_id = hyperlocal_tracker.report_disease(
                    user_id=user_id,
                    village=village,
                    district=district,
                    crop=crop,
                    disease_name=disease_name,
                    severity=severity,
                    symptoms=symptoms
                )
                report_ids.append((report_id, disease_name))
                print(f"  ✓ {disease_name} in {crop} at {village}")

print(f"\n✅ Created {len(report_ids)} disease reports")

print("\n💊 Recording Treatment Successes...")
success_count = 0
for report_id, disease_name in report_ids[:20]:  # Add treatments for first 20 reports
    if disease_name in treatments:
        for treatment_method, score, cost, days, notes in treatments[disease_name]:
            user_id = f"91{random.randint(7000000000, 9999999999)}"
            hyperlocal_tracker.record_treatment_success(
                report_id=report_id,
                user_id=user_id,
                disease_name=disease_name,
                treatment_method=treatment_method,
                effectiveness_score=score,
                cost=cost,
                duration_days=days,
                notes=notes
            )
            success_count += 1
            print(f"  ✓ {treatment_method} for {disease_name} (Score: {score}/10)")

print(f"\n✅ Recorded {success_count} successful treatments")

print("\n🌟 Adding Best Practices...")
practice_count = 0
for crop, practices in best_practices.items():
    for category, title, description, season in practices:
        village, district = random.choice(villages)
        user_id = f"91{random.randint(7000000000, 9999999999)}"
        practice_id = hyperlocal_tracker.add_best_practice(
            user_id=user_id,
            village=village,
            crop_type=crop,
            category=category,
            title=title,
            description=description,
            season=season
        )
        # Simulate some upvotes
        upvotes = random.randint(5, 50)
        for _ in range(upvotes):
            hyperlocal_tracker.upvote_practice(practice_id)
        practice_count += 1
        print(f"  ✓ {title} for {crop} ({upvotes} upvotes)")

print(f"\n✅ Added {practice_count} best practices")

print("\n" + "=" * 60)
print("🎉 Hyperlocal data seeding complete!")
print("\nData Summary:")
print(f"  • {len(report_ids)} disease reports across 5 villages")
print(f"  • {success_count} treatment success stories")
print(f"  • {practice_count} community best practices")
print("\n💡 Farmers can now see:")
print("  1. What diseases are affecting nearby farmers")
print("  2. What treatments worked for others")
print("  3. Best practices from their community")
