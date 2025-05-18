import pandas as pd
import numpy as np

# Load the data
df_noaa = pd.read_pickle("noaa_fips_cleaned_sorted.pkl")
df_eaglei_subset = pd.read_pickle("eaglei_subset_clean_sorted.pkl")

def prepare_for_merge_asof(df, by_col, on_col):
    """Ensure perfect sorting that merge_asof will accept"""
    # Convert to numpy arrays for precise control
    groups = df[by_col].values
    times = df[on_col].values.astype('datetime64[ns]')
    
    # Sort first by group, then by time using mergesort
    sorted_indices = np.lexsort((times, groups))
    
    # Apply the sorting
    sorted_df = df.iloc[sorted_indices].reset_index(drop=True)
    
    # Final verification
    verify_sorting(sorted_df, by_col, on_col)
    
    return sorted_df

def verify_sorting(df, by_col, on_col):
    """Rigorous sorting verification"""
    current_group = None
    last_time = None
    
    for i in range(len(df)):
        if df[by_col].iloc[i] != current_group:
            current_group = df[by_col].iloc[i]
            last_time = df[on_col].iloc[i]
        else:
            if df[on_col].iloc[i] < last_time:
                raise ValueError(f"Sort violation at index {i}")
            last_time = df[on_col].iloc[i]
    print("✓ Perfect sorting verified")

# Prepare both DataFrames without renaming EagleI columns
df_noaa_prepared = prepare_for_merge_asof(df_noaa, 'full_fips_code', 'END_DT_UTC')
df_eaglei_prepared = prepare_for_merge_asof(df_eaglei_subset, 'fips_code', 'EAGLEI_DT_UTC')

# Perform the merge using original column names
try:
    merged_df = pd.merge_asof(
        df_noaa_prepared,
        df_eaglei_prepared,
        left_on='END_DT_UTC',
        right_on='EAGLEI_DT_UTC',
        left_by='full_fips_code',
        right_by='fips_code',
        direction='forward',
        tolerance=pd.Timedelta('2h')
    )
    print("✅ Merge succeeded after rigorous sorting")
    
except Exception as e:
    print(f"❌ Merge failed: {e}")
    print("\n⚠️ Implementing manual merge_asof logic as fallback")
    
    # Manual implementation using original column names
    merged_records = []
    for fips in df_noaa_prepared['full_fips_code'].unique():
        noaa_group = df_noaa_prepared[df_noaa_prepared['full_fips_code'] == fips]
        eaglei_group = df_eaglei_prepared[df_eaglei_prepared['fips_code'] == fips]
        
        for _, noaa_row in noaa_group.iterrows():
            # Find closest matching row in eaglei data
            matches = eaglei_group[
                (eaglei_group['EAGLEI_DT_UTC'] >= noaa_row['END_DT_UTC']) &
                (eaglei_group['EAGLEI_DT_UTC'] <= noaa_row['END_DT_UTC'] + pd.Timedelta('2h'))
            ]
            
            if not matches.empty:
                best_match = matches.iloc[0]  # First match due to sorting
                merged_row = {**noaa_row.to_dict(), **{f"eaglei_{k}": v for k, v in best_match.to_dict().items()}}
                merged_records.append(merged_row)
            else:
                merged_records.append(noaa_row.to_dict())
    
    # Create merged DataFrame with prefixed EagleI columns
    merged_df = pd.DataFrame(merged_records)
    
    # Clean up column names if needed
    merged_df.columns = [col.replace('eaglei_', '') if col.startswith('eaglei_') else col for col in merged_df.columns]

# Final checks
print("\nMerge operation completed. Result shape:", merged_df.shape)
print("Columns in merged result:", merged_df.columns.tolist())

merged_df.to_pickle("noaa_eaglei_merged.pkl")