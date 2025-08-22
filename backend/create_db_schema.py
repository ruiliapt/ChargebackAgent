#!/usr/bin/env python3
"""
Create database schema with all required fields
"""

from app import app, db

if __name__ == "__main__":
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        print("✅ Database schema created successfully with all fields!")
        print("   - Added category, subcategory, reason_code, card_network fields")
        print("   - Ready for data loading")

