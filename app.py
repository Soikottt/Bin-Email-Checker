import streamlit as st
import requests
import pandas as pd

# পেজ লেআউট কনফিগারেশন
st.set_page_config(page_title="ভইরা দিলাম, কইরা খা!", layout="wide")

# --- ফায়ার ব্যাকগ্রাউন্ড এবং আইস কোল্ড ইনপুট বক্সের জন্য CSS ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #2a0800 0%, #6b1100 40%, #b91c1c 80%, #ea580c 100%);
        background-size: 400% 400%;
        animation: fireGlow 10s ease infinite;
        color: #ffffff;
    }

    @keyframes fireGlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    div.stTextInput > div.st-bx > div, div.stTextInput input {
        background-color: #e0f2fe !important;
        color: #0369a1 !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 8px !important;
        font-weight: bold;
    }
    
    div.stTextInput input::placeholder {
        color: #0284c7 !important;
    }

    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Streamlit Secrets থেকে দুটি এপিআই কি লোড করা
try:
    ABSTRACT_API_KEY = st.secrets["ABSTRACT_API_KEY"]
except Exception:
    ABSTRACT_API_KEY = None

try:
    HUNTER_API_KEY = st.secrets["HUNTER_API_KEY"]
except Exception:
    HUNTER_API_KEY = None

if not ABSTRACT_API_KEY and not HUNTER_API_KEY:
    st.error("Please configure at least one API key (ABSTRACT_API_KEY or HUNTER_API_KEY) in Streamlit Secrets!")
    st.stop()

# রাউন্ড-রবিন কাউন্টার ইনিশিয়ালাইজ করা
if 'api_counter' not in st.session_state:
    st.session_state.api_counter = 0

# --- Round-Robin API Verification Function ---
def verify_with_round_robin(email):
    # কোন এপিআই ব্যবহার হবে তা নির্ধারণ (বিকল্প পদ্ধতিতে সুইচ করা)
    available_apis = []
    if ABSTRACT_API_KEY: available_apis.append("ABSTRACT")
    if HUNTER_API_KEY: available_apis.append("HUNTER")
    
    if not available_apis:
        return {"error": "No API keys available."}
    
    # রাউন্ড-রবিন লজিক
    current_api_type = available_apis[st.session_state.api_counter % len(available_apis)]
    st.session_state.api_counter += 1
    
    if current_api_type == "ABSTRACT":
        url = f"https://emailreputation.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&email={email}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                d_dict = data.get("email_deliverability", {})
                status = d_dict.get("status", "UNKNOWN").upper() if isinstance(d_dict, dict) else "UNKNOWN"
                return {
                    "api_used": "Abstract API",
                    "deliverability": status,
                    "quality_score": data.get("quality_score", "N/A"),
                    "raw": data
                }
            else:
                return {"api_used": "Abstract API", "error": f"Status {response.status_code}: {response.text}"}
        except Exception as e:
            return {"api_used": "Abstract API", "error": str(e)}
            
    else: # HUNTER API
        url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={HUNTER_API_KEY}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json().get("data", {})
                status = data.get("result", "unknown").upper() # deliverable, undeliverable etc.
                # Hunter স্ট্যাটাসকে স্ট্যান্ডার্ড ফরম্যাটে রূপান্তর
                deliverability = "DELIVERABLE" if status == "DELIVERABLE" else status
                return {
                    "api_used": "Hunter.io API",
                    "deliverability": deliverability,
                    "quality_score": data.get("score", "N/A"),
                    "raw": data
                }
            else:
                return {"api_used": "Hunter.io API", "error": f"Status {response.status_code}: {response.text}"}
        except Exception as e:
            return {"api_used": "Hunter.io API", "error": str(e)}

# অ্যাপ টাইটেল এবং হেডার
st.title("🔥 ভইরা দিলাম, কইরা খা! (Round-Robin Engine)")
st.markdown("### Multi-API High-Performance Bulk & Single Email Validation System")

tab1, tab2 = st.tabs(["Single Email Verification", "Bulk CSV Verification"])

# --- TAB 1: Single Email ---
with tab1:
    st.header("Check Single Email")
    email_input = st.text_input("Enter email address for verification:", placeholder="name@example.com")
    
    if st.button("Verify Email"):
        if email_input:
            with st.spinner("Executing round-robin high-speed verification..."):
                result = verify_with_round_robin(email_input)
                
                if result and "error" not in result:
                    deliverability = result.get("deliverability")
                    api_used = result.get("api_used")
                    
                    st.info(f"⚡ Routed via: **{api_used}**")
                    
                    # শর্ত অনুযায়ী কাস্টম মেসেজ এবং কালার ডিসপ্লে করা
                    if deliverability == "DELIVERABLE":
                        st.markdown("<p style='color: #22c55e; font-size: 24px; font-weight: bold;'>amar pawna taka ferot de, manger nati</p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p style='color: #ef4444; font-size: 24px; font-weight: bold;'>email putki diya dimu</p>", unsafe_allow_html=True)

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Status", deliverability)
                    col2.metric("Quality Score", str(result.get("quality_score", "N/A")))
                    col3.metric("API Used", api_used)
                    
                    with st.expander("See Full JSON Response"):
                        st.json(result.get("raw"))
                else:
                    error_msg = result.get("error") if result else "Unknown error"
                    st.error(f"Failed to verify via {result.get('api_used', 'API')}. Details: {error_msg}")
        else:
            st.warning("Please enter an email address first.")

# --- TAB 2: Bulk Email (CSV) ---
with tab2:
    st.header("Bulk Email Verification (CSV Upload)")
    st.markdown("Upload a CSV file that contains a column named **'email'**.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        if 'email' in df.columns:
            st.info(f"Total emails found in file: {len(df)}")
            st.dataframe(df.head())
            
            if st.button("Start Bulk Verification"):
                results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total_emails = len(df)
                for index, row in df.iterrows():
                    email = row['email']
                    status_text.text(f"Processing ({index+1}/{total_emails}): {email}")
                    
                    res = verify_with_round_robin(email)
                    if res and "error" not in res:
                        results.append({
                            "email": email,
                            "deliverability": res.get("deliverability"),
                            "quality_score": res.get("quality_score", 0),
                            "api_used": res.get("api_used")
                        })
                    else:
                        results.append({
                            "email": email,
                            "deliverability": "ERROR",
                            "quality_score": 0,
                            "api_used": res.get("api_used", "UNKNOWN")
                        })
                    
                    progress_bar.progress((index + 1) / total_emails)
                
                status_text.text("Bulk round-robin verification finished successfully!")
                result_df = pd.DataFrame(results)
                
                st.subheader("Verification Results:")
                st.dataframe(result_df)
                
                valid_df = result_df[result_df['deliverability'] == 'DELIVERABLE']
                st.write(f"Total Valid (Deliverable) Emails: {len(valid_df)}")
                
                csv_data = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Full Results as CSV",
                    data=csv_data,
                    file_name='verified_emails_round_robin.csv',
                    mime='text/csv',
                )
        else:
            st.error("Error: Your CSV file must contain a column named exactly **'email'**.")
