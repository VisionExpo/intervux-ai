import sys
import os
from pathlib import Path

# Add project root to sys.path
# Script is in backend/scripts/validate_schema_signature.py
# Project root is two levels up from backend/scripts/
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from backend.infrastructure.database.migration_manager import SCHEMA_SIGNATURE
from backend.infrastructure.database.database import Base

# Import all modules that define SQLAlchemy models to populate Base.metadata
try:
    import backend.infrastructure.database.database as db_models
    import backend.models.recruiter_dashboard_models as recruiter_models
    import backend.models.candidate_portal as candidate_models
    print("Successfully imported all model modules.")
except ImportError as e:
    print(f"Error importing models: {e}")
    sys.exit(1)

CORE_TABLES = {"users", "candidates", "job_posts"}

def validate_signature():
    """
    Validates that the SCHEMA_SIGNATURE in migration_manager.py 
    matches the actual SQLAlchemy models.
    """
    errors = []
    warnings = []
    
    # 1. Check if all tables in signature exist in models
    for table_name, expected_columns in SCHEMA_SIGNATURE.items():
        is_core = table_name in CORE_TABLES
        
        if table_name not in Base.metadata.tables:
            msg = f"Table '{table_name}' defined in SCHEMA_SIGNATURE but not found in SQLAlchemy models."
            if is_core:
                errors.append(msg)
            else:
                warnings.append(msg)
            continue
        
        table = Base.metadata.tables[table_name]
        actual_columns = table.columns.keys()
        
        # 2. Check if all expected columns exist in the model
        missing_columns = [col for col in expected_columns if col not in actual_columns]
        if missing_columns:
            msg = f"Table '{table_name}' is missing columns in SQLAlchemy models: {missing_columns}"
            if is_core:
                errors.append(msg)
            else:
                warnings.append(msg)
            
    # 3. Check for tables in models that are NOT in signature
    model_tables = set(Base.metadata.tables.keys())
    signature_tables = set(SCHEMA_SIGNATURE.keys())
    
    untracked_tables = model_tables - signature_tables
    untracked_tables = {t for t in untracked_tables if not t.startswith('alembic')}
    
    if untracked_tables:
        print(f"NOTICE: The following tables exist in models but are not tracked in SCHEMA_SIGNATURE: {list(untracked_tables)}")
        print("Consider adding them to SCHEMA_SIGNATURE for better drift detection.")

    if warnings:
        print("\n--- SCHEMA SIGNATURE WARNINGS ---")
        for warning in warnings:
            print(f"WARNING: {warning}")

    if errors:
        print("\n--- SCHEMA SIGNATURE VALIDATION FAILED (CORE TABLES) ---")
        for error in errors:
            print(f"ERROR: {error}")
        return False
    
    print("\n--- SCHEMA SIGNATURE VALIDATION PASSED ---")
    print(f"Validated {len(SCHEMA_SIGNATURE)} tables.")
    return True

if __name__ == "__main__":
    success = validate_signature()
    sys.exit(0 if success else 1)
