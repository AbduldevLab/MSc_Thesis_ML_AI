def categorical_transform_S6(df): # Step6; Scenario -> Multi class categorical
    df_cleaned = df.copy()
    sent_set = set([str(x).lower() for x in string_sentinels]) | set([str(x).lower() for x in standardised_sentinels])
    numeric_sentinel_set = set(float(x) for x in numeric_sentinels)

    # Helper normaliser
    def _norm(tok):
        if tok is None:
            return None
        s = str(tok).strip().lower()
        if s in blanks:
            return ''
        return s

    # Words -> number map
    word_num_map = {
        'zero':0.0,'one':1.0,'two':2.0,'three':3.0,'four':4.0,'five':5.0,'six':6.0,'seven':7.0,'eight':8.0,'nine':9.0,
        'ten':10.0,'eleven':11.0,'twelve':12.0,'thirteen':13.0,'fourteen':14.0,'fifteen':15.0,'twenty':20.0,
        'thirty':30.0,'forty':40.0,'fifty':50.0,'sixty':60.0,'seventy':70.0,'eighty':80.0,'ninety':90.0,
        'a few':2.0,'a couple':2.0,'few':2.0,'once':1.0,'twice':2.0,'several':3.0,'couple':2.0
    }
    def words_to_num(token):
        if token is None:
            return None
        token = token.strip().lower()
        if token in word_num_map:
            return word_num_map[token]
        try:
            return float(token)
        except Exception:
            return None

    # Regexes for parsing
    RE_TIME = re.compile(r'^\s*(\d{1,2}):(\d{2})\s*$')
    RE_PERCENT = re.compile(r'^\s*(-?\d+(?:\.\d+)?)\s*%\s*$')
    RE_DIRECT_NUM = re.compile(r'^\s*-?\d+(?:\.\d+)?\s*$')
    RE_RANGE = re.compile(r'^\s*(-?\d+(?:\.\d+)?)\s*[-–—/]\s*(-?\d+(?:\.\d+)?)\s*$')
    RE_RANGE_TO = re.compile(r'^\s*(-?\d+(?:\.\d+)?)\s*(?:to|TO)\s*(-?\d+(?:\.\d+)?)\s*$')
    RE_PLUS = re.compile(r'^\s*(-?\d+(?:\.\d+)?)\s*\+\s*$')
    RE_GT = re.compile(r'^\s*(?:>=|>)\s*(-?\d+(?:\.\d+)?)\s*$')
    RE_LT_ANCHOR = re.compile(r'^(?:<|<=)\s*-?\d+(?:\.\d+)?')
    RE_NUM_FIND = re.compile(r'-?\d+(?:\.\d+)?')
    RE_WORD_TOK = re.compile(r"[a-z']+(?:\s[a-z']+)?")
    # RE_SURVEY_TIME = re.compile(r'^\s*(?:[a-z]+\s+)?(\d+(?:\.\d+)?)\s*(?:month|week|year)s?.*$', re.IGNORECASE)

    def norm_return(v):
        try:
            vf = float(v)
        except Exception:
            return None
        if vf in numeric_sentinel_set:
            return 'SENTINEL'
        return vf

    def try_parse_token(x):
        """Return float, 'SENTINEL', or None for unknown token x"""
        if x is None:
            return None

        # preserve numeric pre transformed values
        if isinstance(x, (int, float)):
            if float(x) in numeric_sentinel_set:
                return 'SENTINEL'
            return float(x)

        if isinstance(x, str):
            sx = str(x).strip()
            if (sx.startswith('NOT ') or sx.lower().startswith('not ')) \
                and 'applicable' not in sx.lower() \
                and not sx.lower().startswith('not none'):
                return 0.0
        s = _norm(x)

        if s in ('none', 'none of these', 'none of the these'):  # typo variant too
            return 0.0
        if s.startswith('not none'):
            return 1.0
        # Extending sentinel detection for categorical parsing scenario
        if s == '':
            return 'SENTINEL'
        if 'not applicable' in s or 'does not have' in s or "don't receive" in s or "don\x92t receive" in s or 'unknown' in s:
            return 'SENTINEL'
        if s in sent_set or re.fullmatch(r'[^0-9a-z]+', s):
            return 'SENTINEL'
        if s in ('other', 'other specify') or s.startswith('other (') or s.endswith('(specify)'):
            return 'SENTINEL'

        s0 = s.replace(',', '').replace('$', '').replace('€', '').replace('#', '')
        
        s0 = re.sub(r'(\d+)-', r'\1 -', s0)
        s0 = re.sub(r'-(\d+)', r'- \1', s0)
        
        RE_PREFIX_NUM = re.compile(r'^\s*(-?\d+(?:\.\d+)?)\.\s*.+$')
        
        m = RE_PREFIX_NUM.match(s0)
        if m:
            # If the format is 'NUM. anything', return the number as the category value
            return norm_return(float(m.group(1)))

        # time
        m = RE_TIME.match(s0)
        if m:
            h, mi = float(m.group(1)), float(m.group(2))
            return norm_return(h * 60.0 + mi)

        # percent
        m = RE_PERCENT.match(s0)
        if m:
            return norm_return(float(m.group(1)))

        # direct numeric
        if RE_DIRECT_NUM.match(s0):
            return norm_return(s0)

        # ranges
        m = RE_RANGE.match(s0)
        if m:
            try:
                a, b = float(m.group(1)), float(m.group(2))
                return norm_return((a + b) / 2.0)
            except Exception:
                pass
        m = RE_RANGE_TO.match(s0)
        if m:
            try:
                a, b = float(m.group(1)), float(m.group(2))
                return norm_return((a + b) / 2.0)
            except Exception:
                pass

        # plus / greater than
        m = RE_PLUS.match(s0) or RE_GT.match(s0)
        if m:
            nums = RE_NUM_FIND.findall(s0)
            if nums:
                return norm_return(nums[0])

        # less than
        if RE_LT_ANCHOR.search(s0) or 'less than' in s0:
            nums = RE_NUM_FIND.findall(s0)
            if nums:
                return norm_return(nums[0])

        # or less / more
        m = re.search(r'(-?\d+(?:\.\d+)?)\s*or\s*less', s0)
        if m:
            return norm_return(m.group(1))
        m = re.search(r'(-?\d+(?:\.\d+)?)\s*or\s*more', s0)
        if m:
            return norm_return(m.group(1))
        
        # "more than X but less than Y", "over X but less than Y"
        m = re.search(r'(?:more than|over)\s*e?(-?\d+(?:\.\d+)?)\s*(?:but\s*)?(?:less than|under)\s*e?(-?\d+(?:\.\d+)?)', s0)
        if m:
            try:
                a, b = float(m.group(1)), float(m.group(2))
                return norm_return((a + b) / 2.0)
            except Exception:
                pass

        # "between X and Y" / "between X - Y"
        m = re.search(r'between\s*e?(-?\d+(?:\.\d+)?)\s*(?:and|[-–—/])\s*e?(-?\d+(?:\.\d+)?)', s0)
        if m:
            try:
                a, b = float(m.group(1)), float(m.group(2))
                return norm_return((a + b) / 2.0)
            except Exception:
                pass
        
        # survey time based
        time_map_weeks = {
            'one week': 1.0,
            'two weeks': 2.0,
            'a month (4 weeks)': 4.0,
            'a month/4 weeks': 4.0,
            'three months (13 weeks)': 13.0,
            'three months/13 weeks': 13.0,
            'six months (26 weeks)': 26.0,
            'six months/26 weeks': 26.0,
            'one year (12 months/52 weeks)': 52.0,
            'one year/12 months/52 weeks': 52.0
        }
        if s0 in time_map_weeks:
            return norm_return(time_map_weeks[s0])

        # If a category is '3 months or more', try to extract the number and use upper bound
        if 'months or more' in s0 and RE_NUM_FIND.search(s0):
            nums = RE_NUM_FIND.findall(s0)
            if nums:
                months = float(nums[0])
                return norm_return(months * 4.33) # Convert months to weeks (4.33 weeks per month)

        # Frequency calendar based
        if any(tok in s0 for tok in ('day','week','month','year','daily','never','almost every day','once','twice','thrice','three','several','couple')):
            nums = RE_NUM_FIND.findall(s0)
            if nums:
                val = (float(nums[0]) + float(nums[1])) / 2.0 if len(nums) >= 2 else float(nums[0])
            else:
                if 'once or twice' in s0:
                    val = 1.5
                else:
                    val = None
                    for w in RE_WORD_TOK.findall(s0):
                        wn = words_to_num(w)
                        if wn is not None:
                            val = wn
                            break
            if val is not None:
                if 'day' in s0:
                    if 'week' in s0:
                        return norm_return(val * 4.33)
                    if 'month' in s0:
                        return norm_return(val)
                    if 'daily' in s0 or 'every day' in s0 or 'almost every day' in s0:
                        return norm_return(val * 30.0)
                    return norm_return(val * 4.33)
                if 'week' in s0:
                    return norm_return(val * 4.33)
                if 'month' in s0:
                    return norm_return(val)
                if 'year' in s0:
                    return norm_return(val / 12.0)
                return norm_return(val)

        
        likert_map = { 
            # Likert / ordinals (expanded with quintile/lowest/highest detection)
            'strongly disagree': 0.0, 'disagree': 1.0, 'neither agree nor disagree': 2.0, 'neither': 2.0,
            'agree': 3.0, 'strongly agree': 4.0,
            'very poor': 0.0, 'poor': 1.0, 'fair': 2.0, 'good': 3.0, 'very good': 4.0, 'excellent': 5.0,
            'not at all': 0.0, 'hardly ever': 0.0,
            'a little': 1.0, 'some': 2.0, 'a lot': 3.0, 'alot': 3.0, 'often': 3.0,
            'yes': 1.0, 'no': 0.0, 'sometimes': 2.0, 'rarely': 1.0,
            'pass': 1.0, 'fail': 0.0, '100': 100.0,
            # Problem severity mappings
            'no problem': 0.0, 'minor problem': 1.0, 'moderate problem': 2.0, 'major problem': 3.0,
            # Concern level mappings
            'not at all concerned': 0.0,'somewhat concerned': 1.0,'fairly concerned': 2.0,'very concerned': 3.0,
            # Survey frequency mappings
            'daily / almost daily': 7.0, 'once a week or more': 6.0,'twice a month or more': 5.0,'about once a month': 4.0,
            'every few months': 3.0, 'about once or twice a year': 2.0,'less than once a year': 1.0,'never': 0.0,
            'daily': 7.0,'every day': 7.0,'almost every day': 7.0,'most or all of the time': 7.0,
            'every week': 6.0,'once a week': 6.0,'several times per week': 6.0,
            'twice a month': 5.0,'two a month': 5.0,'several times per month': 5.0,'once or twice a month': 5.0,
            'once a month': 4.0, 'once or twice a year': 2.0,'less than once a month': 1.0,
        }
        
        if s0 in likert_map:
            return float(likert_map[s0])
        
        _CONJ_RE = re.compile(r'\b(?:and|but|or|because|however|although|answered)\b')
        _NO_SPECIFIC = ['problem', 'response', 'prompt']

        if s0.startswith('no ') and not any(w in s0 for w in _NO_SPECIFIC) and not _CONJ_RE.search(s0):
            return 0.0

        if s0.startswith('yes ') and not _CONJ_RE.search(s0):
            return 1.0

        # Quintile / ordinal like tokens: 'lowest', '2nd quintile', 'highest'
        if 'quintile' in s0 or 'lowest' in s0 or 'highest' in s0 or 'middle' in s0 or 'median' in s0:
                if 'lowest' in s0:
                    return norm_return(1.0)
                if 'highest' in s0:
                    return norm_return(5.0)
                if 'middle' in s0 or 'median' in s0:
                    return norm_return(3.0)
                mq = re.search(r'(\d+)(?:st|nd|rd|th)?\s+quintile', s0)
                if mq:
                    return norm_return(float(mq.group(1)))
                nums = RE_NUM_FIND.findall(s0)
                if nums:
                    return norm_return(nums[0])
        
        if 'adjacent' in s0: # Adjacent boxes: keep semantic average if present
            nums = RE_NUM_FIND.findall(s0)
            if len(nums) >= 2:
                return norm_return((float(nums[0]) + float(nums[1])) / 2.0)
            elif nums:
                return norm_return(nums[0])
            return None

        # Fallback: first number
        nums = RE_NUM_FIND.findall(s0)
        if nums:
            return norm_return(nums[0])

        return None

    def category_sort_key(u):
        us = _norm(u) or ''
        parsed = try_parse_token(us)
        if isinstance(parsed, (int, float)):
            return (0, float(parsed), us)
        if us == 'no' or us.startswith('no ') or us.startswith('not '):
            return (1, 0.0, us)
        if 'yes' in us:
            if 'both' in us or 'two' in us:
                return (1, 2.0, us)
            if 'one' in us:
                return (1, 1.0, us)
            return (1, 1.0, us)
        amount_keywords = ['none', 'not at all', 'hardly ever', 'a little', 'some', 'a lot', 'alot', 'often', 'sometimes', 'rarely']
        for i, key in enumerate(amount_keywords):
            if key in us:
                return (2, float(i), us)
        if 'adjacent boxes' in us or 'adjacent numbers' in us:
            nums = RE_NUM_FIND.findall(us)
            if len(nums) >= 2:
                a, b = float(nums[0]), float(nums[1])
                return (10, (a + b) / 2.0, us)
            elif nums:
                return (10, float(nums[0]), us)
            return (10, 0, us)
        return (99, 0, us)

    # Operate only on categorical columns
    cat_cols = df_cleaned.select_dtypes(include='category').columns.tolist()
    for col in cat_cols:
        uniques = list(dict.fromkeys(df_cleaned[col].tolist())) # Preserve original tokens with types (do NOT cast to str here)
        normalised_pairs = [(u, _norm(u)) for u in uniques] # Build normalised pairs keeping original token too
        # Keep tokens that are non sentinel and parseable (strings or numbers)
        non_sentinel = [u for u, nu in normalised_pairs if (nu and nu not in sent_set and nu not in blanks and try_parse_token(nu) != 'SENTINEL')]

        if not non_sentinel:
            continue

        # Computing parse results keyed by normalized string (but keep list of originals too)
        parse_results = { _norm(u): try_parse_token(_norm(u)) for u in non_sentinel }

        numeric_count = sum(1 for v in parse_results.values() if isinstance(v, (int, float)))
        sentinel_parsed_count = sum(1 for v in parse_results.values() if v == 'SENTINEL')
        all_parse_numeric = (numeric_count + sentinel_parsed_count == len(parse_results))

        if all_parse_numeric:
            # Map token string -> numeric (SENTINEL -> -1.0)
            code_map = { k: (float(v) if isinstance(v, (int, float)) else -1.0) for k, v in parse_results.items() }

            def map_to_numeric(x):
                # Preserve the already numeric cells (except numeric sentinels)
                if isinstance(x, (int, float)) and not pd.isna(x):
                    if float(x) in numeric_sentinel_set:
                        return -1.0
                    return float(x)
                if pd.isna(x):
                    return -1.0
                xs = _norm(x)
                if not xs or xs in sent_set or xs in blanks or re.fullmatch(r'[^0-9a-z]+', xs):
                    return -1.0
                return float(code_map.get(xs, -1.0))

            df_cleaned[col] = df_cleaned[col].apply(map_to_numeric).astype(float)

        else:
            first_seen_norm = []
            seen = set()
            for u in non_sentinel:
                nu = _norm(u)
                if nu not in seen:
                    first_seen_norm.append(nu)
                    seen.add(nu)

            parse_results = {nu: try_parse_token(nu) for nu in first_seen_norm}
            max_reserved_val = -1.0
            for nu, val in parse_results.items():
                if isinstance(val, (int, float)):
                    max_reserved_val = max(max_reserved_val, val) # Assuming any parsed float is a reserved ID if it came from the map
            start_i = int(max_reserved_val) + 1 
            if start_i == 0: # Ensure we never start at 0 if 0 is a reserved category i.e for ('no')
                start_i = 1
            string_tokens = [nu for nu in first_seen_norm if not isinstance(parse_results.get(nu), (int, float))]
            sorted_strings = sorted(string_tokens, key=category_sort_key)

            code_map_strings = { norm_tok: i for i, norm_tok in enumerate(sorted_strings, start=start_i) }

            def map_mixed(x):
                if isinstance(x, (int, float)) and not pd.isna(x):# Preserve real numeric cell values
                    if float(x) in numeric_sentinel_set:
                        return -1.0
                    return float(x)
                if pd.isna(x):
                    return -1.0
                xs = _norm(x)
                if xs == '' or xs in sent_set or xs in blanks or re.fullmatch(r'[^0-9a-z]+', xs):
                    return -1.0
                
                parsed_val = try_parse_token(xs)
                if parsed_val == 'SENTINEL':
                    return -1.0
                if isinstance(parsed_val, (int, float)):# Captures 'no' (0.0), 'yes' (1.0), and other hardcoded likert values.
                    return float(parsed_val)
                if xs in code_map_strings:
                    return float(code_map_strings[xs])
                return -1.0

            df_cleaned[col] = df_cleaned[col].apply(map_mixed).astype(float)

    # Final sweep on numeric columns
    for c in df_cleaned.select_dtypes(include='float').columns:
        df_cleaned[c] = df_cleaned[c].fillna(-1.0)
        df_cleaned[c] = df_cleaned[c].replace(list(numeric_sentinel_set), -1.0)

    return df_cleaned
