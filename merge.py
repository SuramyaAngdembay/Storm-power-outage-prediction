import pandas as pd
import numpy as np
import warnings

# Assume df_noaa exists from Step 3
# Assume df_eaglei exists from Step 2
df_noaa = pd.read_csv("noaa_minimal_feature_eng.csv")
df_eaglei = pd.read_csv("eaglei_2014_2024.csv")
print("\nStarting Step 4: Merging NOAA and Eaglei Data...")

# --- 1. Create full 5-digit FIPS code in df_noaa ---
print("Creating 5-digit FIPS code in NOAA data...")
if 'STATE_FIPS' in df_noaa.columns and 'CZ_FIPS' in df_noaa.columns:
    # Ensure source columns are strings and handle potential floats/NaNs gracefully first
    df_noaa['STATE_FIPS_STR'] = df_noaa['STATE_FIPS'].astype(str).str.split('.').str[0]
    df_noaa['CZ_FIPS_STR'] = df_noaa['CZ_FIPS'].astype(str).str.split('.').str[0]

    # Pad STATE_FIPS to 2 digits, CZ_FIPS to 3 digits
    state_fips_padded = df_noaa['STATE_FIPS_STR'].str.zfill(2)
    cz_fips_padded = df_noaa['CZ_FIPS_STR'].str.zfill(3)

    # Concatenate, but only if both parts are valid (not NaN after conversion)
    # Create mask for valid rows
    valid_fips_mask = state_fips_padded.notna() & cz_fips_padded.notna()
    df_noaa['full_fips_code'] = np.nan # Initialize with NaN
    df_noaa.loc[valid_fips_mask, 'full_fips_code'] = state_fips_padded[valid_fips_mask] + cz_fips_padded[valid_fips_mask]

    # Drop intermediate columns
    df_noaa.drop(columns=['STATE_FIPS_STR', 'CZ_FIPS_STR'], inplace=True)

    # Check how many NaNs were created
    fips_nan_count = df_noaa['full_fips_code'].isna().sum()
    if fips_nan_count > 0:
        print(f"  Warning: Created {fips_nan_count} NaN values in 'full_fips_code' due to missing STATE or CZ FIPS.")
        # Optional: Drop rows with missing FIPS before merging if needed
        # df_noaa.dropna(subset=['full_fips_code'], inplace=True)

    print("  'full_fips_code' created.")
    # Verify one FIPS code
    print(f"  Example NOAA full_fips_code: {df_noaa['full_fips_code'].iloc[0] if not df_noaa.empty else 'N/A'}")

else:
    print("Error: STATE_FIPS or CZ_FIPS missing from df_noaa. Cannot create full FIPS code.")
    # Handle error - cannot proceed with merge
    exit()

# Verify Eaglei FIPS code formatting (should be done already)
print(f"  Example Eaglei fips_code: {df_eaglei['fips_code'].iloc[0] if not df_eaglei.empty else 'N/A'}")


# --- 2. Prepare df_eaglei Key (already done) ---
# Ensure required columns exist
if not all(col in df_eaglei.columns for col in ['fips_code', 'EAGLEI_DT_UTC', 'customers_out']):
     print("Error: Required columns missing from df_eaglei.")
     exit()
# Select only necessary columns from Eaglei to save memory during merge
df_eaglei_subset = df_eaglei[['fips_code', 'EAGLEI_DT_UTC', 'customers_out']].copy()
print(f"Prepared Eaglei subset with {len(df_eaglei_subset)} rows.")


# --- 3. Sort DataFrames ---
print("Sorting DataFrames (this might take time)...")
# Sort NOAA by the new full FIPS and storm END time
df_noaa.sort_values(by=['full_fips_code', 'END_DT_UTC'], inplace=True)
# Sort Eaglei subset by FIPS and outage time
df_eaglei_subset.sort_values(by=['fips_code', 'EAGLEI_DT_UTC'], inplace=True)
print("DataFrames sorted.")

df_eaglei_subset['EAGLEI_DT_UTC'] = pd.to_datetime(df_eaglei_subset['EAGLEI_DT_UTC'], errors='coerce', utc=True)
df_noaa['END_DT_UTC'] = pd.to_datetime(df_noaa['END_DT_UTC'], errors='coerce', utc=True)
# And similarly for df_noaa['END_DT_UTC']
df_eaglei_subset['fips_code'] = df_eaglei_subset['fips_code'].astype(str).str.zfill(5)

# --- 4. Define Target & Tolerance ---
# Let's look for outages within 6 hours AFTER a storm ends
merge_tolerance = pd.Timedelta('6h')
print(f"Merge tolerance set to: {merge_tolerance}")
print(df_noaa['END_DT_UTC'].dtype)
print(df_noaa['full_fips_code'].dtype)
print(df_eaglei_subset['EAGLEI_DT_UTC'].dtype)
print(df_eaglei_subset['fips_code'].dtype)

print("Performing merge_asof (this is memory intensive and may take significant time)...")
try:
    # Merge df_noaa (left) with df_eaglei_subset (right)
    # For each storm in df_noaa, find the Eaglei record matching FIPS
    # where Eaglei time is >= storm end time, within the tolerance.
    merged_df = pd.merge_asof(
        df_noaa,                     # Left DataFrame
        df_eaglei_subset,            # Right DataFrame (subset)
        left_on='END_DT_UTC',        # Time column in left df (storm end)
        right_on='EAGLEI_DT_UTC',    # Time column in right df (outage time)
        left_by='full_fips_code',    # Key column in left df (county FIPS)
        right_by='fips_code',        # Key column in right df (county FIPS)
        direction='forward',         # Find Eaglei time >= left time
        tolerance=merge_tolerance    # Look ahead up to 6 hours
    )
    print("merge_asof complete.")

    # Rename columns coming from Eaglei for clarity, handling potential conflicts
    merged_df.rename(columns={
        'EAGLEI_DT_UTC': 'MATCHED_OUTAGE_DT_UTC',
        'customers_out': 'MATCHED_CUSTOMERS_OUT'
        # Note: 'fips_code' column from df_eaglei_subset will also be present
    }, inplace=True)

    # Check results
    print(f"Merged DataFrame length: {len(merged_df)}")
    if len(merged_df) != len(df_noaa):
         print("Warning: Length of merged df differs from original NOAA df. This shouldn't happen with merge_asof.")

    # See how many storms found a matching outage record within the window
    matches_found = merged_df['MATCHED_OUTAGE_DT_UTC'].notna().sum()
    print(f"Found matching outage records for {matches_found} out of {len(merged_df)} storm events within the {merge_tolerance} window.")

except MemoryError:
    print("!!! MEMORY ERROR during merge_asof !!!")
    print("The DataFrames are too large for a direct merge in available memory.")
    print("Next steps would require chunking, Dask, or more memory.")
    merged_df = None # Indicate failure
except Exception as e:
    print(f"An unexpected error occurred during merge_asof: {e}")
    merged_df = None # Indicate failure


# --- Display Info and Head of Merged Data (if successful) ---
if merged_df is not None:
    print("\n--- Merged DataFrame Info ---")
    merged_df.info(verbose=True, show_counts=True)

    print("\n--- Merged DataFrame Head ---")
    print(merged_df[[
        'EVENT_ID', 'full_fips_code', 'END_DT_UTC',
        'MATCHED_OUTAGE_DT_UTC', 'MATCHED_CUSTOMERS_OUT'
        # Add other relevant NOAA columns to view
    ]].head())

    print("\nStep 4 (Merge) Complete.")
else:
    print("\nStep 4 (Merge) FAILED due to errors.")

# 'merged_df' now holds the result IF the merge was successful.
# It has one row per original NOAA storm event.
# Rows where no outage was found within the window will have NaT/NaN
# in MATCHED_OUTAGE_DT_UTC and MATCHED_CUSTOMERS_OUT.
