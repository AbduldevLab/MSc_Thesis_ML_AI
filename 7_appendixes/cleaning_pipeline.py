# Cleaning pipeline to all waves
dfs_cleaned = {}

# flattened dtype df
dfs_flat = {wave: flatten_column_types(df) for wave, df in dfs.items()} # flatten dtypes

# Original df
display(scenario_count_table(dfs_flat).style.set_caption("--- Original Table - pre cleaning ---")) # display original scenario count table

# Step 1: Clean empty/missing values
dfs_step1 = {wave: clean_empty_missing(df) for wave, df in dfs_flat.items()} # apply step 1 cleaning
display(scenario_count_table(dfs_step1).style.hide(axis="index").set_caption("--- Step 1: Empty / Blank - post cleaning ---"))

# Step 2: Clean sentinel values
dfs_step2 = {wave: clean_sentinel(df) for wave, df in dfs_step1.items()} # apply step 2 cleaning
display(scenario_count_table(dfs_step2).style.hide(axis="index").set_caption("--- Step 2: Sentinel - post cleaning ---"))

# Step 3: Numerical Transformation
dfs_step3 = {wave: numerical_transform(df) for wave, df in dfs_step2.items()} # apply step 3 cleaning
display(scenario_count_table(dfs_step3).style.hide(axis="index").set_caption("--- Step 3: Numeric Transformation - post cleaning ---"))

# Step 4: Categorical Transformation for censored scenario
dfs_step4 = {wave: categorical_transform_S4(df) for wave, df in dfs_step3.items()} # apply step 4 cleaning
display(scenario_count_table(dfs_step4).style.hide(axis="index").set_caption("--- Step 4: Category Transformation S4 - post cleaning ---"))

# Step 5: Categorical Transformation for binary values
dfs_step5 = {wave: binary_transform_S5(df) for wave, df in dfs_step4.items()} # apply step 5 cleaning
display(scenario_count_table(dfs_step5).style.hide(axis="index").set_caption("--- Step 5: Binary Transformation S5 - post cleaning ---"))

# Step 6: Categorical Transformation for multi class/mixed values
dfs_step6 = {wave: categorical_transform_S6(df) for wave, df in dfs_step5.items()} # apply step 6 cleaning
display(scenario_count_table(dfs_step6).style.hide(axis="index").set_caption("--- Step 6: Category Transformation S6 - post cleaning ---"))

dfs_cleaned = dfs_step6