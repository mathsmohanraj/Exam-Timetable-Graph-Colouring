import pandas as pd
import os
import csv
import shutil

def deep_clean_text(text):
    """புள்ளிகள், இடைவெளிகளை நீக்கி மேட்ச் செய்ய உதவும்"""
    if pd.isna(text): return ""
    return str(text).replace(".", "").replace(" ", "").upper().strip()

def run_final_exam_system():
    try:
        # 1. மாணவர் கோப்புகளைப் படித்தல்
        years = {'I Year': 'I YEAR.csv', 'II Year': 'II YEAR.csv', 'III Year': 'III YEAR.csv'}
        all_students = []

        print("படிநிலை 1: மாணவர் கோப்புகளை ஆய்வு செய்கிறது...")
        for year_label, file_name in years.items():
            if os.path.exists(file_name):
                with open(file_name, 'r', encoding='latin-1') as f:
                    reader = csv.reader(f)
                    headers = [h.strip() for h in next(reader) if h.strip()]
                    for row in reader:
                        for idx, reg_no in enumerate(row):
                            if idx < len(headers):
                                clean_reg = str(reg_no).strip()
                                if clean_reg and len(clean_reg) > 5 and clean_reg.lower() != 'nan':
                                    all_students.append({
                                        'Register No': clean_reg,
                                        'Department': headers[idx],
                                        'Year': year_label
                                    })

        student_df = pd.DataFrame(all_students)
        total_stu = len(student_df)
        print(f"வெற்றி! கண்டறியப்பட்ட மொத்த மாணவர்கள்: {total_stu}")

        # 2. ஹால் விவரங்கள்
        h_file = 'Updated Halls File.csv'
        halls_df = pd.read_csv(h_file, encoding='latin-1')
        halls_df['CAN SIT'] = pd.to_numeric(halls_df['CAN SIT'], errors='coerce').fillna(0).astype(int)
        halls_df = halls_df[halls_df['CAN SIT'] > 0]

        # 3. சீட்டிங் அலோகேஷன்
        allocated = []
        idx = 0
        for _, hall in halls_df.iterrows():
            cap = int(hall['CAN SIT'])
            block, hno = str(hall.get('BLOCK', 'A')), str(hall.get('HALL NO', ''))
            for seat in range(1, cap + 1):
                if idx < total_stu:
                    s = student_df.iloc[idx]
                    allocated.append({
                        'Block': block, 'Hall No': hno, 'Seat No': seat,
                        'Register No': s['Register No'], 'Department': s['Department'], 'Year': s['Year']
                    })
                    idx += 1
                else: break

        seating_df = pd.DataFrame(allocated)

        # 4. டைம் டேபிள் இணைப்பு
        tt_file = 'time table new.csv'
        tt_df = pd.read_csv(tt_file, encoding='latin-1', engine='python', on_bad_lines='skip')
        tt_df.columns = [str(c).strip().upper() for c in tt_df.columns]

        # மேப்பிங்
        year_map = {"I Year": "I", "II Year": "II", "III Year": "III"}
        seating_df['Y_K'] = seating_df['Year'].map(year_map)
        seating_df['D_K'] = seating_df['Department'].apply(deep_clean_text)

        dept_col = 'DEPARTMENT' if 'DEPARTMENT' in tt_df.columns else 'DEPT'
        tt_df['D_M'] = tt_df[dept_col].apply(deep_clean_text)
        tt_df['Y_M'] = tt_df['YEAR'].astype(str).str.strip().str.upper()

        master = pd.merge(seating_df, tt_df, left_on=['D_K', 'Y_K'], right_on=['D_M', 'Y_M'], how='left')

        # 5. சேமித்தல் மற்றும் தனித்தனி ஹால் லிஸ்ட்
        master.to_csv('Master_Seating_Plan_2026.csv', index=False, encoding='utf-8-sig')

        output_folder = "Hall_Lists"
        if os.path.exists(output_folder): shutil.rmtree(output_folder)
        os.makedirs(output_folder)

        for h, group in master.groupby('Hall No'):
            group.to_csv(f"{output_folder}/Hall_{str(h).replace('/', '_')}.csv", index=False, encoding='utf-8-sig')

        # 6. அனைத்தையும் ஜிப் (Zip) செய்தல்
        shutil.make_archive('Final_Reports_Mohanraj', 'zip', output_folder)

        print("\n--- அனைத்தும் வெற்றிகரமாக முடிந்தது! ---")
        print("1. முழு மாஸ்டர் கோப்பு: Master_Seating_Plan_2026.csv")
        print("2. அனைத்து ஹால் பட்டியல்கள் (ZIP): Final_Reports_Mohanraj.zip")

        # விடுபட்ட டிபார்ட்மென்ட் செக்
        missing = master[master['EXAM DATE'].isna()]['Department'].unique()
        if len(missing) > 0:
            print("\nஎச்சரிக்கை! பின்வரும் டிபார்ட்மென்ட்களுக்குத் தேர்வு விவரங்கள் இணையவில்லை:")
            for m in missing: print(f"- {m}")

    except Exception as e:
        print(f"பிழை: {e}")

# ரன் செய்க
run_final_exam_system()
