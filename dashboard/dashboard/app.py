from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file, session
import pandas as pd
from datetime import datetime
import os
import io

app = Flask(__name__)
app.secret_key = 'cwk_secret_key_here'  # Required for login session

EXCEL_FILE = 'students_data.xlsx'

def get_dashboard_data(start_date=None, end_date=None):
    if not os.path.exists(EXCEL_FILE):
        df_sample = pd.DataFrame({
            'ID': [1, 2, 3],
            'Student_Name': ['Arun Kumar', 'Priya S', 'Kavi Priya'],
            'Course_Enrolled': ['Python', 'Java', 'Python'],
            'Status': ['Active', 'Active', 'Completed'],
            'Admission_Date': [datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d'), '2026-01-10'],
            'Base_Fee_INR': [15000, 20000, 15000],
            'Amount_Paid_INR': [10000, 20000, 15000],
            'Balance_Due_INR': [5000, 0, 0],
            'Certificate_Issued': [0, 1, 1],
            'Study_Material': [1, 1, 1]
        })
        df_sample.to_excel(EXCEL_FILE, index=False)

    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        print("Error reading Excel:", e)
        df = pd.DataFrame()

    if not df.empty and 'Student_Name' in df.columns:
        df = df.dropna(subset=['Student_Name'])
        df = df[df['Student_Name'].astype(str).str.strip() != '']
        if 'ID' not in df.columns:
            df['ID'] = range(1, len(df) + 1)
        df.to_excel(EXCEL_FILE, index=False)

    total_students = len(df)
    status_col = 'Status' if 'Status' in df.columns else 'status'
    active_students = len(df[df[status_col].astype(str).str.strip().str.title() == 'Active']) if status_col in df.columns and total_students > 0 else 0

    date_col = 'Admission_Date' if 'Admission_Date' in df.columns else 'date'

    if start_date and end_date and date_col in df.columns and not df.empty:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        mask = (df[date_col] >= start_dt) & (df[date_col] <= end_dt)
        filtered_df = df.loc[mask]
    else:
        filtered_df = df

    today_str = datetime.now().strftime('%Y-%m-%d')
    today_walkins = 0
    today_admissions = 0
    if date_col in df.columns and not df.empty:
        today_df = df[df[date_col].astype(str).str.startswith(today_str)]
        today_walkins = len(today_df)
        today_admissions = len(today_df)

    current_month = datetime.now().strftime('%Y-%m')
    this_month_join = len(df[df[date_col].astype(str).str.startswith(current_month)]) if date_col in df.columns and not df.empty else 0
    this_year_join = len(df[df[date_col].astype(str).str.startswith(str(datetime.now().year))]) if date_col in df.columns and not df.empty else 0

    paid_col = 'Amount_Paid_INR' if 'Amount_Paid_INR' in df.columns else 'paid'
    due_col = 'Balance_Due_INR' if 'Balance_Due_INR' in df.columns else 'due'
    cert_col = 'Certificate_Issued' if 'Certificate_Issued' in df.columns else 'certificate'
    mat_col = 'Study_Material' if 'Study_Material' in df.columns else 'study_material'

    amount_paid = int(filtered_df[paid_col].sum()) if paid_col in filtered_df.columns and not filtered_df.empty else 0
    balance_due = int(filtered_df[due_col].sum()) if due_col in filtered_df.columns and not filtered_df.empty else 0
    pending_revenue = balance_due

    certificate_issued = int(filtered_df[cert_col].sum()) if cert_col in filtered_df.columns and not filtered_df.empty else 0
    study_material_distributed = int(filtered_df[mat_col].sum()) if mat_col in filtered_df.columns and not filtered_df.empty else 0

    course_col = 'Course_Enrolled' if 'Course_Enrolled' in df.columns else 'course'
    if course_col in filtered_df.columns and not filtered_df.empty:
        filtered_df[course_col] = filtered_df[course_col].astype(str).str.strip().str.title()
        course_counts = filtered_df[course_col].value_counts()
        chart_labels = course_counts.index.tolist()
        chart_data = course_counts.values.tolist()
    else:
        chart_labels = []
        chart_data = []

    students_list = []
    if not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            students_list.append({
                "id": int(row['ID']) if 'ID' in row and pd.notnull(row['ID']) else 1,
                "name": str(row.get('Student_Name', row.get('name', ''))),
                "course": str(row.get('Course_Enrolled', row.get('course', ''))),
                "status": str(row.get('Status', row.get('status', 'Active'))),
                "date": str(row.get(date_col, '')).split('T')[0],
                "base_fee": int(row.get('Base_Fee_INR', row.get('base_fee', 0))),
                "paid": int(row.get(paid_col, 0)),
                "due": int(row.get(due_col, 0)),
                "certificate": int(row.get(cert_col, 0))
            })

    return {
        "total_students": total_students,
        "active_students": active_students,
        "today_walkins": today_walkins,
        "today_admissions": today_admissions,
        "this_month_join": this_month_join,
        "prev_month_join": 0,
        "this_year_join": this_year_join,
        "certificate_issued": certificate_issued,
        "pending_revenue": pending_revenue,
        "study_material_distributed": study_material_distributed,
        "amount_paid": amount_paid,
        "balance_due": balance_due,
        "students_list": students_list,
        "chart_labels": chart_labels,
        "chart_data": chart_data
    }

# --- AUTHENTICATION ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Default Admin Credentials (Neenga engalukkuethapadi change pannikonga)
        if username == 'admin' and password == 'cwk123':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid Username or Password!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/api/dashboard-data')
def dashboard_data():
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data = get_dashboard_data(start_date, end_date)
    return jsonify(data)

@app.route('/add-student', methods=['POST'])
def add_student():
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "Unauthorized"})
    try:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
        else:
            df = pd.DataFrame(columns=['ID', 'Student_Name', 'Course_Enrolled', 'Base_Fee_INR', 'Amount_Paid_INR', 'Balance_Due_INR', 'Admission_Date', 'Status', 'Certificate_Issued', 'Study_Material'])

        new_id = int(df['ID'].max() + 1) if not df.empty and 'ID' in df.columns else 1
        
        name = request.form.get('name')
        course = request.form.get('course', '').strip().title()
        status = request.form.get('status', 'Active')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        base_fee = int(request.form.get('base_fee', 0))
        paid = int(request.form.get('paid', 0))
        due = base_fee - paid
        certificate = int(request.form.get('certificate', 0))
        study_material = int(request.form.get('study_material', 1))

        new_row = {
            'ID': new_id,
            'Student_Name': name,
            'Course_Enrolled': course,
            'Status': status,
            'Admission_Date': date,
            'Base_Fee_INR': base_fee,
            'Amount_Paid_INR': paid,
            'Balance_Due_INR': due,
            'Certificate_Issued': certificate,
            'Study_Material': study_material
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        return jsonify({"success": True, "message": "Student added successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/update-student/<int:student_id>', methods=['POST'])
def update_student(student_id):
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "Unauthorized"})
    try:
        if not os.path.exists(EXCEL_FILE):
            return jsonify({"success": False, "message": "Excel file not found!"})
        
        df = pd.read_excel(EXCEL_FILE)
        id_col = 'ID' if 'ID' in df.columns else df.columns[0]

        if student_id not in df[id_col].values:
            return jsonify({"success": False, "message": "Student ID not found!"})

        name = request.form.get('name')
        course = request.form.get('course', '').strip().title()
        status = request.form.get('status', 'Active')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        base_fee = int(request.form.get('base_fee', 0))
        paid = int(request.form.get('paid', 0))
        due = base_fee - paid
        certificate = int(request.form.get('certificate', 0))

        df.loc[df[id_col] == student_id, 'Student_Name'] = name
        df.loc[df[id_col] == student_id, 'Course_Enrolled'] = course
        df.loc[df[id_col] == student_id, 'Status'] = status
        df.loc[df[id_col] == student_id, 'Admission_Date'] = date
        df.loc[df[id_col] == student_id, 'Base_Fee_INR'] = base_fee
        df.loc[df[id_col] == student_id, 'Amount_Paid_INR'] = paid
        df.loc[df[id_col] == student_id, 'Balance_Due_INR'] = due
        df.loc[df[id_col] == student_id, 'Certificate_Issued'] = certificate

        df.to_excel(EXCEL_FILE, index=False)
        return jsonify({"success": True, "message": "Student updated successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/delete-student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    if not session.get('logged_in'):
        return jsonify({"success": False, "message": "Unauthorized"})
    try:
        df = pd.read_excel(EXCEL_FILE)
        id_col = 'ID' if 'ID' in df.columns else df.columns[-1]
        if student_id in df[id_col].values:
            df = df[df[id_col] != student_id]
            df.to_excel(EXCEL_FILE, index=False)
            return jsonify({"success": True, "message": "Student deleted successfully!"})
        return jsonify({"success": False, "message": "Student ID not found."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/download-report')
def download_report():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    df = pd.read_excel(EXCEL_FILE)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reports')
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='CWK_Reports.xlsx')

if __name__ == '__main__':
    app.run(debug=True)
