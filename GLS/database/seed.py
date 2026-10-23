"""
Production seed dataset for GLORENZA SALON AHMEDABAD.
Guarantees clean connection disposal without SQLite database lock.
"""

from database.connection import get_db_connection
from utils.validators import hash_password


def seed_database():
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()

            # 1. 6 Dedicated Salon Stations
            chairs = [
                ("GLZ-CHR-01", "Styling Station 01 (Hair Designing)", "General", "Available"),
                ("GLZ-CHR-02", "Styling Station 02 (Creative Cut)", "General", "Available"),
                ("GLZ-CHR-03", "Hair Spa & Scalp Detox Suite", "Hair Wash", "Available"),
                ("GLZ-CHR-04", "Hydra-Facial & Aesthetic Suite", "Facial Room", "Available"),
                ("GLZ-CHR-05", "Nail Couture & Pedicure Lounge", "Pedicure Station", "Available"),
                ("GLZ-CHR-06", "VIP Grooming & Royal Bridal Suite", "VIP", "Available")
            ]
            for c in chairs:
                cursor.execute(
                    "INSERT INTO chairs (chair_code, chair_name, chair_type, status) VALUES (?, ?, ?, ?) ON CONFLICT(chair_code) DO NOTHING;",
                    c
                )

            # 2. 30 Salon Services
            services = [
                ("GLZ-SRV-01", "Men's Precision Fade & Haircut", "Men's Hair", "Wash, fade cut and styling", 35, 450.0),
                ("GLZ-SRV-02", "Royal Hot Towel Beard Sculpting", "Men's Beard", "Blade line, steam & argan oil", 30, 400.0),
                ("GLZ-SRV-03", "Men's Charcoal Anti-Pollution D-Tan", "Men's Skin", "Detan mask & cold compress", 30, 650.0),
                ("GLZ-SRV-04", "Men's Hair Color Ammonia Free", "Men's Hair", "Natural black/dark brown tint", 30, 850.0),
                ("GLZ-SRV-05", "Men's Keratin Beard Straightening", "Men's Beard", "Intense beard frizz control", 45, 1200.0),
                ("GLZ-SRV-06", "Men's Scalp Detox & Anti-Dandruff Spa", "Men's Hair", "Tea-tree scrub & high-frequency ozone", 45, 1200.0),
                ("GLZ-SRV-07", "Men's Royal Face & Neck Cleanup", "Men's Skin", "Ultrasonic exfoliation & face mask", 40, 950.0),
                ("GLZ-SRV-08", "Men's Sports Pedicure & Foot Scrub", "Men's Spa", "De-stress salt soak & massage", 45, 1100.0),
                ("GLZ-SRV-09", "Signature Precision Haircut & Blowdry", "Women's Hair", "Senior stylist cut & blowdry styling", 45, 950.0),
                ("GLZ-SRV-10", "Creative Director Bespoke Restyling", "Women's Hair", "Face contouring restyling cut", 60, 1800.0),
                ("GLZ-SRV-11", "Moroccan Argan Deep Moisture Spa", "Women's Hair", "Deep lipid restoration therapy", 60, 2400.0),
                ("GLZ-SRV-12", "Keratin Protein Smoothing Treatment", "Women's Hair", "Formaldehyde-free realignment", 120, 6000.0),
                ("GLZ-SRV-13", "Hair Botox Anti-Ageing Treatment", "Women's Hair", "Hyaluronic acid & caviar repair", 120, 7500.0),
                ("GLZ-SRV-14", "Balayage Couture Hand-Painted Highlights", "Women's Hair", "Bespoke dimensional highlights", 150, 7000.0),
                ("GLZ-SRV-15", "Global Ammonia-Free Hair Color", "Women's Hair", "Rich permanent radiant tone", 90, 4200.0),
                ("GLZ-SRV-16", "Root Touch-Up & Bond Multiplier", "Women's Hair", "100% grey coverage with Olaplex", 60, 2200.0),
                ("GLZ-SRV-17", "Cysteine Protein Curl Taming", "Women's Hair", "Botanical protein curl softening", 120, 6500.0),
                ("GLZ-SRV-18", "Hydra-Facial Express Radiance", "Skin & Facial", "Deep suction & hyaluronic infusion", 60, 3500.0),
                ("GLZ-SRV-19", "O3+ Bridal Radiant Oxygen Facial", "Skin & Facial", "Brightening multi-layer oxygen complex", 75, 4500.0),
                ("GLZ-SRV-20", "24K Gold Luxury Illuminating Facial", "Skin & Facial", "Colloidal gold cellular rejuvenation", 75, 5500.0),
                ("GLZ-SRV-21", "Sara D-Tan Instant Radiance Pack", "Skin & Facial", "Eucalyptus tan-removal pack", 30, 800.0),
                ("GLZ-SRV-22", "Ultrasonic Pore Deep Cleanse", "Skin & Facial", "Blackhead extraction & ice globes", 45, 1400.0),
                ("GLZ-SRV-23", "Under-Eye Dark Circle Brightening Treatment", "Skin & Facial", "Peptide mask & cold roll massage", 30, 1100.0),
                ("GLZ-SRV-24", "Therapeutic Rose Quartz Pedicure", "Hands & Feet", "Aroma soak, scrub & leg massage", 60, 1500.0),
                ("GLZ-SRV-25", "Signature Paraffin Thermal Manicure", "Hands & Feet", "Thermal wax hydration & polish", 45, 1200.0),
                ("GLZ-SRV-26", "Gel Nail Extensions with Custom Art", "Nails", "Full sculpted extensions with art", 90, 2800.0),
                ("GLZ-SRV-27", "Gel Polish Application (Hands/Feet)", "Nails", "High-gloss chip-free UV coat", 40, 1000.0),
                ("GLZ-SRV-28", "Full Body Organic Polishing & Scrub", "Body Spa", "Walnut scrub & body butter wrap", 90, 4800.0),
                ("GLZ-SRV-29", "High-Definition Occasion Party Makeup", "Makeup", "HD airbrush foundation & mink lashes", 90, 5000.0),
                ("GLZ-SRV-30", "Royal Luxury Bridal Couture Package", "Bridal", "Complete bridal makeover, hair couture", 240, 22000.0)
            ]
            for s in services:
                cursor.execute(
                    """
                    INSERT INTO services (service_code, name, category, description, duration_minutes, price, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'active')
                    ON CONFLICT(service_code) DO NOTHING;
                    """,
                    s
                )

            # 3. 6 Specialists
            staff_members = [
                ("Aarav Mehta", "9898011111", "Creative Hair Director", "Balayage, Precision Cut", 10, 100000.0, 15.0),
                ("Sneha Parikh", "9898022222", "Master Bridal Stylist", "HD Makeup, Bridal Couture", 8, 90000.0, 14.0),
                ("Meera Singhania", "9898033333", "Senior Aesthetician", "Hydra-Facials, 24K Gold Rituals", 7, 80000.0, 12.0),
                ("Rohan Verma", "9898044444", "Senior Hair Stylist", "Keratin Botox, Moroccan Spa", 6, 70000.0, 10.0),
                ("Pooja Shah", "9898055555", "Nail & Spa Specialist", "Therapeutic Pedicure, Manicures", 5, 60000.0, 10.0),
                ("Karan Joshi", "9898066666", "Master Barber & Groomer", "Beard Sculpting, Men's Detan", 4, 50000.0, 8.0)
            ]
            for idx, (s_name, s_phone, s_role, s_spec, s_exp, s_sal, s_comm) in enumerate(staff_members, start=1):
                s_code = f"GLZ-STF-000{idx}"
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role, full_name, phone, status) VALUES (?, ?, 'staff', ?, ?, 'active') ON CONFLICT(phone) DO NOTHING;",
                    (s_phone, hash_password("Staff@123"), s_name, s_phone)
                )
                cursor.execute("SELECT id FROM users WHERE phone = ?;", (s_phone,))
                u_row = cursor.fetchone()
                if u_row:
                    cursor.execute(
                        """
                        INSERT INTO staff (user_id, staff_code, full_name, phone, role, specialization, experience_years, salary, service_commission_percent, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
                        ON CONFLICT(staff_code) DO NOTHING;
                        """,
                        (u_row[0], s_code, s_name, s_phone, s_role, s_spec, s_exp, s_sal, s_comm)
                    )
                    cursor.execute("SELECT id FROM staff WHERE staff_code = ?;", (s_code,))
                    stf_row = cursor.fetchone()
                    if stf_row:
                        cursor.execute("SELECT id FROM services;")
                        srv_rows = cursor.fetchall()
                        for srv_row in srv_rows:
                            cursor.execute("INSERT OR IGNORE INTO staff_services (staff_id, service_id) VALUES (?, ?);", (stf_row[0], srv_row[0]))

            # 4. 50 Inventory Items
            inventory_items = [
                ("GLZ-PRD-01", "Disposable Salon Cutting Sheets (100 Pcs)", "Consumables", "GL-Pack", 450.0, 0.0, 12, 3),
                ("GLZ-PRD-02", "Sanitary Elastic Neck Paper Rolls (5 Pack)", "Consumables", "BarberPro", 320.0, 0.0, 15, 4),
                ("GLZ-PRD-03", "Non-Woven Facial Cotton Pads (500 Pcs)", "Consumables", "Dermacot", 260.0, 0.0, 20, 5),
                ("GLZ-PRD-04", "Facial Tissue Box (200 Pulls)", "Consumables", "Origami", 85.0, 0.0, 30, 6),
                ("GLZ-PRD-05", "Single-Edge Razor Blades (Box of 100)", "Consumables", "Laser Super", 180.0, 0.0, 15, 3),
                ("GLZ-PRD-06", "Aluminum Highlighting Foil Rolls (300m)", "Consumables", "FoilMaster", 650.0, 0.0, 8, 2),
                ("GLZ-PRD-07", "Nitrile Gloves Powder-Free (Box of 100)", "Consumables", "SafeTouch", 420.0, 0.0, 12, 3),
                ("GLZ-PRD-08", "Disposable Wooden Waxing Spatulas (200 Pcs)", "Consumables", "WaxPro", 160.0, 0.0, 10, 2),
                ("GLZ-PRD-09", "Disposable Pedicure Tub Liners (100 Pcs)", "Consumables", "SpaCare", 380.0, 0.0, 10, 2),
                ("GLZ-PRD-10", "Disposable Headbands with Velcro (100 Pcs)", "Consumables", "BeautyPro", 290.0, 0.0, 10, 2),
                ("GLZ-PRD-11", "Sara Oxy D-Tan Professional Pack (500g Tub)", "Backbar Skin", "Sara Beauty", 850.0, 0.0, 8, 2),
                ("GLZ-PRD-12", "O3+ Radiant Facial Single Dose Kits (10 Kits)", "Backbar Skin", "O3+", 3800.0, 0.0, 5, 2),
                ("GLZ-PRD-13", "Aroma Magic Activated Charcoal Cleanser (1L)", "Backbar Skin", "Aroma Magic", 620.0, 0.0, 6, 2),
                ("GLZ-PRD-14", "Rica Brazilian Liposoluble Hard Wax (800ml)", "Backbar Skin", "Rica", 1450.0, 0.0, 6, 2),
                ("GLZ-PRD-15", "O3+ Purifying Hydrating Face Toner (1000ml)", "Backbar Skin", "O3+", 890.0, 0.0, 5, 1),
                ("GLZ-PRD-16", "L'Oreal Majirel Base 1 Black (50ml Tube)", "Backbar Color", "L'Oreal", 320.0, 0.0, 15, 4),
                ("GLZ-PRD-17", "L'Oreal Majirel 3 Dark Brown (50ml Tube)", "Backbar Color", "L'Oreal", 320.0, 0.0, 18, 5),
                ("GLZ-PRD-18", "L'Oreal Majirel 5 Light Brown (50ml Tube)", "Backbar Color", "L'Oreal", 320.0, 0.0, 12, 3),
                ("GLZ-PRD-19", "L'Oreal Developer 20 Vol / 6% (1000ml)", "Backbar Color", "L'Oreal", 450.0, 0.0, 10, 3),
                ("GLZ-PRD-20", "L'Oreal Developer 30 Vol / 9% (1000ml)", "Backbar Color", "L'Oreal", 450.0, 0.0, 10, 3),
                ("GLZ-PRD-21", "Schwarzkopf Blondme Premium Lightener 9+ (450g)", "Backbar Color", "Schwarzkopf", 1850.0, 0.0, 6, 2),
                ("GLZ-PRD-22", "Olaplex Salon Bond Multiplier No. 1 (525ml)", "Backbar Hair", "Olaplex", 9500.0, 0.0, 4, 1),
                ("GLZ-PRD-23", "Olaplex Bond Perfector No. 2 (525ml)", "Backbar Hair", "Olaplex", 9500.0, 0.0, 4, 1),
                ("GLZ-PRD-24", "Moroccanoil Professional Backbar Spa Mask (1L)", "Backbar Hair", "Moroccanoil", 4200.0, 0.0, 5, 1),
                ("GLZ-PRD-25", "L'Oreal Absolut Repair Clarifying Shampoo (1.5L)", "Backbar Hair", "L'Oreal", 1850.0, 0.0, 6, 2),
                ("GLZ-PRD-26", "Wahl Cordless Magic Clip Professional Trimmer", "Equipment", "Wahl", 6200.0, 0.0, 4, 1),
                ("GLZ-PRD-27", "Ikonic Pro 2500+ Ionic Hair Dryer", "Equipment", "Ikonic", 3400.0, 0.0, 5, 1),
                ("GLZ-PRD-28", "Ikonic Titanium Flat Iron Straightener", "Equipment", "Ikonic", 4200.0, 0.0, 4, 1),
                ("GLZ-PRD-29", "Hydra-Facial 7-in-1 Smart Aesthetic Station", "Equipment", "HydraPro", 48000.0, 0.0, 2, 1),
                ("GLZ-PRD-30", "UV Towel Sterilizer & Warmer Cabinet (16L)", "Equipment", "SaniCare", 4500.0, 0.0, 3, 1),
                ("GLZ-PRD-31", "Moroccanoil Treatment Original Oil (100ml)", "Retail Hair", "Moroccanoil", 2600.0, 3500.0, 14, 3),
                ("GLZ-PRD-32", "Kerastase Bain Satin Hydrating Shampoo (250ml)", "Retail Hair", "Kerastase", 2100.0, 2900.0, 18, 4),
                ("GLZ-PRD-33", "Kerastase Masquintense Nutrition Mask (200ml)", "Retail Hair", "Kerastase", 2600.0, 3600.0, 10, 2),
                ("GLZ-PRD-34", "Olaplex No. 3 Hair Perfector (100ml)", "Retail Hair", "Olaplex", 2200.0, 2950.0, 15, 3),
                ("GLZ-PRD-35", "Olaplex No. 4 Bond Maintenance Shampoo (250ml)", "Retail Hair", "Olaplex", 2200.0, 2950.0, 12, 3),
                ("GLZ-PRD-36", "Olaplex No. 5 Bond Maintenance Conditioner", "Retail Hair", "Olaplex", 2200.0, 2950.0, 12, 3),
                ("GLZ-PRD-37", "L'Oreal Absolut Repair Molecular Mask (250ml)", "Retail Hair", "L'Oreal", 1400.0, 1950.0, 22, 5),
                ("GLZ-PRD-38", "L'Oreal Vitamino Color Acidic Sealer (210ml)", "Retail Hair", "L'Oreal", 1200.0, 1650.0, 16, 4),
                ("GLZ-PRD-39", "Schwarzkopf Osis+ Dust It Mattifying Powder (10g)", "Retail Styling", "Schwarzkopf", 750.0, 1150.0, 25, 6),
                ("GLZ-PRD-40", "Schwarzkopf Session Label Strong Hair Spray (300ml)", "Retail Styling", "Schwarzkopf", 850.0, 1300.0, 20, 5),
                ("GLZ-PRD-41", "Dermalogica Daily Microfoliant Scrub (74g)", "Retail Skin", "Dermalogica", 3800.0, 4900.0, 8, 2),
                ("GLZ-PRD-42", "Dermalogica Special Cleansing Gel (250ml)", "Retail Skin", "Dermalogica", 2700.0, 3500.0, 10, 2),
                ("GLZ-PRD-43", "Forest Essentials Soundarya Beauty Elixir (30ml)", "Retail Skin", "Forest Essentials", 2400.0, 3200.0, 10, 3),
                ("GLZ-PRD-44", "Forest Essentials Facial Ubtan Narangi (80g)", "Retail Skin", "Forest Essentials", 950.0, 1350.0, 12, 3),
                ("GLZ-PRD-45", "Beardo Godfather Luxury Beard Oil (30ml)", "Retail Beard", "Beardo", 350.0, 550.0, 30, 8),
                ("GLZ-PRD-46", "Beardo Dark Side Perfume Body Spray (150ml)", "Retail Grooming", "Beardo", 400.0, 650.0, 25, 5),
                ("GLZ-PRD-47", "Ustraa Hair Growth Vitalizer Serum (100ml)", "Retail Hair", "Ustraa", 520.0, 799.0, 18, 4),
                ("GLZ-PRD-48", "BBlunt Heat Protection & Shine Mist (150ml)", "Retail Styling", "BBlunt", 380.0, 550.0, 20, 5),
                ("GLZ-PRD-49", "O.P.I ProSpa Protective Hand Cream (120ml)", "Retail Spa", "OPI", 950.0, 1400.0, 14, 3),
                ("GLZ-PRD-50", "The Man Company Charcoal Blackhead Strips (6 Pcs)", "Retail Grooming", "TMC", 180.0, 299.0, 35, 10)
            ]
            for p in inventory_items:
                cursor.execute(
                    """
                    INSERT INTO products (product_code, name, category, brand, purchase_price, selling_price, stock_quantity, min_stock_alert, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
                    ON CONFLICT(product_code) DO NOTHING;
                    """,
                    p
                )
    finally:
        conn.close()