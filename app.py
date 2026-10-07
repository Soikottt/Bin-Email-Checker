import streamlit as st
import requests
import pandas as pd

# পেজ লেআউট কনফিগারেশন
st.set_page_config(page_title="ভইরা দিলাম, কইরা খা!", layout="wide")

# --- ফায়ার ব্যাকগ্রাউন্ড এবং আইস কোল্ড ইনপুট বক্সের জন্য CSS ---
st.markdown("""
<style>
    /* পুরো ওয়েবপেজের ফায়ার ব্যাকগ্রাউন্ড (লাল, কমলা ও হলুদ শেড) */
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

    /* সার্চ বক্স / টেক্সট ইনপুট ফিল্ডের আইস কোল্ড থিম */
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

# Streamlit Secrets থেকে এপিআই কি লোড করা
try:
    API_KEY = st.secrets["ABSTRACT_API_KEY"]
except Exception as e:
    st.error("API Key not found in Streamlit Secrets! Please check your secrets.toml configuration.")
    st.stop()

# সিঙ্গেল ইমেইল চেক করার ফাংশন
def verify_single_email(email):
    url = f"https://emailvalidation.abstractapi.com/v1/?api_key={API_KEY}&email={email}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return {"error": str(e)}
    return None

# অ্যাপ টাইটেল এবং হেডার
st.title("🔥 Inferno & 🧊 Ice Email Verification Engine")
st.markdown("### High-Performance Bulk & Single Email Validation System")

# ট্যাব তৈরি (Single এবং Bulk এর জন্য)
tab1, tab2 = st.tabs(["Single Email Verification", "Bulk CSV Verification"])

# --- TAB 1: Single Email ---
with tab1:
    st.header("Check Single Email")
    email_input = st.text_input("Enter email address for verification:", placeholder="name@example.com")
    
    if st.button("Verify Email"):
        if email_input:
            with st.spinner("Executing high-speed verification..."):
                result = verify_single_email(email_input)
                
                if result and "error" not in result:
                    deliverability = result.get("deliverability")
                    
                    # শর্ত অনুযায়ী কাস্টম মেসেজ এবং কালার ডিসপ্লে করা
                    if deliverability == "DELIVERABLE":
                        st.markdown("<p style='color: #22c55e; font-size: 24px; font-weight: bold;'>amar pawa na taka ferot de, manger nati</p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p style='color: #ef4444; font-size: 24px; font-weight: bold;'>email putki diya dimu</p>", unsafe_allow_html=True)

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Status", deliverability)
                    col2.metric("Quality Score", result.get("quality_score"))
                    col3.metric("Is Disposable?", str(result.get("is_disposable_email", {}).get("value")))
                    
                    with st.expander("See Full JSON Response"):
                        st.json(result)
                else:
                    st.error("Failed to verify. Please check the email or API limits.")
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
                    
                    res = verify_single_email(email)
                    if res and "error" not in res:
                        results.append({
                            "email": email,
                            "deliverability": res.get("deliverability"),
                            "quality_score": res.get("quality_score"),
                            "is_valid_format": res.get("is_valid_format", {}).get("value"),
                            "is_disposable": res.get("is_disposable_email", {}).get("value")
                        })
                    else:
                        results.append({
                            "email": email,
                            "deliverability": "ERROR",
                            "quality_score": 0,
                            "is_valid_format": False,
                            "is_disposable": False
                        })
                    
                    progress_bar.progress((index + 1) / total_emails)
                
                status_text.text("Bulk verification finished successfully")
                result_df = pd.DataFrame(results)
                
                st.subheader("Verification Results:")
                st.dataframe(result_df)
                
                valid_df = result_df[result_df['deliverability'] == 'DELIVERABLE']
                st.write(f"Total Valid (Deliverable) Emails: {len(valid_df)}")
                
                csv_data = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Full Results as CSV",
                    data=csv_data,
                    file_name='verified_emails_full.csv',
                    mime='text/csv',
                )
        else:
            st.error("Error: Your CSV file must contain a column named exactly **'email'**.")
