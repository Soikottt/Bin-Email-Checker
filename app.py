import streamlit as st
import requests
import pandas as pd

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

# পেজ লেআউট কনফিগারেশন
st.set_page_config(page_title="NeverBounce Clone - Secure", layout="wide")
st.title("🛡️ Secure Email Verifier (NeverBounce Clone)")
st.markdown("Powered by Python, Abstract API & Streamlit Secrets")

# ট্যাব তৈরি (Single এবং Bulk এর জন্য)
tab1, tab2 = st.tabs(["🔍 Single Email Verification", "📂 Bulk CSV Verification"])

# --- TAB 1: Single Email ---
with tab1:
    st.header("Check Single Email")
    email_input = st.text_input("Enter email address for verification:")
    
    if st.button("Verify Email"):
        if email_input:
            with st.spinner("Verifying email..."):
                result = verify_single_email(email_input)
                
                if result and "error" not in result:
                    st.success("Verification Complete!")
                    col1, col2, col3 = st.columns(3)
                    
                    col1.metric("Status", result.get("deliverability"))
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
        
        # চেক করা ফাইলে 'email' কলাম আছে কি না
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
                    
                    # এপিআই কল
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
                    
                    # প্রোগ্রেস বার আপডেট
                    progress_bar.progress((index + 1) / total_emails)
                
                status_text.text("Bulk verification finished successfully!")
                result_df = pd.DataFrame(results)
                
                st.subheader("Verification Results:")
                st.dataframe(result_df)
                
                # ফিল্টার করে শুধু ভ্যালিড মেইলগুলো আলাদা ডাউনলোড করার অপশন
                valid_df = result_df[result_df['deliverability'] == 'DELIVERABLE']
                st.write(f"Total Valid (Deliverable) Emails: {len(valid_df)}")
                
                csv_data = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Full Results as CSV",
                    data=csv_data,
                    file_name='verified_emails_full.csv',
                    mime='text/csv',
                )
        else:
            st.error("Error: Your CSV file must contain a column named exactly **'email'**.")