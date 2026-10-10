from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import mysql.connector

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

app.secret_key = "ai-hospital-development-key"


# =========================================================
# MYSQL CONNECTION
# =========================================================

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="amreen",
        database="ai_hospital_db"
    )
# =========================================================
# INNOVATION USAGE LOGGER
# =========================================================

def log_innovation_usage(innovation_id, action):
    connection = None
    cursor = None

    try:
        user_id = session.get("user_id")

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO innovation_usage
            (innovation_id, user_id, action)
            VALUES (%s, %s, %s)
            """,
            (
                innovation_id,
                user_id,
                action
            )
        )

        connection.commit()

    except mysql.connector.Error as e:

        print(
            "Innovation usage logging error:",
            e
        )

        if connection:
            connection.rollback()

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

# =========================================================
# ADMIN LOGIN REQUIRED
# =========================================================

def admin_required():

    if "user_id" not in session:
        return False

    if session.get("role") != "admin":
        return False

    return True


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


# =========================================================
# SERVICES
# =========================================================

@app.route("/services")
def services():

    return render_template(
        "services.html"
    )

@app.route('/patient-management', methods=['GET', 'POST'])
def patient_management():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':

        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        blood_group = request.form.get('blood_group')
        address = request.form.get('address')

        cursor.execute("""
            INSERT INTO patients
            (
                user_id,
                name,
                age,
                gender,
                phone,
                address,
                blood_group
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            name,
            age,
            gender,
            phone,
            address,
            blood_group
        ))

        conn.commit()

    cursor.execute("""
        SELECT *
        FROM patients
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (session['user_id'],))

    patients = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'patient_management.html',
        patients=patients
    )
# =========================================================
# AI INNOVATIONS
# =========================================================
@app.route("/innovations")
def innovations():

    return render_template(
        "innovations.html"
    )
# =====================================================
# AI SYMPTOM CHECKER - DEMO
# =====================================================

@app.route("/ai-symptom-checker", methods=["GET", "POST"])
def ai_symptom_checker():

    result = None

    if request.method == "POST":

        symptoms = request.form.getlist("symptoms")

        if not symptoms:

            flash(
                "Please select at least one symptom.",
                "warning"
            )

            return redirect(url_for("ai_symptom_checker"))

        symptoms = set(symptoms)

        # ---------------------------------------------
        # DEMO AI ANALYSIS
        # ---------------------------------------------

        if (
            "chest_pain" in symptoms
            and "shortness_of_breath" in symptoms
        ):

            result = {
                "condition": "Possible cardiovascular or respiratory concern",
                "risk": "High",
                "guidance": "Seek urgent medical attention, especially if symptoms are severe or sudden."
            }

        elif (
            "fever" in symptoms
            and "cough" in symptoms
            and "sore_throat" in symptoms
        ):

            result = {
                "condition": "Possible respiratory infection",
                "risk": "Moderate",
                "guidance": "Rest, stay hydrated and consult a healthcare professional."
            }

        elif (
            "fever" in symptoms
            and "headache" in symptoms
            and "body_ache" in symptoms
        ):

            result = {
                "condition": "Possible viral illness",
                "risk": "Moderate",
                "guidance": "Stay hydrated, rest and consider consulting a healthcare professional."
            }

        elif (
            "stomach_pain" in symptoms
            and "nausea" in symptoms
            and "vomiting" in symptoms
        ):

            result = {
                "condition": "Possible digestive illness",
                "risk": "Moderate",
                "guidance": "Maintain hydration and seek medical advice if symptoms persist."
            }

        elif (
            "headache" in symptoms
            and "dizziness" in symptoms
        ):

            result = {
                "condition": "Possible headache or dehydration-related condition",
                "risk": "Low to Moderate",
                "guidance": "Rest, drink adequate fluids and consult a doctor if symptoms continue."
            }

        elif (
            "cough" in symptoms
            and "shortness_of_breath" in symptoms
        ):

            result = {
                "condition": "Possible respiratory condition",
                "risk": "Moderate",
                "guidance": "Monitor breathing difficulty and consult a healthcare professional."
            }

        elif (
            "frequent_urination" in symptoms
            and "excessive_thirst" in symptoms
        ):

            result = {
                "condition": "Possible metabolic or urinary-related condition",
                "risk": "Moderate",
                "guidance": "Consult a healthcare professional for proper evaluation."
            }

        elif (
            "skin_rash" in symptoms
            and "itching" in symptoms
        ):

            result = {
                "condition": "Possible allergic or skin-related condition",
                "risk": "Low",
                "guidance": "Avoid possible triggers and consult a doctor if the rash worsens."
            }

        elif "fatigue" in symptoms:

            result = {
                "condition": "Possible general fatigue-related condition",
                "risk": "Low",
                "guidance": "Rest adequately, maintain a healthy routine and consult a doctor if persistent."
            }

        else:

            result = {
                "condition": "General health concern",
                "risk": "Low",
                "guidance": "Monitor your symptoms and consult a healthcare professional for proper evaluation."
            }

    return render_template(
        "ai_symptom_checker.html",
        result=result
    )
# =========================================================
# AI HEALTHCARE ASSISTANT
# =========================================================

@app.route("/ai-healthcare-assistant", methods=["GET", "POST"])
def ai_healthcare_assistant():

    answer = None
    question = ""

    if request.method == "POST":

        question = request.form.get(
            "question",
            ""
        ).strip()

        q = question.lower()

        # =====================================================
        # EMPTY QUESTION
        # =====================================================

        if not question:

            flash(
                "Please enter your question.",
                "warning"
            )

        # =====================================================
        # HOSPITAL TIMINGS
        # =====================================================

        elif (
            "timing" in q
            or "timings" in q
            or "opening hours" in q
            or "working hours" in q
        ):

            answer = (
                "Please contact the hospital reception for "
                "the latest department and doctor timings."
            )

        # =====================================================
        # CANCEL APPOINTMENT
        # =====================================================

        elif (
            "cancel appointment" in q
            or "cancel my appointment" in q
            or "appointment cancel" in q
        ):

            answer = (
                "You can open My Appointments and cancel an "
                "eligible appointment from there."
            )

        # =====================================================
        # MY APPOINTMENT / STATUS
        # =====================================================

        elif (
            "my appointment" in q
            or "my appointments" in q
            or "appointment status" in q
            or "appointment pending" in q
            or "appointment approved" in q
        ):

            answer = (
                "You can open My Appointments to check your "
                "appointment history and current status."
            )

        # =====================================================
        # BOOK APPOINTMENT
        # =====================================================

        elif (
            "appointment" in q
            or "booking" in q
            or "book appointment" in q
            or "schedule" in q
        ):

            answer = (
                "You can book an appointment with our doctors "
                "from the Appointment page."
            )

        # =====================================================
        # DOCTORS
        # =====================================================

        elif (
            "doctor" in q
            or "doctors" in q
            or "specialist" in q
            or "specialization" in q
            or "find doctor" in q
        ):

            answer = (
                "You can visit the Doctors page to view "
                "available doctors and their specialties."
            )

        # =====================================================
        # HOSPITAL SERVICES
        # =====================================================

        elif (
            "service" in q
            or "services" in q
            or "facility" in q
            or "facilities" in q
        ):

            answer = (
                "Our hospital provides doctor consultations, "
                "appointment management, patient support and "
                "AI-powered healthcare features."
            )

        # =====================================================
        # SYMPTOM CHECKER
        # =====================================================

        elif (
            "symptom" in q
            or "symptoms" in q
            or "symptom checker" in q
        ):

            answer = (
                "You can use our AI Symptom Checker for "
                "preliminary guidance based on selected symptoms. "
                "It does not replace professional medical advice."
            )

        # =====================================================
        # MEDICINE
        # =====================================================

        elif (
            "medicine" in q
            or "medicines" in q
            or "tablet" in q
            or "tablets" in q
        ):

            answer = (
                "Please take medicines only as prescribed or "
                "advised by a qualified healthcare professional."
            )

        # =====================================================
        # EMERGENCY
        # =====================================================

        elif (
            "emergency" in q
            or "urgent" in q
            or "ambulance" in q
        ):

            answer = (
                "If you think you have a medical emergency, "
                "please seek immediate medical help or visit "
                "the nearest emergency department."
            )

        # =====================================================
        # CONTACT
        # =====================================================

        elif (
            "contact" in q
            or "email" in q
            or "phone number" in q
            or "contact hospital" in q
        ):

            answer = (
                "You can visit the Contact page to find the "
                "hospital's available contact information."
            )

        # =====================================================
        # AI FEATURES
        # =====================================================

        elif (
            "ai" in q
            or "artificial intelligence" in q
            or "ai features" in q
            or "innovations" in q
        ):

            answer = (
                "AI Hospital includes AI-powered healthcare "
                "features such as the AI Healthcare Assistant "
                "and AI Symptom Checker."
            )

        # =====================================================
        # HOSPITAL INFORMATION
        # =====================================================

        elif (
            "hospital" in q
            or "about hospital" in q
            or "ai hospital" in q
        ):

            answer = (
                "AI Hospital provides doctor consultations, "
                "appointment management, patient support and "
                "AI-powered healthcare features."
            )

        # =====================================================
        # GREETING
        # =====================================================

        elif (
            "hello" in q
            or "hi" in q
            or "hey" in q
            or "help" in q
        ):

            answer = (
                "Hello! 👋 I can help you with appointments, "
                "doctors, hospital services, symptoms, medicines "
                "and AI Hospital features."
            )

        # =====================================================
        # DEFAULT RESPONSE
        # =====================================================

        else:

            answer = (
                "I can help with general questions about "
                "appointments, doctors, hospital services, "
                "medicines, symptoms, appointment status and "
                "AI Hospital features."
            )

    return render_template(
        "ai_healthcare_assistant.html",
        answer=answer,
        question=question
    )

        
       


      
# =========================================================
# DOCTORS PAGE
# =========================================================

@app.route("/doctors")
def doctors():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                name,
                specialization,
                department,
                phone,
                email,
                experience,
                availability
            FROM doctors
            ORDER BY id DESC
            """
        )

        doctors_list = cursor.fetchall()

        return render_template(
            "doctors.html",
            doctors=doctors_list
        )

    except mysql.connector.Error as e:

        print(
            "Doctors database error:",
            e
        )

        flash(
            "Unable to load doctors.",
            "danger"
        )

        return render_template(
            "doctors.html",
            doctors=[]
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# APPOINTMENT DOCTOR AVAILABILITY
# =========================================================

@app.route("/appointment/doctor-availability")
def appointment_doctor_availability():

    department = request.args.get("department", "").strip()
    appointment_date = request.args.get("appointment_date", "").strip()
    appointment_time = request.args.get("appointment_time", "").strip()

    if not department or not appointment_date or not appointment_time:
        return jsonify({"booked_doctor_ids": []})

    from datetime import datetime

    try:
        appointment_time = datetime.strptime(
            appointment_time,
            "%I:%M %p"
        ).strftime("%H:%M:%S")
    except ValueError:
        return jsonify({"booked_doctor_ids": []})

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT DISTINCT doctor_id
            FROM appointments
            WHERE appointment_date = %s
              AND appointment_time = %s
              AND status != 'Cancelled'
              AND doctor_id IN (
                  SELECT id
                  FROM doctors
                  WHERE department = %s
              )
            """,
            (
                appointment_date,
                appointment_time,
                department
            )
        )

        rows = cursor.fetchall()

        return jsonify({
            "booked_doctor_ids": [int(row["doctor_id"]) for row in rows]
        })

    except mysql.connector.Error as e:
        print("Doctor availability error:", e)
        return jsonify({"booked_doctor_ids": []}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# =========================================================
# APPOINTMENT
# =========================================================
@app.route("/doctor-availability")
def doctor_availability():

    appointment_date = request.args.get("date")
    appointment_time = request.args.get("time")

    if not appointment_date or not appointment_time:
        return jsonify({"booked_doctors": []})

    try:
        from datetime import datetime

        appointment_time = datetime.strptime(
            appointment_time,
            "%I:%M %p"
        ).strftime("%H:%M:%S")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT doctor_id
            FROM appointments
            WHERE appointment_date = %s
              AND appointment_time = %s
              AND status != 'Cancelled'
            """,
            (
                appointment_date,
                appointment_time
            )
        )

        rows = cursor.fetchall()

        booked_doctors = [
            row["doctor_id"]
            for row in rows
        ]

        return jsonify({
            "booked_doctors": booked_doctors
        })

    except mysql.connector.Error as e:

        print("Doctor availability error:", e)

        return jsonify({
            "booked_doctors": []
        })

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

@app.route(
    "/appointment",
    methods=["GET", "POST"]
)
def appointment():

    print(">>> APPOINTMENT ROUTE HIT:", request.method)

    connection = None
    cursor = None

    # =====================================================
    # GET REQUEST
    # =====================================================

    if request.method == "GET":

        try:

            connection = get_db_connection()

            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    specialization,
                    department,
                    availability,
                    consultation_fee
                FROM doctors
                ORDER BY name ASC
                """
            )

            doctors_list = cursor.fetchall()

            return render_template(
                "appointment.html",
                doctors=doctors_list
            )

        except mysql.connector.Error as e:

            print(
                "Appointment doctors error:",
                e
            )

            flash(
                "Unable to load doctors.",
                "danger"
            )

            return render_template(
                "appointment.html",
                doctors=[]
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    # =====================================================
    # POST REQUEST
    # =====================================================

    patient_name = request.form.get(
        "patient_name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    department = request.form.get(
        "department",
        ""
    ).strip()

    doctor_id = request.form.get(
        "doctor",
        ""
    ).strip()
    charges = 0
    appointment_date = request.form.get(
        "appointment_date",
        ""
    ).strip()
    
    appointment_time = request.form.get(
        "appointment_time",
        ""
    ).strip()
        # Convert 12-hour time to MySQL TIME format

    from datetime import datetime

    if appointment_time:

        try:

            appointment_time = datetime.strptime(
                appointment_time,
                "%I:%M %p"
            ).strftime(
                "%H:%M:%S"
            )

        except ValueError:

            flash(
                "Invalid appointment time.",
                "danger"
            )

            return redirect(
                url_for("appointment")
            )
    reason = request.form.get(
    "reason",
    ""
    ).strip()    

    # =====================================================
    # BASIC VALIDATION
    # =====================================================

    if not all([
        patient_name,
        email,
        phone,
        department,
        doctor_id,
        appointment_date,
        appointment_time,
        reason
    ]):

        flash(
            "Please fill all appointment fields.",
            "danger"
        )

        return redirect(
            url_for("appointment")
        )


    # =====================================================
    # DATABASE OPERATIONS
    # =====================================================

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        # =================================================
        # CHECK DOCTOR
        # =================================================

        cursor.execute(
            """
            SELECT
                id,
                name,
                department,
                consultation_fee
            FROM doctors
            WHERE id = %s
            """,
            (doctor_id,)
        )

        doctor = cursor.fetchone()


        if not doctor:

            flash(
                "Selected doctor was not found.",
                "danger"
            )

            return redirect(
                url_for("appointment")
            )
        charges = doctor["consultation_fee"]


        # =================================================
        # CHECK DEPARTMENT
        # =================================================

        if doctor["department"] != department:

            flash(
                "Selected doctor does not belong to this department.",
                "danger"
            )

            return redirect(
                url_for("appointment")
            )


        # =================================================
        # CHECK EXISTING APPOINTMENT
        # =================================================

        cursor.execute(
            """
            SELECT
                id
            FROM appointments
            WHERE doctor_id = %s
              AND appointment_date = %s
              AND appointment_time = %s
              AND status != 'Cancelled'
            """,
            (
                doctor_id,
                appointment_date,
                appointment_time
            )
        )

        existing_appointment = cursor.fetchone()


        if existing_appointment:

            # Find other doctors from the same department
            # who are available at the selected date and time.
            cursor.execute(
                """
                SELECT
                    d.id,
                    d.name,
                    d.consultation_fee
                FROM doctors d
                WHERE d.department = %s
                  AND d.id != %s
                  AND d.availability = 'Available'
                  AND NOT EXISTS (
                      SELECT 1
                      FROM appointments a
                      WHERE a.doctor_id = d.id
                        AND a.appointment_date = %s
                        AND a.appointment_time = %s
                        AND a.status != 'Cancelled'
                  )
                ORDER BY d.name ASC
                """,
                (
                    department,
                    doctor_id,
                    appointment_date,
                    appointment_time
                )
            )

            alternative_doctors = cursor.fetchall()

            if alternative_doctors:

                doctor_names = ", ".join(
                    doctor["name"]
                    for doctor in alternative_doctors
                )

                flash(
                    "The selected doctor is already booked for this date and time. "
                    "Please choose another available doctor from the same department: "
                    + doctor_names,
                    "warning"
                )

            else:

                flash(
                    "The selected doctor is already booked for this date and time, "
                    "and no other doctor from this department is available at that time.",
                    "warning"
                )

            return redirect(
                url_for("appointment")
            )


        # =================================================
        # FIND EXISTING PATIENT
        # =================================================
        user_id = session.get("user_id")
        cursor.execute(
        """
            SELECT
                id
            FROM patients
            WHERE user_id = %s
              AND phone = %s
              LIMIT 1
            """,
           (
                user_id,
                phone
            )
        )

        patient = cursor.fetchone()


        # =================================================
        # CREATE PATIENT IF NOT FOUND
        # =================================================

        if patient:

            patient_id = patient["id"]

        else:

            cursor.execute(
                """
                INSERT INTO patients
                (
                    user_id,
                    name,
                    phone
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    user_id,
                    patient_name,
                    phone
                )
            )

            patient_id = cursor.lastrowid


        # =================================================
        # CREATE APPOINTMENT
        # =================================================

        cursor.execute(
            """
            INSERT INTO appointments
            (
                patient_id,
                doctor_id,
                appointment_date,
                appointment_time,
                charges,
                payment_status,
                reason,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                patient_id,
                doctor_id,
                appointment_date,
                appointment_time,
                charges,
                "Pending",
                reason,
                "Pending"
            )
        )


        # =================================================
        # COMMIT
        # =================================================

        connection.commit()


        flash(
            "Appointment booked successfully! Your request is pending confirmation.",
            "success"
        )


        return redirect(
            url_for("appointment")
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.Error as e:

        print(
            "Appointment booking error:",
            e
        )

        if connection:
            connection.rollback()

        flash(
            "Unable to book appointment. Please try again.",
            "danger"
        )

        return redirect(
            url_for("appointment")
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
# =========================================================
# MY APPOINTMENTS
# =========================================================

@app.route("/my-appointments")
def my_appointments():

    # Patient must be logged in
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # Get appointments belonging to logged-in patient
        cursor.execute(
            """
            SELECT
                a.id,
                a.appointment_date,
                a.appointment_time,
                a.charges,
                a.payment_status,
                a.reason,
                a.status,
                d.name AS doctor_name,
                d.specialization,
                d.department
            FROM appointments a
            INNER JOIN patients p
                ON a.patient_id = p.id
            INNER JOIN doctors d
                ON a.doctor_id = d.id
            WHERE p.user_id = %s
            ORDER BY a.appointment_date DESC, a.id DESC
            """,
            (session["user_id"],)
        )

        appointments = cursor.fetchall()

        return render_template(
            "my_appointments.html",
            appointments=appointments
        )

    except mysql.connector.Error as e:

        print(
            "My appointments error:",
            e
        )

        flash(
            "Unable to load your appointments.",
            "danger"
        )

        return render_template(
            "my_appointments.html",
            appointments=[]
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
# =========================================================
# DEMO PAYMENT
# =========================================================

@app.route(
    "/demo-payment/<int:appointment_id>",
    methods=["GET", "POST"]
)
def demo_payment(appointment_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                a.id,
                a.charges,
                a.payment_status,
                d.name AS doctor_name,
                d.specialization
            FROM appointments a
            INNER JOIN patients p
                ON a.patient_id = p.id
            INNER JOIN doctors d
                ON a.doctor_id = d.id
            WHERE a.id = %s
              AND p.user_id = %s
            """,
            (
                appointment_id,
                session["user_id"]
            )
        )

        appointment = cursor.fetchone()

        if not appointment:

            flash(
                "Appointment not found.",
                "danger"
            )

            return redirect(
                url_for("my_appointments")
            )

        if request.method == "POST":

            cursor.execute(
                """
                UPDATE appointments
                SET payment_status = 'Paid'
                WHERE id = %s
                """,
                (appointment_id,)
            )

            connection.commit()

            flash(
                "Demo payment successful! Your appointment payment is confirmed.",
                "success"
            )

            return redirect(
                url_for("my_appointments")
            )

        return render_template(
            "demo_payment.html",
            appointment=appointment
        )

    except mysql.connector.Error as e:

        print(
            "Demo payment error:",
            e
        )

        if connection:
            connection.rollback()

        flash(
            "Unable to process demo payment.",
            "danger"
        )

        return redirect(
            url_for("my_appointments")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
# =========================================================
# CANCEL PATIENT APPOINTMENT
# =========================================================

@app.route(
    "/cancel-appointment/<int:appointment_id>",
    methods=["POST"]
)
def cancel_appointment(appointment_id):

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # Make sure this appointment belongs
        # to the currently logged-in patient
        cursor.execute(
            """
            SELECT
                a.id,
                a.status
            FROM appointments a
            INNER JOIN patients p
                ON a.patient_id = p.id
            WHERE a.id = %s
              AND p.user_id = %s
            LIMIT 1
            """,
            (
                appointment_id,
                session["user_id"]
            )
        )

        appointment = cursor.fetchone()

        if not appointment:

            flash(
                "Appointment not found.",
                "danger"
            )

            return redirect(
                url_for("my_appointments")
            )

        # Only Pending or Approved appointments
        # can be cancelled by the patient
        if appointment["status"] not in [
            "Pending",
            "Approved"
        ]:

            flash(
                "This appointment cannot be cancelled.",
                "warning"
            )

            return redirect(
                url_for("my_appointments")
            )

        cursor.execute(
            """
            UPDATE appointments
            SET status = 'Cancelled'
            WHERE id = %s
            """,
            (appointment_id,)
        )

        connection.commit()

        flash(
            "Appointment cancelled successfully.",
            "success"
        )

    except mysql.connector.Error as e:

        print(
            "Cancel appointment error:",
            e
        )

        if connection:
            connection.rollback()

        flash(
            "Unable to cancel appointment. Please try again.",
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(
        url_for("my_appointments")
    )
# =========================================================
# SMART QUEUE MANAGEMENT - APPOINTMENT BASED
# =========================================================

@app.route("/smart-queue")
def smart_queue():

    if "user_id" not in session:
        flash(
            "Please login to check your queue.",
            "warning"
        )
        return redirect(url_for("login"))

    connection = None
    cursor = None
    queue_data = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)
        # -------------------------------------------------
        # TRACK AI SMART QUEUE USAGE
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM innovations
            WHERE title = %s
            LIMIT 1
            """,
            ("ai smart queue management",)
           )

        innovation = cursor.fetchone()

        if innovation:

            cursor.execute(
                """
                INSERT INTO innovation_usage
                (
                    innovation_id,
                    user_id,
                    action
                )
                VALUES (%s, %s, %s)
                """,
                (
                    innovation["id"],
                    session["user_id"],
                    "viewed"
                )
            )

            connection.commit()

        # -------------------------------------------------
        # FIND USER'S APPROVED APPOINTMENT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                a.id AS appointment_id,
                a.patient_id,
                a.doctor_id,
                a.appointment_date,
                a.appointment_time,
                a.status,

                p.name AS patient_name,

                d.name AS doctor_name,
                d.specialization,
                d.department

            FROM appointments a

            INNER JOIN patients p
                ON a.patient_id = p.id

            LEFT JOIN doctors d
                ON a.doctor_id = d.id

            WHERE p.user_id = %s

            AND a.status = 'Approved'

            ORDER BY
                a.appointment_date ASC,
                a.appointment_time ASC,
                a.id ASC

            LIMIT 1
            """,
            (session["user_id"],)
        )

        appointment = cursor.fetchone()

        # -------------------------------------------------
        # NO APPROVED APPOINTMENT
        # -------------------------------------------------

        if not appointment:

            flash(
                "You do not have any approved appointment for the queue.",
                "warning"
            )

            return render_template(
                "smart_queue.html",
                queue_data=None
            )

        # -------------------------------------------------
        # CHECK DOCTOR
        # -------------------------------------------------

        if not appointment["doctor_id"]:

            flash(
                "Doctor is not assigned to your appointment.",
                "warning"
            )

            return render_template(
                "smart_queue.html",
                queue_data=None
            )

        # -------------------------------------------------
        # COUNT PATIENTS AHEAD
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                COUNT(*) AS patients_ahead

            FROM appointments

            WHERE doctor_id = %s

            AND appointment_date = %s

            AND appointment_time < %s

            AND status = 'Approved'
            """,
            (
                appointment["doctor_id"],
                appointment["appointment_date"],
                appointment["appointment_time"]
            )
        )

        result = cursor.fetchone()

        patients_ahead = int(
            result["patients_ahead"] or 0
        )

        # -------------------------------------------------
        # TOKEN NUMBER
        # -------------------------------------------------

        token_number = patients_ahead + 1

        # -------------------------------------------------
        # ESTIMATED WAITING TIME
        # 15 MINUTES PER PATIENT
        # -------------------------------------------------

        estimated_wait = patients_ahead * 15

        if estimated_wait == 0:

            waiting_text = "You are next"

        elif estimated_wait < 60:

            waiting_text = (
                f"Approximately "
                f"{estimated_wait} minutes"
            )

        else:

            hours = estimated_wait // 60
            minutes = estimated_wait % 60

            if minutes:

                waiting_text = (
                    f"Approximately "
                    f"{hours} hour(s) "
                    f"{minutes} minutes"
                )

            else:

                waiting_text = (
                    f"Approximately "
                    f"{hours} hour(s)"
                )

        # -------------------------------------------------
        # QUEUE DATA
        # -------------------------------------------------

        queue_data = {

            "appointment_id":
                appointment["appointment_id"],

            "patient_name":
                appointment["patient_name"],

            "doctor_name":
                appointment["doctor_name"],

            "specialization":
                appointment["specialization"],

            "department":
                appointment["department"],

            "date":
                appointment["appointment_date"],

            "time":
                appointment["appointment_time"],

            "status":
                appointment["status"],

            "patients_ahead":
                patients_ahead,

            "token":
                token_number,

            "waiting":
                waiting_text
        }

    except mysql.connector.Error as e:

        print(
            "Smart Queue database error:",
            e
        )

        flash(
            "Unable to load Smart Queue information.",
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return render_template(
        "smart_queue.html",
        queue_data=queue_data
   )

# =========================================================
# MEDICINE REMINDER
# =========================================================

@app.route("/medicine_reminder", methods=["GET", "POST"])
def medicine_reminder():

    if "user_id" not in session:
        flash(
            "Please login to manage your medicine reminders.",
            "warning"
        )
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # ADD MEDICINE REMINDER
        # -------------------------------------------------

        if request.method == "POST":

            medicine_name = request.form.get(
                "medicine_name",
                ""
            ).strip()

            dosage = request.form.get(
                "dosage",
                ""
            ).strip()

            reminder_time = request.form.get(
                "reminder_time",
                ""
            ).strip()

            start_date = request.form.get(
                "start_date",
                ""
            ).strip()

            end_date = request.form.get(
                "end_date",
                ""
            ).strip()

            if not all([
                medicine_name,
                reminder_time,
                start_date,
                end_date
            ]):

                flash(
                    "Please fill all required fields.",
                    "warning"
                )

            elif end_date < start_date:

                flash(
                    "End date cannot be before start date.",
                    "warning"
                )

            else:

                cursor.execute(
                    """
                    INSERT INTO medicine_reminders
                    (
                        user_id,
                        medicine_name,
                        dosage,
                        reminder_time,
                        start_date,
                        end_date,
                        status
                    )
                    VALUES
                    (%s, %s, %s, %s, %s, %s, 'Active')
                    """,
                    (
                        session["user_id"],
                        medicine_name,
                        dosage,
                        reminder_time,
                        start_date,
                        end_date
                    )
                )

                connection.commit()

                flash(
                    "Medicine reminder added successfully.",
                    "success"
                )

        # -------------------------------------------------
        # LOAD USER'S REMINDERS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                medicine_name,
                dosage,
                reminder_time,
                start_date,
                end_date,
                status
            FROM medicine_reminders
            WHERE user_id = %s
            ORDER BY
                reminder_time ASC,
                start_date ASC
            """,
            (session["user_id"],)
        )

        reminders = cursor.fetchall()

    except mysql.connector.Error as e:

        print(
            "Medicine Reminder database error:",
            e
        )

        flash(
            "Unable to load medicine reminders.",
            "danger"
        )

        reminders = []

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return render_template(
        "medicine_reminder.html",
        reminders=reminders
    )
@app.route("/delete-medicine/<int:reminder_id>", methods=["POST"])
def delete_medicine(reminder_id):

    if "user_id" not in session:
        flash(
            "Please login to manage your medicine reminders.",
            "warning"
        )
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM medicine_reminders
            WHERE id = %s
            AND user_id = %s
            """,
            (
                reminder_id,
                session["user_id"]
            )
        )

        connection.commit()

        flash(
            "Medicine reminder deleted successfully.",
            "success"
        )

    except mysql.connector.Error as e:

        print("Delete medicine reminder error:", e)

        flash(
            "Unable to delete medicine reminder.",
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(url_for("medicine_reminder"))
# =========================================================
# EDIT MEDICINE REMINDER
# =========================================================

@app.route("/edit-medicine/<int:reminder_id>", methods=["GET", "POST"])
def edit_medicine(reminder_id):

    if "user_id" not in session:
        flash(
            "Please login to manage your medicine reminders.",
            "warning"
        )
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # UPDATE MEDICINE REMINDER
        # -------------------------------------------------

        if request.method == "POST":

            medicine_name = request.form.get(
                "medicine_name",
                ""
            ).strip()

            dosage = request.form.get(
                "dosage",
                ""
            ).strip()

            reminder_time = request.form.get(
                "reminder_time",
                ""
            ).strip()

            start_date = request.form.get(
                "start_date",
                ""
            ).strip()

            end_date = request.form.get(
                "end_date",
                ""
            ).strip()

            if not all([
                medicine_name,
                reminder_time,
                start_date,
                end_date
            ]):

                flash(
                    "Please fill all required fields.",
                    "warning"
                )

            elif end_date < start_date:

                flash(
                    "End date cannot be before start date.",
                    "warning"
                )

            else:

                cursor.execute(
                    """
                    UPDATE medicine_reminders
                    SET
                        medicine_name = %s,
                        dosage = %s,
                        reminder_time = %s,
                        start_date = %s,
                        end_date = %s
                    WHERE id = %s
                    AND user_id = %s
                    """,
                    (
                        medicine_name,
                        dosage,
                        reminder_time,
                        start_date,
                        end_date,
                        reminder_id,
                        session["user_id"]
                    )
                )

                connection.commit()

                flash(
                    "Medicine reminder updated successfully.",
                    "success"
                )

                return redirect(
                    url_for("medicine_reminder")
                )

        # -------------------------------------------------
        # GET EXISTING REMINDER
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                medicine_name,
                dosage,
                reminder_time,
                start_date,
                end_date,
                status
            FROM medicine_reminders
            WHERE id = %s
            AND user_id = %s
            """,
            (
                reminder_id,
                session["user_id"]
            )
        )

        reminder = cursor.fetchone()

        if not reminder:

            flash(
                "Medicine reminder not found.",
                "danger"
            )

            return redirect(
                url_for("medicine_reminder")
            )

    except mysql.connector.Error as e:

        print(
            "Edit medicine reminder error:",
            e
        )

        flash(
            "Unable to edit medicine reminder.",
            "danger"
        )

        return redirect(
            url_for("medicine_reminder")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return render_template(
        "edit_medicine.html",
        reminder=reminder
    )
# =========================================================
# HOSPITAL CROWD PREDICTION
# =========================================================

@app.route("/crowd_prediction", methods=["GET", "POST"])
def crowd_prediction():

    if "user_id" not in session:
        flash(
            "Please login to use Hospital Crowd Prediction.",
            "warning"
        )
        return redirect(url_for("login"))

    connection = None
    cursor = None

    prediction = None
    history = []

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # CREATE CROWD PREDICTION
        # -------------------------------------------------

        if request.method == "POST":

            department = request.form.get(
                "department",
                ""
            ).strip()

            visit_date = request.form.get(
                "visit_date",
                ""
            ).strip()

            visit_time = request.form.get(
                "visit_time",
                ""
            ).strip()

            if not all([
                department,
                visit_date,
                visit_time
            ]):

                flash(
                    "Please fill all required fields.",
                    "warning"
                )

            else:

                # -----------------------------------------
                # CONVERT TIME TO HOUR
                # -----------------------------------------

                hour = int(
                    visit_time.split(":")[0]
                )

                # -----------------------------------------
                # CROWD PREDICTION LOGIC
                # -----------------------------------------

                if 9 <= hour < 12:

                    crowd_level = "High"
                    estimated_wait = "30-45 minutes"

                elif 12 <= hour < 15:

                    crowd_level = "Medium"
                    estimated_wait = "15-30 minutes"

                elif 15 <= hour < 18:

                    crowd_level = "Medium"
                    estimated_wait = "15-30 minutes"

                else:

                    crowd_level = "Low"
                    estimated_wait = "5-15 minutes"

                # -----------------------------------------
                # SAVE PREDICTION
                # -----------------------------------------

                cursor.execute(
                    """
                    INSERT INTO crowd_predictions
                    (
                        user_id,
                        department,
                        visit_date,
                        visit_time,
                        crowd_level,
                        estimated_wait
                    )
                    VALUES
                    (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        session["user_id"],
                        department,
                        visit_date,
                        visit_time,
                        crowd_level,
                        estimated_wait
                    )
                )

                connection.commit()

                prediction = {
                    "department": department,
                    "date": visit_date,
                    "time": visit_time,
                    "crowd": crowd_level,
                    "waiting": estimated_wait
                }

                flash(
                    "Crowd prediction generated successfully.",
                    "success"
                )

        # -------------------------------------------------
        # LOAD USER PREDICTION HISTORY
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                department,
                visit_date,
                visit_time,
                crowd_level,
                estimated_wait,
                created_at
            FROM crowd_predictions
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 10
            """,
            (session["user_id"],)
        )

        history = cursor.fetchall()

    except mysql.connector.Error as e:

        print(
            "Crowd Prediction database error:",
            e
        )

        flash(
            "Unable to generate crowd prediction.",
            "danger"
        )

    except (ValueError, TypeError) as e:

        print(
            "Crowd Prediction input error:",
            e
        )

        flash(
            "Invalid date or time information.",
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return render_template(
        "crowd_prediction.html",
        prediction=prediction,
        history=history
    )
@app.route('/medicine_shortage')
def medicine_shortage():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            id,
            medicine_name,
            current_stock,
            daily_usage,
            reorder_level,
            ROUND(current_stock / NULLIF(daily_usage, 0), 1) AS days_left
        FROM medicine_inventory
        ORDER BY days_left ASC
    """)

    medicines = cursor.fetchall()

    # Shortage status calculation
    for medicine in medicines:
        days_left = float(medicine['days_left'] or 0)

        if days_left <= 3:
            medicine['status'] = 'Critical'
        elif medicine['current_stock'] <= medicine['reorder_level']:
            medicine['status'] = 'Low Stock'
        else:
            medicine['status'] = 'Available'

    cursor.close()
    conn.close()

    return render_template(
        'medicine_shortage.html',
        medicines=medicines
    )
@app.route('/update-medicine-stock/<int:medicine_id>', methods=['POST'])
def update_medicine_stock(medicine_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    new_stock = request.form.get('new_stock')

    if not new_stock or int(new_stock) < 0:
        return redirect(url_for('medicine_shortage'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get current stock
    cursor.execute("""
        SELECT current_stock
        FROM medicine_inventory
        WHERE id = %s
    """, (medicine_id,))

    medicine = cursor.fetchone()

    if medicine:
        old_stock = medicine['current_stock']
        new_stock = int(new_stock)

        # Update stock
        cursor.execute("""
            UPDATE medicine_inventory
            SET current_stock = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (new_stock, medicine_id))

        # Save update history
        cursor.execute("""
            INSERT INTO medicine_stock_updates
            (medicine_id, old_stock, new_stock)
            VALUES (%s, %s, %s)
        """, (medicine_id, old_stock, new_stock))

        conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('medicine_shortage'))
@app.route('/emergency-priority')
def emergency_priority():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM emergency_priority
        ORDER BY priority_score DESC, created_at DESC
    """)

    patients = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'emergency_priority.html',
        patients=patients
    )


@app.route('/calculate-emergency-priority', methods=['POST'])
def calculate_emergency_priority():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    patient_name = request.form.get('patient_name')
    age = int(request.form.get('age') or 0)
    heart_rate = int(request.form.get('heart_rate') or 0)
    oxygen_level = int(request.form.get('oxygen_level') or 0)
    temperature = float(request.form.get('temperature') or 0)
    systolic_bp = int(request.form.get('systolic_bp') or 0)
    symptoms = request.form.get('symptoms', '')

    # Priority score calculation
    score = 0

    if oxygen_level < 90:
        score += 40
    elif oxygen_level < 94:
        score += 25

    if heart_rate > 120 or heart_rate < 50:
        score += 25
    elif heart_rate > 100:
        score += 10

    if systolic_bp < 90:
        score += 25
    elif systolic_bp < 100:
        score += 15

    if temperature >= 103:
        score += 15
    elif temperature >= 101:
        score += 10

    if age >= 65:
        score += 5

    if symptoms.strip():
        score += 5

    # Maximum score = 100
    score = min(score, 100)

    if score >= 70:
        priority_level = 'Critical'
    elif score >= 50:
        priority_level = 'High'
    elif score >= 25:
        priority_level = 'Medium'
    else:
        priority_level = 'Low'

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO emergency_priority
        (
            patient_name,
            age,
            heart_rate,
            oxygen_level,
            temperature,
            systolic_bp,
            symptoms,
            priority_score,
            priority_level
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        patient_name,
        age,
        heart_rate,
        oxygen_level,
        temperature,
        systolic_bp,
        symptoms,
        score,
        priority_level
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('emergency_priority'))
# =========================================================
# CONTACT
# =========================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not subject or not message:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("contact"))

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO contact_messages
                (name, email, phone, subject, message)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (name, email, phone, subject, message)
            )

            connection.commit()

            flash("Message sent successfully.", "success")

        except mysql.connector.Error as e:

            if connection:
                connection.rollback()

            print("Contact error:", e)

            flash("Unable to send message.", "danger")

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

        return redirect(url_for("contact"))

    return render_template("contact.html")
# =========================================================
# ADMIN CONTACT MESSAGES
# =========================================================

@app.route("/admin/contact-messages")
def admin_contact_messages():

    if not admin_required():
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                phone,
                subject,
                message
            FROM contact_messages
            ORDER BY id DESC
            """
        )

        messages = cursor.fetchall()

        return render_template(
            "admin_contact_messages.html",
            messages=messages
        )

    except mysql.connector.Error as e:

        print("Admin contact messages error:", e)

        flash(
            "Unable to load contact messages.",
            "danger"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
# =========================================================
# ADMIN SERVICES MANAGEMENT
# =========================================================


# ---------------------------------------------------------
# VIEW ALL SERVICES
# ---------------------------------------------------------

@app.route("/admin/services")
def admin_services():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                title,
                description,
                icon,
                created_at
            FROM services
            ORDER BY id DESC
            """
        )

        services_list = cursor.fetchall()

    except mysql.connector.Error as e:

        print(
            "Admin services database error:",
            e
        )

        services_list = []

        flash(
            "Unable to load services.",
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


    return render_template(
        "admin_services.html",
        services=services_list
    )


# ---------------------------------------------------------
# ADD SERVICE
# ---------------------------------------------------------

@app.route(
    "/services/add",
    methods=["GET", "POST"]
)
def add_service():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        icon = request.form.get(
            "icon",
            "fa-solid fa-stethoscope"
        ).strip()


        if not title or not description:

            flash(
                "Title and description are required.",
                "danger"
            )

            return render_template(
                "service_form.html",
                service=None
            )


        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO services
                (
                    title,
                    description,
                    icon
                )
                VALUES (%s, %s, %s)
                """,
                (
                    title,
                    description,
                    icon
                )
            )

            connection.commit()

            flash(
                "Service added successfully.",
                "success"
            )


        except mysql.connector.Error as e:

            print(
                "Add service database error:",
                e
            )

            flash(
                "Unable to add service.",
                "danger"
            )


        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()


        return redirect(
            url_for("admin_services")
        )


    return render_template(
        "service_form.html",
        service=None
    )


# ---------------------------------------------------------
# EDIT SERVICE
# ---------------------------------------------------------

@app.route(
    "/services/edit/<int:service_id>",
    methods=["GET", "POST"]
)
def edit_service(service_id):

    connection = None
    cursor = None


    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        icon = request.form.get(
            "icon",
            "fa-solid fa-stethoscope"
        ).strip()


        if not title or not description:

            flash(
                "Title and description are required.",
                "danger"
            )

        else:

            try:

                connection = get_db_connection()

                cursor = connection.cursor()

                cursor.execute(
                    """
                    UPDATE services
                    SET
                        title = %s,
                        description = %s,
                        icon = %s
                    WHERE id = %s
                    """,
                    (
                        title,
                        description,
                        icon,
                        service_id
                    )
                )

                connection.commit()

                flash(
                    "Service updated successfully.",
                    "success"
                )

                return redirect(
                    url_for("admin_services")
                )


            except mysql.connector.Error as e:

                print(
                    "Edit service database error:",
                    e
                )

                flash(
                    "Unable to update service.",
                    "danger"
                )


            finally:

                if cursor:
                    cursor.close()

                if connection:
                    connection.close()


    # LOAD SERVICE FOR EDIT

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                title,
                description,
                icon
            FROM services
            WHERE id = %s
            """,
            (service_id,)
        )

        service = cursor.fetchone()


    except mysql.connector.Error as e:

        print(
            "Load service error:",
            e
        )

        service = None


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


    if not service:

        flash(
            "Service not found.",
            "danger"
        )

        return redirect(
            url_for("admin_services")
        )


    return render_template(
        "service_form.html",
        service=service
    )


# ---------------------------------------------------------
# DELETE SERVICE
# ---------------------------------------------------------

@app.route(
    "/services/delete/<int:service_id>",
    methods=["POST"]
)
def delete_service(service_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM services
            WHERE id = %s
            """,
            (service_id,)
        )

        connection.commit()

        flash(
            "Service deleted successfully.",
            "success"
        )


    except mysql.connector.Error as e:

        print(
            "Delete service database error:",
            e
        )

        flash(
            "Unable to delete service.",
            "danger"
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


    return redirect(
        url_for("admin_services")
    )
# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        # =================================================
        # VALIDATION
        # =================================================

        if not email or not password:

            flash(
                "Please enter email and password.",
                "danger"
            )

            return redirect(
                url_for("login")
            )


        connection = None
        cursor = None


        try:

            connection = get_db_connection()

            cursor = connection.cursor(
                dictionary=True
            )


            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    email,
                    password,
                    role
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            user = cursor.fetchone()


            # =================================================
            # PASSWORD CHECK
            # =================================================

            if user and check_password_hash(
                user["password"],
                password
            ):

                session["user_id"] = user["id"]

                session["user_name"] = user["name"]

                session["user_email"] = user["email"]

                session["role"] = user["role"]


                # =================================================
                # ADMIN
                # =================================================

                if user["role"] == "admin":

                    return redirect(
                        url_for("admin_dashboard")
                    )


                # =================================================
                # NORMAL USER
                # =================================================

                return redirect(
                    url_for("home")
                )


            flash(
                "Invalid email or password.",
                "danger"
            )


        except mysql.connector.Error as e:

            print(
                "Login database error:",
                e
            )

            flash(
                "Database error. Please try again.",
                "danger"
            )


        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()


        return redirect(
            url_for("login")
        )


    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin/dashboard")
def admin_dashboard():

    if not admin_required():

        return redirect(
            url_for("login")
        )


    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        # =================================================
        # TOTAL USERS
        # =================================================

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total
            FROM users
            """
        )

        total_users = cursor.fetchone()["total"]


        # =================================================
        # TOTAL PATIENTS
        # =================================================

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total
            FROM patients
            """
        )

        total_patients = cursor.fetchone()["total"]


        # =================================================
        # TOTAL DOCTORS
        # =================================================

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total
            FROM doctors
            """
        )

        total_doctors = cursor.fetchone()["total"]


        # =================================================
        # TOTAL APPOINTMENTS
        # =================================================

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total
            FROM appointments
            """
        )

        total_appointments = cursor.fetchone()["total"]


        return render_template(
            "admin_dashboard.html",
            total_users=total_users,
            total_patients=total_patients,
            total_doctors=total_doctors,
            total_appointments=total_appointments
        )


    except mysql.connector.Error as e:

        print(
            "Dashboard database error:",
            e
        )

        return render_template(
            "admin_dashboard.html",
            total_users=0,
            total_patients=0,
            total_doctors=0,
            total_appointments=0
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# USER MANAGEMENT
# =========================================================

@app.route("/admin/users")
def admin_users():

    if not admin_required():

        return redirect(
            url_for("login")
        )


    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                role,
                created_at
            FROM users
            ORDER BY id DESC
            """
        )

        users = cursor.fetchall()


        return render_template(
            "users.html",
            users=users
        )


    except mysql.connector.Error as e:

        print(
            "Users database error:",
            e
        )

        flash(
            "Unable to load users.",
            "danger"
        )

        return redirect(
            url_for("admin_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# ADD USER
# =========================================================

@app.route(
    "/admin/users/add",
    methods=["POST"]
)
def add_user():

    if not admin_required():

        return redirect(
            url_for("login")
        )


    name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    role = request.form.get(
        "role",
        "patient"
    ).strip()


    # =================================================
    # VALIDATION
    # =================================================

    if not name or not email or not password:

        flash(
            "All fields are required.",
            "danger"
        )

        return redirect(
            url_for("admin_users")
        )


    allowed_roles = [
        "admin",
        "patient",
        "doctor"
    ]


    if role not in allowed_roles:

        role = "patient"


    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        # =================================================
        # CHECK EMAIL
        # =================================================

        cursor.execute(
            """
            SELECT
                id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing_user = cursor.fetchone()


        if existing_user:

            flash(
                "Email already exists.",
                "warning"
            )

            return redirect(
                url_for("admin_users")
            )


        # =================================================
        # HASH PASSWORD
        # =================================================

        hashed_password = generate_password_hash(
            password
        )


        # =================================================
        # INSERT USER
        # =================================================

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password,
                role
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                name,
                email,
                hashed_password,
                role
            )
        )


        connection.commit()


        flash(
            "User added successfully.",
            "success"
        )


    except mysql.connector.Error as e:

        print(
            "Add user error:",
            e
        )

        if connection:
            connection.rollback()

        flash(
            "Unable to add user.",
            "danger"
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


    return redirect(
        url_for("admin_users")
    )


# =========================================================
# DELETE USER
# =========================================================

@app.route(
    "/admin/users/delete/<int:user_id>",
    methods=["POST"]
)
def delete_user(user_id):

    if not admin_required():

        return redirect(
            url_for("login")
        )


    if user_id == session.get("user_id"):

        flash(
            "You cannot delete your own account.",
            "warning"
        )

        return redirect(
            url_for("admin_users")
        )


    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            DELETE FROM users
            WHERE id = %s
            """,
            (user_id,)
        )


        connection.commit()


        flash(
            "User deleted successfully.",
            "success"
        )


    except mysql.connector.Error as e:

        print(
            "Delete user error:",
            e
        )

        if connection:
            connection.rollback()

        flash(
            "Unable to delete user.",
            "danger"
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


    return redirect(
        url_for("admin_users")
    )


# =========================================================
# ADMIN DOCTORS MANAGEMENT
# =========================================================

@app.route("/admin/doctors")
def admin_doctors():

    if not admin_required():

        return redirect(
            url_for("login")
        )


    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT
                id,
                name,
                specialization,
                department,
                phone,
                email,
                experience,
                availability,
                created_at
            FROM doctors
            ORDER BY id DESC
            """
        )


        doctors_list = cursor.fetchall()


        return render_template(
            "admin_doctors.html",
            doctors=doctors_list
        )


    except mysql.connector.Error as e:

        print(
            "Admin doctors error:",
            e
        )

        flash(
            "Unable to load doctors.",
            "danger"
        )

        return redirect(
            url_for("admin_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
# =========================================================
# ADD DOCTOR
# =========================================================

@app.route(
    "/admin/doctors/add",
    methods=["POST"]
)
def add_doctor():

    if not admin_required():
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    specialization = request.form.get("specialization", "").strip()
    department = request.form.get("department", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    experience = request.form.get("experience", "").strip()
    availability = request.form.get("availability", "").strip()

    if not name or not specialization:
        flash(
            "Doctor name and specialization are required.",
            "danger"
        )
        return redirect(url_for("admin_doctors"))

    if experience:
        try:
            experience = int(experience)
        except ValueError:
            flash(
                "Experience must be a number.",
                "danger"
            )
            return redirect(url_for("admin_doctors"))
    else:
        experience = None

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        if email:

            cursor.execute(
                """
                SELECT id
                FROM doctors
                WHERE email = %s
                """,
                (email,)
            )

            existing_doctor = cursor.fetchone()

            if existing_doctor:
                flash(
                    "Doctor email already exists.",
                    "warning"
                )
                return redirect(url_for("admin_doctors"))

        cursor.execute(
            """
            INSERT INTO doctors
            (
                name,
                specialization,
                department,
                phone,
                email,
                experience,
                availability
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                name,
                specialization,
                department or None,
                phone or None,
                email or None,
                experience,
                availability or None
            )
        )

        connection.commit()

        flash(
            "Doctor added successfully.",
            "success"
        )

    except mysql.connector.Error as e:

        if connection:
            connection.rollback()

        print("Add doctor error:", e)

        flash(
            "Unable to add doctor.",
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(url_for("admin_doctors"))


# =========================================================
# EDIT DOCTOR
# =========================================================

@app.route(
    "/admin/doctors/edit/<int:doctor_id>",
    methods=["GET", "POST"]
)
def edit_doctor(doctor_id):

    if not admin_required():
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                name,
                specialization,
                department,
                phone,
                email,
                experience,
                availability
            FROM doctors
            WHERE id = %s
            """,
            (doctor_id,)
        )

        doctor = cursor.fetchone()

        if not doctor:

            flash(
                "Doctor not found.",
                "danger"
            )

            return redirect(
                url_for("admin_doctors")
            )

        # =================================================
        # UPDATE DOCTOR
        # =================================================

        if request.method == "POST":

            name = request.form.get(
                "name",
                ""
            ).strip()

            specialization = request.form.get(
                "specialization",
                ""
            ).strip()

            department = request.form.get(
                "department",
                ""
            ).strip()

            phone = request.form.get(
                "phone",
                ""
            ).strip()

            email = request.form.get(
                "email",
                ""
            ).strip()

            experience = request.form.get(
                "experience",
                ""
            ).strip()

            availability = request.form.get(
                "availability",
                ""
            ).strip()

            if not name or not specialization:

                flash(
                    "Doctor name and specialization are required.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "edit_doctor",
                        doctor_id=doctor_id
                    )
                )

            if experience:

                try:
                    experience = int(experience)

                except ValueError:

                    flash(
                        "Experience must be a number.",
                        "danger"
                    )

                    return redirect(
                        url_for(
                            "edit_doctor",
                            doctor_id=doctor_id
                        )
                    )

            else:

                experience = None

            cursor.execute(
                """
                UPDATE doctors
                SET
                    name = %s,
                    specialization = %s,
                    department = %s,
                    phone = %s,
                    email = %s,
                    experience = %s,
                    availability = %s
                WHERE id = %s
                """,
                (
                    name,
                    specialization,
                    department or None,
                    phone or None,
                    email or None,
                    experience,
                    availability or None,
                    doctor_id
                )
            )

            connection.commit()

            flash(
                "Doctor updated successfully.",
                "success"
            )

            return redirect(
                url_for("admin_doctors")
            )

        return render_template(
            "edit_doctor.html",
            doctor=doctor
        )

    except mysql.connector.Error as e:

        if connection:
            connection.rollback()

        print(
            "Edit doctor error:",
            e
        )

        flash(
            "Unable to update doctor.",
            "danger"
        )

        return redirect(
            url_for("admin_doctors")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# DELETE DOCTOR
# =========================================================

@app.route(
    "/admin/doctors/delete/<int:doctor_id>",
    methods=["POST"]
)
def delete_doctor(doctor_id):

    if not admin_required():
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM doctors
            WHERE id = %s
            """,
            (doctor_id,)
        )

        connection.commit()

        flash(
            "Doctor deleted successfully.",
            "success"
        )

    except mysql.connector.Error as e:

        if connection:
            connection.rollback()

        print(
            "Delete doctor error:",
            e
        )

        flash(
            "Unable to delete doctor.",
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(
        url_for("admin_doctors")
    )
 
@app.route("/admin/innovations")
def admin_innovations():

    if not admin_required():
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                title,
                description,
                icon,
                created_at
            FROM innovations
            ORDER BY id DESC
        """)

        innovations = cursor.fetchall()

        return render_template(
            "admin_innovations.html",
            innovations=innovations
        )

    except mysql.connector.Error as e:

        print("Admin innovations error:", e)

        flash(
            "Unable to load innovations.",
            "danger"
        )

        return redirect(url_for("admin_dashboard"))

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
# =========================================================
# ADD / EDIT AI INNOVATION
# =========================================================

@app.route(
    "/admin/innovations/add",
    methods=["GET", "POST"]
)
def add_innovation():

    if not admin_required():
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        if request.method == "POST":

            title = request.form.get(
                "title", ""
            ).strip()

            description = request.form.get(
                "description", ""
            ).strip()

            icon = request.form.get(
                "icon",
                "fa-solid fa-brain"
            ).strip()

            if not title or not description:

                flash(
                    "Title and description are required.",
                    "warning"
                )

                return render_template(
                    "innovation_form.html",
                    innovation=None,
                    form_title="Add AI Innovation"
                )

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO innovations
                (title, description, icon)
                VALUES (%s, %s, %s)
                """,
                (
                    title,
                    description,
                    icon
                )
            )

            connection.commit()

            flash(
                "AI Innovation added successfully.",
                "success"
            )

            return redirect(
                url_for("admin_innovations")
            )

        return render_template(
            "innovation_form.html",
            innovation=None,
            form_title="Add AI Innovation"
        )

    except mysql.connector.Error as e:

        print(
            "Add innovation error:",
            e
        )

        if connection:
            connection.rollback()

        flash(
            "Unable to add AI Innovation.",
            "danger"
        )

        return redirect(
            url_for("admin_innovations")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# EDIT AI INNOVATION
# =========================================================

@app.route(
    "/admin/innovations/edit/<int:innovation_id>",
    methods=["GET", "POST"]
)
def edit_innovation(innovation_id):

    if not admin_required():
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                title,
                description,
                icon
            FROM innovations
            WHERE id = %s
            """,
            (innovation_id,)
        )

        innovation = cursor.fetchone()

        if not innovation:

            flash(
                "Innovation not found.",
                "danger"
            )

            return redirect(
                url_for("admin_innovations")
            )

        if request.method == "POST":

            title = request.form.get(
                "title", ""
            ).strip()

            description = request.form.get(
                "description", ""
            ).strip()

            icon = request.form.get(
                "icon",
                "fa-solid fa-brain"
            ).strip()

            if not title or not description:

                flash(
                    "Title and description are required.",
                    "warning"
                )

                return render_template(
                    "innovation_form.html",
                    innovation=innovation,
                    form_title="Edit AI Innovation"
                )

            cursor.execute(
                """
                UPDATE innovations
                SET
                    title = %s,
                    description = %s,
                    icon = %s
                WHERE id = %s
                """,
                (
                    title,
                    description,
                    icon,
                    innovation_id
                )
            )

            connection.commit()

            flash(
                "AI Innovation updated successfully.",
                "success"
            )

            return redirect(
                url_for("admin_innovations")
            )

        return render_template(
            "innovation_form.html",
            innovation=innovation,
            form_title="Edit AI Innovation"
        )

    except mysql.connector.Error as e:

        print(
            "Edit innovation error:",
            e
        )

        if connection:
            connection.rollback()

        flash(
            "Unable to edit AI Innovation.",
            "danger"
        )

        return redirect(
            url_for("admin_innovations")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
# =========================================================
# DELETE AI INNOVATION
# =========================================================

@app.route(
    "/admin/innovations/delete/<int:innovation_id>",
    methods=["POST"]
)
def delete_innovation(innovation_id):

    if not admin_required():
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM innovations
            WHERE id = %s
            """,
            (innovation_id,)
        )

        connection.commit()

        flash(
            "AI Innovation deleted successfully.",
            "success"
        )

    except mysql.connector.Error as e:

        print(
            "Delete innovation error:",
            e
        )

        if connection:
            connection.rollback()

        flash(
            "Unable to delete AI Innovation.",
            "danger"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(
        url_for("admin_innovations")
    )
# =========================================================
# ADMIN PATIENTS MANAGEMENT
# =========================================================

@app.route("/admin/patients")
def admin_patients():

    if not admin_required():

        return redirect(
            url_for("login")
        )


    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT
                id,
                user_id,
                name,
                age,
                gender,
                phone,
                address,
                blood_group,
                created_at
            FROM patients
            ORDER BY id DESC
            """
        )


        patients = cursor.fetchall()


        return render_template(
            "admin_patients.html",
            patients=patients
        )


    except mysql.connector.Error as e:

        print(
            "Admin patients error:",
            e
        )

        flash(
            "Unable to load patients.",
            "danger"
        )

        return redirect(
            url_for("admin_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
# =========================================================
# EDIT PATIENT
# =========================================================

@app.route(
    "/admin/patients/edit/<int:patient_id>",
    methods=["GET", "POST"]
)
def edit_patient(patient_id):

    if not admin_required():
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # GET PATIENT
        cursor.execute(
            """
            SELECT
                id,
                user_id,
                name,
                age,
                gender,
                phone,
                address,
                blood_group
            FROM patients
            WHERE id = %s
            """,
            (patient_id,)
        )

        patient = cursor.fetchone()

        if not patient:

            flash(
                "Patient not found.",
                "danger"
            )

            return redirect(
                url_for("admin_patients")
            )

        # UPDATE PATIENT
        if request.method == "POST":

            name = request.form.get(
                "name",
                ""
            ).strip()

            age = request.form.get(
                "age",
                ""
            ).strip()

            gender = request.form.get(
                "gender",
                ""
            ).strip()

            phone = request.form.get(
                "phone",
                ""
            ).strip()

            address = request.form.get(
                "address",
                ""
            ).strip()

            blood_group = request.form.get(
                "blood_group",
                ""
            ).strip()


            # VALIDATION
            if not name:

                flash(
                    "Patient name is required.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "edit_patient",
                        patient_id=patient_id
                    )
                )


            if age:

                try:

                    age = int(age)

                except ValueError:

                    flash(
                        "Age must be a number.",
                        "danger"
                    )

                    return redirect(
                        url_for(
                            "edit_patient",
                            patient_id=patient_id
                        )
                    )

            else:

                age = None


            # UPDATE DATABASE
            cursor.execute(
                """
                UPDATE patients
                SET
                    name = %s,
                    age = %s,
                    gender = %s,
                    phone = %s,
                    address = %s,
                    blood_group = %s
                WHERE id = %s
                """,
                (
                    name,
                    age,
                    gender,
                    phone,
                    address,
                    blood_group,
                    patient_id
                )
            )

            connection.commit()


            flash(
                "Patient updated successfully.",
                "success"
            )

            return redirect(
                url_for("admin_patients")
            )


        return render_template(
            "edit_patient.html",
            patient=patient
        )


    except mysql.connector.Error as e:

        if connection:
            connection.rollback()

        print(
            "Edit patient error:",
            e
        )

        flash(
            "Unable to update patient.",
            "danger"
        )

        return redirect(
            url_for("admin_patients")
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# ADD PATIENT
# =========================================================

@app.route(
    "/admin/patients/add",
    methods=["POST"]
)
def add_patient():

    if not admin_required():

        return redirect(
            url_for("login")
        )


    name = request.form.get(
        "name",
        ""
    ).strip()

    age = request.form.get(
        "age",
        ""
    ).strip()

    gender = request.form.get(
        "gender",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    address = request.form.get(
        "address",
        ""
    ).strip()

    blood_group = request.form.get(
        "blood_group",
        ""
    ).strip()


    # =================================================
    # VALIDATION
    # =================================================

    if not name:

        flash(
            "Patient name is required.",
            "danger"
        )

        return redirect(
            url_for("admin_patients")
        )


    if age:

        try:

            age = int(age)

            if age < 0:
                raise ValueError

        except ValueError:

            flash(
                "Age must be a valid number.",
                "danger"
            )

            return redirect(
                url_for("admin_patients")
            )

    else:

        age = None


    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO patients
            (
                user_id,
                name,
                age,
                gender,
                phone,
                address,
                blood_group
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                None,
                name,
                age,
                gender or None,
                phone or None,
                address or None,
                blood_group or None
            )
        )


        connection.commit()


        flash(
            "Patient added successfully.",
            "success"
        )


    except mysql.connector.Error as e:

        print(
            "Add patient error:",
            e
        )

        if connection:
            connection.rollback()

        flash(
            "Unable to add patient.",
            "danger"
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


    return redirect(
        url_for("admin_patients")
    )


# =========================================================
# DELETE PATIENT
# =========================================================

@app.route(
    "/admin/patients/delete/<int:patient_id>",
    methods=["POST"]
)
def delete_patient(patient_id):

    if not admin_required():

        return redirect(
            url_for("login")
        )


    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            DELETE FROM patients
            WHERE id = %s
            """,
            (patient_id,)
        )


        connection.commit()


        flash(
            "Patient deleted successfully.",
            "success"
        )


    except mysql.connector.Error as e:

        print(
            "Delete patient error:",
            e
        )

        if connection:
            connection.rollback()

        flash(
            "Unable to delete patient.",
            "danger"
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


    return redirect(
        url_for("admin_patients")
    )


# =========================================================
# ADMIN APPOINTMENTS MANAGEMENT
# =========================================================

@app.route("/admin/appointments")
def admin_appointments():

    if not admin_required():

        return redirect(
            url_for("login")
        )


    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            """
            SELECT
                a.id,
                a.patient_id,
                a.doctor_id,
                a.appointment_date,
                a.appointment_time,
                a.reason,
                a.status,
                a.created_at,
                p.name AS patient_name,
                d.name AS doctor_name
            FROM appointments a
            LEFT JOIN patients p
                ON a.patient_id = p.id
            LEFT JOIN doctors d
                ON a.doctor_id = d.id
            ORDER BY a.id DESC
            """
        )


        appointments = cursor.fetchall()


        return render_template(
            "admin_appointments.html",
            appointments=appointments
        )


    except mysql.connector.Error as e:

        print(
            "Admin appointments error:",
            e
        )

        flash(
            "Unable to load appointments.",
            "danger"
        )

        return redirect(
            url_for("admin_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# DELETE APPOINTMENT
# =========================================================

@app.route(
    "/admin/appointments/delete/<int:appointment_id>",
    methods=["POST"]
)
def delete_appointment(appointment_id):

    if not admin_required():

        return redirect(
            url_for("login")
        )


    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            DELETE FROM appointments
            WHERE id = %s
            """,
            (appointment_id,)
        )


        connection.commit()


        flash(
            "Appointment deleted successfully.",
            "success"
        )


    except mysql.connector.Error as e:

        print(
            "Delete appointment error:",
            e
        )

        if connection:
            connection.rollback()

        flash(
            "Unable to delete appointment.",
            "danger"
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


    return redirect(
        url_for("admin_appointments")
    )


# =========================================================
# UPDATE APPOINTMENT STATUS
# =========================================================

@app.route(
    "/admin/appointments/update/<int:appointment_id>",
    methods=["POST"]
)
def update_appointment_status(appointment_id):

    if not admin_required():

        return redirect(
            url_for("login")
        )


    status = request.form.get(
        "status",
        ""
    ).strip()


    allowed_statuses = [
        "Pending",
        "Approved",
        "Completed",
        "Cancelled"
    ]


    if status not in allowed_statuses:

        flash(
            "Invalid appointment status.",
            "danger"
        )

        return redirect(
            url_for("admin_appointments")
        )


    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            UPDATE appointments
            SET status = %s
            WHERE id = %s
            """,
            (
                status,
                appointment_id
            )
        )


        connection.commit()


        flash(
            "Appointment status updated successfully.",
            "success"
        )


    except mysql.connector.Error as e:

        print(
            "Update appointment error:",
            e
        )

        if connection:
            connection.rollback()

        flash(
            "Unable to update appointment status.",
            "danger"
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


    return redirect(
        url_for("admin_appointments")
    )


# =========================================================
# DATABASE TEST
# =========================================================

@app.route("/db-test")
def db_test():

    connection = None
    cursor = None


    try:

        connection = get_db_connection()

        cursor = connection.cursor()


        cursor.execute(
            "SELECT DATABASE()"
        )


        result = cursor.fetchone()


        return (
            "Database connected successfully: "
            + str(result[0])
        )


    except mysql.connector.Error as e:

        return (
            "Database connection failed: "
            + str(e)
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
@app.route('/medical-records', methods=['GET', 'POST'])
def medical_records():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':

        patient_name = request.form.get('patient_name')
        record_type = request.form.get('record_type')
        diagnosis = request.form.get('diagnosis')
        doctor_name = request.form.get('doctor_name')
        record_date = request.form.get('record_date')
        description = request.form.get('description')

        cursor.execute("""
            INSERT INTO medical_records
            (
                user_id,
                patient_name,
                record_type,
                diagnosis,
                doctor_name,
                record_date,
                description
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            patient_name,
            record_type,
            diagnosis,
            doctor_name,
            record_date,
            description
        ))

        conn.commit()

    cursor.execute("""
        SELECT *
        FROM medical_records
        WHERE user_id = %s
        ORDER BY record_date DESC, id DESC
    """, (session['user_id'],))

    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'medical_records.html',
        records=records
    )
@app.route('/laboratory', methods=['GET', 'POST'])
def laboratory():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':

        patient_name = request.form.get('patient_name')
        test_name = request.form.get('test_name')
        doctor_name = request.form.get('doctor_name')
        test_date = request.form.get('test_date')
        result = request.form.get('result')
        remarks = request.form.get('remarks')

        cursor.execute("""
            INSERT INTO laboratory_records
            (
                user_id,
                patient_name,
                test_name,
                doctor_name,
                test_date,
                result,
                remarks
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            patient_name,
            test_name,
            doctor_name,
            test_date,
            result,
            remarks
        ))

        conn.commit()

    cursor.execute("""
        SELECT *
        FROM laboratory_records
        WHERE user_id = %s
        ORDER BY test_date DESC, id DESC
    """, (session['user_id'],))

    lab_records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'laboratory.html',
        lab_records=lab_records
    )
@app.route('/pharmacy', methods=['GET', 'POST'])
def pharmacy():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':

        patient_name = request.form.get('patient_name')
        doctor_name = request.form.get('doctor_name')
        medicine_name = request.form.get('medicine_name')
        dosage = request.form.get('dosage')
        duration = request.form.get('duration')
        instructions = request.form.get('instructions')
        prescription_date = request.form.get('prescription_date')

        cursor.execute("""
            INSERT INTO prescriptions
            (
                user_id,
                patient_name,
                doctor_name,
                medicine_name,
                dosage,
                duration,
                instructions,
                prescription_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            patient_name,
            doctor_name,
            medicine_name,
            dosage,
            duration,
            instructions,
            prescription_date
        ))

        conn.commit()

    cursor.execute("""
        SELECT *
        FROM prescriptions
        WHERE user_id = %s
        ORDER BY prescription_date DESC, id DESC
    """, (session['user_id'],))

    prescriptions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'pharmacy.html',
        prescriptions=prescriptions
    )
@app.route('/billing', methods=['GET', 'POST'])
def billing():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':

        patient_name = request.form.get('patient_name')
        consultation_fee = float(request.form.get('consultation_fee') or 0)
        lab_charges = float(request.form.get('lab_charges') or 0)
        medicine_charges = float(request.form.get('medicine_charges') or 0)
        other_charges = float(request.form.get('other_charges') or 0)
        payment_status = request.form.get('payment_status')
        bill_date = request.form.get('bill_date')

        total_amount = (
            consultation_fee
            + lab_charges
            + medicine_charges
            + other_charges
        )

        cursor.execute("""
            INSERT INTO bills
            (
                user_id,
                patient_name,
                consultation_fee,
                lab_charges,
                medicine_charges,
                other_charges,
                total_amount,
                payment_status,
                bill_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            patient_name,
            consultation_fee,
            lab_charges,
            medicine_charges,
            other_charges,
            total_amount,
            payment_status,
            bill_date
        ))

        conn.commit()

    cursor.execute("""
        SELECT *
        FROM bills
        WHERE user_id = %s
        ORDER BY bill_date DESC, id DESC
    """, (session['user_id'],))

    bills = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'billing.html',
        bills=bills
    )
@app.route('/emergency-care', methods=['GET', 'POST'])
def emergency_care():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':

        patient_name = request.form.get('patient_name')
        emergency_type = request.form.get('emergency_type')
        symptoms = request.form.get('symptoms')
        contact_number = request.form.get('contact_number')

        cursor.execute("""
            INSERT INTO emergency_requests
            (
                user_id,
                patient_name,
                emergency_type,
                symptoms,
                contact_number
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            patient_name,
            emergency_type,
            symptoms,
            contact_number
        ))

        conn.commit()

    cursor.execute("""
        SELECT *
        FROM emergency_requests
        WHERE user_id = %s
        ORDER BY id DESC
    """, (session['user_id'],))

    emergency_requests = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'emergency_care.html',
        emergency_requests=emergency_requests
    )
# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )

