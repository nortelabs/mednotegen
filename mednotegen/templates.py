from .synthea_integration import get_random_patient_with_meds



class PatientReportTemplate:
    filename_prefix = "patient_report"
    def __init__(self, gender=None, min_age=None, max_age=None, modules=None, reference_date=None, synthea_csv_dir=None):
        self.gender = gender
        self.min_age = min_age
        self.max_age = max_age
        self.modules = modules
        self.reference_date = reference_date
        self.synthea_csv_dir = synthea_csv_dir
    def generate(self):
        import re
        from datetime import datetime, date
        from .synthea_integration import get_random_patient_with_meds
        patient, meds, conditions, careplans = get_random_patient_with_meds(
            gender=self.gender,
            min_age=self.min_age,
            max_age=self.max_age,
            modules=self.modules,
            reference_date=self.reference_date,
            synthea_csv_dir=self.synthea_csv_dir
        )

        # Helper to strip trailing digits from names
        def strip_digits(s):
            return re.sub(r'\d+$', '', str(s)).strip()

        name = f"{strip_digits(patient['FIRST'])} {strip_digits(patient['LAST'])}"
        dob = patient['BIRTHDATE']
        sex = patient.get('GENDER', 'Unknown').capitalize()
        # Calculate age if possible
        try:
            birth_year = int(dob[:4])
            birth_month = int(dob[5:7])
            birth_day = int(dob[8:10])
            # Use reference_date if provided, else today
            if self.reference_date is not None:
                try:
                    ref_dt = datetime.strptime(str(self.reference_date), "%Y%m%d")
                except Exception:
                    ref_dt = datetime.now()
            else:
                ref_dt = datetime.now()
            age = ref_dt.year - birth_year - ((ref_dt.month, ref_dt.day) < (birth_month, birth_day))
            age_str = f"{age} yrs"
        except Exception:
            age_str = "-"

        # Visit date: most recent med start or today
        visit_date = dob
        if not meds.empty and 'START' in meds.columns:
            valid_dates = meds['START'].dropna()
            if not valid_dates.empty:
                visit_date = str(valid_dates.max())
        visit_date = re.sub(r'T.*', '', str(visit_date))

        import random
        import pandas as pd
        today_str = str(date.today())
        body_weight = f"{round(random.uniform(50, 110), 1)} kg"
        body_height = f"{round(random.uniform(150, 200), 1)} cm"
        body_bmi = f"{round(random.uniform(18.5, 35.0), 1)} kg/m2"
        systolic_bp = f"{random.randint(100, 145)}"
        diastolic_bp = f"{random.randint(60, 95)}"
        race_options = [
            'White',
            'Black or African American',
            'Asian',
            'American Indian or Alaska Native',
            'Native Hawaiian or Other Pacific Islander',
            'Other',
            'Multiple'
        ]
        ethnicity_options = [
            'Hispanic or Latino',
            'Non-Hispanic'
        ]
        race = patient.get('RACE', None)
        ethnicity = patient.get('ETHNICITY', None)
        if not race or race.strip().lower() == 'white':
            race = random.choice(race_options)
        if not ethnicity or ethnicity.strip().lower() in ['non-hispanic', 'not hispanic or latino']:
            ethnicity = random.choice(ethnicity_options)
        marital = patient.get('MARITAL', 'N/A')

        # Allergies
        allergies = patient.get('ALLERGIES', [])
        if isinstance(allergies, str):
            allergies = [allergies] if allergies else []
        if not allergies:
            allergies = [random.choice([
                'Penicillin', 'Latex', 'Peanuts', 'Shellfish', 'Aspirin', 'Sulfa drugs', 'Cat hair', 'Pollen'
            ])]
        allergy_section = '\n'.join([f"{a}" for a in allergies])

        import pandas as pd
        def safe_fmt(val):
            if isinstance(val, str):
                return val[:10]
            if pd.isna(val):
                return ''
            return str(val)[:10]

        # Medications (limit to 5, and show which condition each is for if available)
        med_lines = []
        if not meds.empty and 'DESCRIPTION' in meds.columns:
            for _, row in meds.iterrows():
                if len(med_lines) >= 5:
                    break
                start = row.get('START', '')
                status = row.get('STOP', '')
                med = row.get('DESCRIPTION', '')
                reason = row.get('REASONDESCRIPTION', '')
                start_fmt = safe_fmt(start)
                status_str = '[CURRENT]' if not status or pd.isna(status) else '[STOPPED]'
                reason_str = f" for {reason}" if reason else ''
                med_lines.append(f"{start_fmt} {status_str} : {med}{reason_str}")
        if not med_lines:
            med_lines = [
                f"{date.today()} [CURRENT] : No medications prescribed"
            ]
        med_section = '\n'.join(f'- {line}' for line in med_lines)

        # Conditions (use patient_conditions DataFrame, filter out non-clinical entries)
        cond_lines = []
        non_conditions = [
            "Received higher education", "Completed high school", "Completed college", "Graduated", "Education", "Employed", "Unemployed", "Student", "Retired", "Homemaker", "Military service",
            "Educated to high school level (finding)", "Education level", "Educational attainment", "High school education", "Bachelor's degree", "Master's degree", "Doctorate degree", "GED", "Diploma", "School", "Degree", "Literacy",
            # Employment-related
            "employ", "occupation", "job", "work", "unemployed", "retired", "layoff", "career", "profession", "business owner", "self-employed", "laborer", "manager", "office worker", "technician", "engineer", "teacher", "service worker"
        ]
        filtered_conditions = conditions.copy()
        if not filtered_conditions.empty and 'DESCRIPTION' in filtered_conditions.columns:
            import re
            escaped_patterns = [re.escape(s) for s in non_conditions]
            pattern = '|'.join(escaped_patterns)
            mask = ~filtered_conditions['DESCRIPTION'].str.contains(pattern, case=False, na=False, regex=True)
            filtered_conditions = filtered_conditions[mask]
        if not filtered_conditions.empty:
            for _, cond in filtered_conditions.iterrows():
                start = cond.get('START', '')
                stop = cond.get('STOP', '')
                desc = cond.get('DESCRIPTION', '')
                reason = cond.get('REASONDESCRIPTION', '')
                start_fmt = safe_fmt(start)
                stop_fmt = safe_fmt(stop)
                cond_lines.append(f"{start_fmt} - {stop_fmt:<11}: {desc}{' for ' + reason if reason else ''}")
        if not cond_lines:
            cond_lines = [
                f"{date.today()} -            : No chronic conditions found"
            ]
        cond_section = '\n'.join(f'- {line}' for line in cond_lines)

        # Care Plans (from Synthea careplans DataFrame)
        care_lines = []
        import pandas as pd
        def safe_fmt(val):
            if isinstance(val, str):
                return val[:10]
            if pd.isna(val):
                return ''
            return str(val)[:10]
        if careplans is not None and not careplans.empty:
            for _, cp in careplans.iterrows():
                start = cp.get('START', '')
                stop = cp.get('STOP', '')
                desc = cp.get('DESCRIPTION', '')
                reason = cp.get('REASONDESCRIPTION', '')
                start_fmt = safe_fmt(start)
                status_str = '[CURRENT]' if not stop or pd.isna(stop) else '[STOPPED]'
                line = f"{start_fmt} {status_str} : {desc}"
                if reason:
                    if reason and str(reason).lower() != 'nan':
                        line += f" (Reason: {reason})"
                care_lines.append(line)
        if not care_lines:
            care_lines = [
                "None reported"
            ]
        care_section = '\n'.join(f'- {line}' for line in care_lines)

        # Observations
        observations = patient.get('OBSERVATIONS', [])
        if isinstance(observations, str):
            observations = [observations] if observations else []
        obs_lines = []
        for obs in observations:
            if isinstance(obs, dict):
                date_obs = obs.get('DATE', '')
                desc = obs.get('DESCRIPTION', '').lower()
                value = obs.get('VALUE', '')
                unit = obs.get('UNIT', '')
                obs_lines.append(f"- {date_obs[:10]} : {obs.get('DESCRIPTION',''):<40} {value} {unit}")
        # Add the randomized observations
        obs_lines.append(f"- {today_str} : Body Weight                              {body_weight}")
        obs_lines.append(f"- {today_str} : Body Height                              {body_height}")
        obs_lines.append(f"- {today_str} : Body Mass Index                          {body_bmi}")
        obs_lines.append(f"- {today_str} : Systolic Blood Pressure                  {systolic_bp} mmHg")
        obs_lines.append(f"- {today_str} : Diastolic Blood Pressure                 {diastolic_bp} mmHg")

        # Procedures
        procedures = patient.get('PROCEDURES', [])
        if isinstance(procedures, str):
            procedures = [procedures] if procedures else []
        proc_lines = []
        for proc in procedures:
            if isinstance(proc, dict):
                date = proc.get('DATE', '')
                desc = proc.get('DESCRIPTION', '')
                reason = proc.get('REASONDESCRIPTION', '')
                proc_lines.append(f"{date[:10]} : {desc}" + (f" for {reason}" if reason else ''))
            else:
                proc_lines.append(str(proc))
        if not proc_lines:
            proc_lines = [
                f"{date.today()} : Blood draw"
            ]
        proc_section = '\n'.join(f'- {line}' for line in proc_lines)

        # Encounters
        encounters = patient.get('ENCOUNTERS', [])
        if isinstance(encounters, str):
            encounters = [encounters] if encounters else []
        enc_lines = []
        for enc in encounters:
            if isinstance(enc, dict):
                date = enc.get('DATE', '')
                desc = enc.get('DESCRIPTION', '')
                reason = enc.get('REASONDESCRIPTION', '')
                enc_lines.append(f"{date[:10]} : {desc}" + (f" for {reason}" if reason else ''))
            else:
                enc_lines.append(str(enc))
        if not enc_lines:
            enc_lines = [
                f"{date.today()} : Office visit"
            ]
        enc_section = '\n'.join(f'- {line}' for line in enc_lines)

        # Header block (demographics)
        lines = [
            f"{name}",
            "="*18,
            f"Race:           {race}",
            f"Ethnicity:      {ethnicity}",
            f"Gender:         {sex[0] if sex else ''}",
            f"Age:            {age_str}",
            f"Birth Date:     {dob[:10]}",
            f"Marital Status: {marital}",
            "-"*80,
            f"ALLERGIES: {', '.join(allergies) if allergies else 'N/A'}",
            "-"*80,
            "MEDICATIONS:",
            *med_section.splitlines(),
            "-"*80,
            "CONDITIONS:",
            *cond_section.splitlines()[:5],
            "-"*80,
            "CARE PLANS:",
            *care_section.splitlines(),
            "-"*80,
            "OBSERVATIONS:",
            *obs_lines,
            "-"*80,
            "PROCEDURES:",
            *proc_section.splitlines(),
            "-"*80,
            "ENCOUNTERS:",
            *enc_section.splitlines(),
            "-"*80,
        ]
        lines.append("END OF REPORT")
        lines.append("="*70)
        return {"lines": lines}
