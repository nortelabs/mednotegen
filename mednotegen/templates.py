from .synthea_integration import get_random_patient_with_meds

class DoctorNoteTemplate:
    filename_prefix = "doctor_note"
    def generate(self):
        patient, meds, conditions = get_random_patient_with_meds()
        name = f"{patient['FIRST']} {patient['LAST']}"
        date = patient['BIRTHDATE']
        diagnosis = conditions.get('DESCRIPTION', 'N/A')
        medication = ', '.join(meds['DESCRIPTION'].unique()) if not meds.empty else "None"
        instructions = "Take medications as prescribed. Follow up as needed."
        lines = [
            f"Doctor Note",
            f"Date: {date}",
            f"Patient: {name}",
            f"Diagnosis: {diagnosis}",
            f"Prescribed Medication: {medication}",
            "\nInstructions:",
            instructions,
        ]
        return {"lines": lines}

class PatientReportTemplate:
    filename_prefix = "patient_report"
    def generate(self):
        import re
        from datetime import datetime, date
        from .synthea_integration import get_random_patient_with_meds
        patient, meds, conditions = get_random_patient_with_meds()

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
            today = datetime.now()
            age = today.year - birth_year - ((today.month, today.day) < (birth_month, birth_day))
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
        med_section = '\n'.join(med_lines)

        # Conditions (use patient_conditions DataFrame, filter out non-clinical entries)
        cond_lines = []
        non_conditions = [
            "Received higher education", "Completed high school", "Completed college", "Graduated", "Education", "Employed", "Unemployed", "Student", "Retired", "Homemaker", "Military service"
        ]
        filtered_conditions = conditions.copy()
        if not filtered_conditions.empty and 'DESCRIPTION' in filtered_conditions.columns:
            mask = ~filtered_conditions['DESCRIPTION'].str.contains('|'.join(non_conditions), case=False, na=False)
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
        cond_section = '\n'.join(cond_lines)

        # Care Plans
        careplans = patient.get('CAREPLANS', [])
        if isinstance(careplans, str):
            careplans = [careplans] if careplans else []
        care_lines = []
        for cp in careplans:
            if isinstance(cp, dict):
                start = cp.get('START', '')
                status = cp.get('STOP', '')
                desc = cp.get('DESCRIPTION', '')
                reason = cp.get('REASONDESCRIPTION', '')
                acts = cp.get('ACTIVITIES', [])
                start_fmt = start[:10] if start else ''
                status_str = '[CURRENT]' if not status or pd.isna(status) else '[STOPPED]'
                care_lines.append(f"{start_fmt} {status_str} : {desc}")
                if reason:
                    care_lines.append(f"     Reason: {reason}")
                for act in acts:
                    care_lines.append(f"     Activity: {act}")
            else:
                care_lines.append(str(cp))
        if not care_lines:
            care_lines = [
                f"{date.today()} [CURRENT] : Lifestyle counseling\n     Activity: Recommendation to increase exercise"
            ]
        care_section = '\n'.join(care_lines)

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
                obs_lines.append(f"{date_obs[:10]} : {obs.get('DESCRIPTION',''):<40} {value} {unit}")
        # Add the randomized observations
        obs_lines.append(f"{today_str} : Body Weight                              {body_weight}")
        obs_lines.append(f"{today_str} : Body Height                              {body_height}")
        obs_lines.append(f"{today_str} : Body Mass Index                          {body_bmi}")
        obs_lines.append(f"{today_str} : Systolic Blood Pressure                  {systolic_bp} mmHg")
        obs_lines.append(f"{today_str} : Diastolic Blood Pressure                 {diastolic_bp} mmHg")

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
        proc_section = '\n'.join(proc_lines)

        # Encounters
        encounters = patient.get('ENCOUNTERS', [])
        if isinstance(encounters, str):
            encounters = [encounters] if encounters else []
        enc_lines = []
        for enc in encounters:
            if isinstance(enc, dict):
                date = enc.get('DATE', '')
                desc = enc.get('DESCRIPTION', '')
                enc_lines.append(f"{date[:10]} : {desc}")
            else:
                enc_lines.append(str(enc))
        if not enc_lines:
            enc_lines = [
                f"{date.today()} : Outpatient Encounter"
            ]
        enc_section = '\n'.join(enc_lines)

        # Header block (demographics)
        lines = [
            f"PATIENT REPORT",
            "="*70,
            f"Name:           {name}",
            f"Date of Birth:  {dob}",
            f"Gender:         {sex}",
            f"Age:            {age_str}",
            f"Race:           {race}",
            f"Ethnicity:      {ethnicity}",
            f"Marital Status: {patient.get('MARITAL', 'Unknown')}",
            "-"*70,
        ]
        # Allergies
        lines.append("ALLERGIES:")
        if allergies:
            lines.extend([f"  - {a}" for a in allergies])
        else:
            lines.append("  None reported")
        lines.append("-"*70)

        # Encounters (chronological)
        lines.append("ENCOUNTERS:")
        lines.append("-"*70)
        lines.extend(enc_lines)
        lines.append("-"*70)

        # Conditions (limit to 4)
        lines.append("CONDITIONS:")
        lines.append("-"*70)
        if cond_lines:
            lines.extend(cond_lines[:4])
        else:
            lines.append("  None reported")
        lines.append("-"*70)

        # Medications
        lines.append("MEDICATIONS:")
        lines.append("-"*70)
        lines.extend(med_lines)
        lines.append("-"*70)

        # Procedures
        lines.append("PROCEDURES:")
        lines.append("-"*70)
        lines.extend(proc_lines)
        lines.append("-"*70)

        # Observations
        lines.append("OBSERVATIONS:")
        lines.append("-"*70)
        lines.extend(obs_lines)
        lines.append("-"*70)

        # Footer
        lines.append("END OF REPORT")
        lines.append("="*70)

        return {"lines": lines}
