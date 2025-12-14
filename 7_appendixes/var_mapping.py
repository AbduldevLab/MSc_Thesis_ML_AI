# Sentinel values (numeric and string)
# -1 and -1.0 is sentinel but will be used in the clean pipeline
standardised_sentinels = {'-1', '-1.0', -1, -1.0} #  set -> duplicates removed -> counts correct -> single value detection is zero
numeric_sentinels = [-1, -1.0, -98, -98.0, -99, -99.0,
                     95, 95.0, 96, 96.0, 98, 98.0, 99, 99.0]
string_sentinels = [str(x) for x in numeric_sentinels] + [f"_{x}" for x in numeric_sentinels] + \
    ['na', 'n/a', 'refused', 'missing', 'dk', 'rf', 'refused', "refuse", 'none', 'no response', 'nan', 'not answered', 'no answer',
     'not applicable','no consent','dont know',"don't know","didn't answer",'prefer not to say', 'task not done', 'insufficient sample', 'unable to record',
     '__', '*']
blanks = ['', ' ', '\t', '\n']

SCENARIOS = [
    "Empty / blank values",
    "Numeric with sentinel",
    "Clean numeric",
    "Censored / bracketed numeric",
    "Binary categorical",
    "Multi class categorical / mixed",
    "Single value categorical",
    "Special symbol / mixed",
    "Unknown / complex mixed"
]


# flatten all dtypes across the waves to float and category
def flatten_column_types(df):
    df_flat = df.copy()

    for col in df_flat.columns:
        if pd.api.types.is_numeric_dtype(df_flat[col]): # Numeric columns
            df_flat[col] = df_flat[col].astype(float)  # Convert to float
        else:
            df_flat[col] = (  # Convert to string, strip whitespace, lowercase, then category
                df_flat[col]
                .astype(str)
                .str.strip()
                .str.lower()
                .astype('category')
            )

    return df_flat

def detect_column_scenario_mapping(df, sample_size=10):
    summary = []

    # Regex patterns
    special_symbols_pattern = r'[^A-Za-z0-9\s\.,\-+&/()]' # special symbols excluding common numeric formatting
    bracketed_numeric_pattern = r"\d{1,3}(?:,\d{3})*[-/]\d{1,3}(?:,\d{3})*|\d+\s*[<>+-]"  # patterns like "10-20", "30/40", ">=50"
    sentinel_set = set(x.lower() for x in string_sentinels) # Lowercase string sentinels for comparison

    for col in df.columns:
        col_data = df[col].copy()
        dtype = str(col_data.dtype) # get data type as string

        # Convert to string for sentinel / blank detection
        str_vals = col_data.astype(str).str.lower().str.strip() # lowercase and strip whitespace
        clean_vals = col_data[~str_vals.isin(sentinel_set) & ~(str_vals.isin(blanks))] # remove sentinels and blanks
        
        # Remove sentinels and blanks for scenario detection only
        vals_no_sentinel = clean_vals[~clean_vals.astype(str).str.lower().isin(sentinel_set)
                                      & ~clean_vals.astype(str).str.lower().isin(blanks)].unique()
        num_unique_no_sentinel = len(vals_no_sentinel)
        
        # Check if any sentinel values are present
        sentinel_present = str_vals.isin(sentinel_set).any()

        # Detection flags
        empty_detected = str_vals.isin(blanks).any() or len(col_data) == 0 

        # Numeric detection: coerce to numeric, NaNs for non-numeric
        numeric_vals = pd.to_numeric(clean_vals, errors='coerce') # coerce non-numeric to NaN
        numeric_like = numeric_vals.notna().all() and len(clean_vals) > 0 # all values are numeric-like after cleaning

        sentinel_detected = str_vals[~str_vals.isin(standardised_sentinels)].isin(sentinel_set).any() # or col_data.eq(-1.0).any() # check for sentinel presence
        censored_detected = clean_vals.astype(str).str.contains(bracketed_numeric_pattern).any() # check for bracketed numeric patterns

        # Binary categorical detection (exactly 2 unique values after cleaning)
        binary_categorical_detected = False
        if dtype == 'category':
            if num_unique_no_sentinel == 2:
                binary_categorical_detected = True
            elif num_unique_no_sentinel == 1 and sentinel_present:
                binary_categorical_detected = True

        # Multi-class categorical (3+ unique values, object/category)
        multi_class_categorical_detected = num_unique_no_sentinel > 2 and dtype == 'category'

        # Single value categorical
        single_value_detected = num_unique_no_sentinel == 1 and not binary_categorical_detected

        # Special symbols detection (ignore numeric formatting)
        symbol_detected = clean_vals.astype(str).str.contains(special_symbols_pattern).any()

        # Mixed types detection
        mixed_detected = len(set(type(v) for v in col_data)) > 1 # more than one data type present

      # Determine scenario in order of pipeline
        if empty_detected:
            scenario = SCENARIOS[0]
            handling = "Replace numeric/categorical empty/blank with -1.0"
        elif numeric_like and sentinel_detected:
            scenario = SCENARIOS[1]
            handling = "Replace numeric sentinel values with -1.0"
        elif numeric_like and not sentinel_detected:
            scenario = SCENARIOS[2]
            handling = "Keep as numeric"
        elif censored_detected:
            scenario = SCENARIOS[3]
            handling = "Convert numeric ranges to midpoints or keep as categorical"
        elif binary_categorical_detected:
            scenario = SCENARIOS[4]
            handling = "Encode as 0/1 or keep as category"
        elif multi_class_categorical_detected:
            scenario = SCENARIOS[5]
            handling = "One-hot encode, label encode, or keep as category"
        elif single_value_detected:
            scenario = SCENARIOS[6]
            handling = "Keep as category / constant column"
        elif symbol_detected:
            scenario = SCENARIOS[7]
            handling = "Inspect and preprocess based on context"
        else:
            scenario = SCENARIOS[8]
            handling = "Inspect manually / complex mixed types"

        sample_values = list(col_data.unique()[:sample_size]) # sample unique values

        summary.append({
            'Variable': col,
            'DataType': dtype,
            'UniqueValues': num_unique_no_sentinel,
            'Scenario': scenario,
            'SuggestedHandling': handling,
            'SampleValues': sample_values
        })

    return pd.DataFrame(summary)