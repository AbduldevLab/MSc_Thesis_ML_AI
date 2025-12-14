# Cleaning pipeline to all waves
dfs_cleaned = {}

# flattened dtype df
dfs_flat = {wave: flatten_column_types(df) for wave, df in dfs.items()} # flatten dtypes

# Original df
display(scenario_count_table(dfs_flat).style.set_caption("Original Table - pre cleaning")) # display original scenario count table

# Step 1: Clean empty/missing values
dfs_step1 = {wave: clean_empty_missing(df) for wave, df in dfs_flat.items()} # apply step 1 cleaning
display(scenario_count_table(dfs_step1).style.hide(axis="index").set_caption("Step 1: Empty / Blank - post cleaning"))

# Step 2: Clean sentinel values
dfs_step2 = {wave: clean_sentinel(df) for wave, df in dfs_step1.items()} # apply step 2 cleaning
display(scenario_count_table(dfs_step2).style.hide(axis="index").set_caption("Step 2: Sentinel - post cleaning"))

# Step 3: Numerical Transformation
dfs_step3 = {wave: numerical_transform(df) for wave, df in dfs_step2.items()} # apply step 3 cleaning
display(scenario_count_table(dfs_step3).style.hide(axis="index").set_caption("Step 3: Numeric Transformation - post cleaning"))

# Step 4: Categorical Transformation for censored scenario
dfs_step4 = {wave: categorical_transform_S4(df) for wave, df in dfs_step3.items()} # apply step 4 cleaning
display(scenario_count_table(dfs_step4).style.hide(axis="index").set_caption("Step 4: Category Transformation S4 - post cleaning"))

# Step 5: Categorical Transformation for binary values
dfs_step5 = {wave: categorical_transform_S5(df) for wave, df in dfs_step4.items()} # apply step 5 cleaning
display(scenario_count_table(dfs_step5).style.hide(axis="index").set_caption("Step 5: Category Transformation S5 - post cleaning"))

# Step 6: Categorical Transformation for multi class/mixed values
dfs_step6 = {wave: categorical_transform_S6(df) for wave, df in dfs_step5.items()} # apply step 6 cleaning
display(scenario_count_table(dfs_step6).style.hide(axis="index").set_caption("Step 6: Category Transformation S6 - post cleaning"))

dfs_cleaned = dfs_step6


def show_grouped_vars_for_scenarios(dfs, scenarios_to_show): # Function to show grouped variables per scenario across waves -> markdown format
    """
    Used to inspect the scenario variables/features that need handling for transformation/cleaning. 
    A pre and post cleaning helper function to identify variables that need specific handling and to
    Inspect actual changes for a scenario from previous cleaning step to current step.
    """
    
    print("# Category Transformation Mapping")
    print(f"## Scenario: {scenarios_to_show}") # Markdown mapping dictionary header
    for wave, df in dfs.items():
        print(f"\n### ==================== {wave.upper()} ====================")
        
        mapping_df = detect_column_scenario_mapping(df) # Get scenario mapping

        for scenario in scenarios_to_show:
            vars_in_scenario = mapping_df[mapping_df['Scenario'] == scenario]['Variable'].tolist() # Variables in scenario
            # print(f"\n--- Scenario: {scenario} ---") # Scenario header for pipeline git commit
            print(f"\n--- Total: {len(vars_in_scenario)} ---") # \n
            if not vars_in_scenario:
                print("No variables found.")
                continue

            # Dictionary: frozen set(values) -> list of variables
            groups = {}

            for var in vars_in_scenario:
                unique_vals = list(dict.fromkeys(df[var].dropna()))  # Preserve first-seen order
                key = tuple(unique_vals)  # Use ordered tuple as key

                if key not in groups: # Initialise list if key not present
                    groups[key] = []
                groups[key].append(var) # Append variable to the group

            # Print grouped variables in markdown format friendly for Notion -> mapping dictionary
            for value_set, var_list in groups.items():
                print("\n*Variables:*","`" + ", ".join(var_list) + "`  ") # \n
                print(f"*Pre transformed values:* {list(value_set)}  ")
                
                # Pull transformed values from dfs_cleaned / specific step using preserved order
                try:
                    df_before = df[var_list[0]]
                    df_after = dfs_cleaned[wave][var_list[0]]
                    
                    # Build transformed list in same order as original values
                    transformed_vals = []
                    seen = set()
                    
                    for orig_val in value_set: # Iterate through original values in order
                            mask = df_before == orig_val
                            if mask.any():
                                trans_vals = df_after[mask].unique().tolist() # Get unique transformed values
                                if trans_vals:
                                    transformed_vals.append(trans_vals[0]) # Append first transformed value
                except Exception:
                    transformed_vals = []
                print(f"*Transformed numeric:* `{transformed_vals}`")
  
            
scenarios_to_show = SCENARIOS
# scenarios_to_show = ["Clean numeric"]
# scenarios_to_show = ["Censored / bracketed numeric"]
# scenarios_to_show = ["Binary categorical"]
# scenarios_to_show = ["Multi class categorical / mixed"]

show_grouped_vars_for_scenarios(dfs_cleaned, scenarios_to_show) # prev step == comparison to current step else current step transformed/cleaned for ready .md dictionary