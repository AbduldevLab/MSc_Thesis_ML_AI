def show_grouped_vars_for_scenarios(dfs_original, dfs_transformed, scenarios_to_show): # Function to show grouped variables per scenario across waves -> markdown format
    """
    Used to inspect the scenario variables/features that need handling for transformation/cleaning. 
    A pre and post cleaning helper function to identify variables that need specific handling and to
    Inspect actual changes for a scenario from previous cleaning step to current step.
    """
    
    print("# Category Transformation Mapping")
    # print(f"\n## Scenarios: {scenarios_to_show}") # Markdown mapping dictionary header
    for wave in dfs_original.keys():
        print(f"\n### ==================== {wave.upper()} ====================")
        
        mapping_df = detect_column_scenario_mapping(dfs_transformed[wave]) # Get scenario mapping from transformed/cleaned to see overall changes for all variables 
        # mapping_df = detect_column_scenario_mapping(dfs_original[wave]) # Get scenario mapping from original to see untransformed values

        for scenario in scenarios_to_show:
            vars_in_scenario = mapping_df[mapping_df['Scenario'] == scenario]['Variable'].tolist() # Variables in scenario
            print(f"\n--- Scenario {scenario}: {len(vars_in_scenario)} ---") # Scenario header for pipeline git commit
            if not vars_in_scenario:
                print("\nNo variables found.")
                continue

            # Dictionary: frozen set(values) -> list of variables
            groups = {}

            for var in vars_in_scenario:
                unique_vals = list(dict.fromkeys(dfs_original[wave][var].dropna()))  # Preserve first seen order from ORIGINAL
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
                    df_before = dfs_original[wave][var_list[0]]
                    df_after = dfs_transformed[wave][var_list[0]]
                    
                    # Build transformed list in same order as original values
                    transformed_vals = []                    
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

show_grouped_vars_for_scenarios(dfs, dfs_cleaned, scenarios_to_show) # prev step == comparison to current step else current step transformed/cleaned for ready .md dictionary