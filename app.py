import streamlit as st
import requests
import pandas as pd

# পেজ লেআউট কনফিগারেশন
st.set_page_config(page_title="NeverBounce Clone - Inferno Edition", layout="wide")

# --- কাস্টম ফায়ার থেম এবং ফুল-স্ক্রিন রানিং ফায়ার অ্যানিমেশন CSS ---
st.markdown("""
<style>
    /* পুরো ওয়েবপেজের ফায়ার ব্যাকগ্রাউন্ড এবং অ্যানিমেশন */
    .stApp {
        background: linear-gradient(135deg, #180202 0%, #3a0a00 35%, #7c1100 70%, #b91c1c 100%);
        background-size: 400% 400%;
        animation: fireBackgroundGlow 8s ease infinite;
        color: #ffedd5;
    }

    @keyframes fireBackgroundGlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ফুল স্ক্রিন ফায়ার রানিং ট্র্যাক কন্টেইনার */
    .fire-runner-track {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100vw;
        height: 120px;
        pointer-events: none;
        z-index: 99999;
        overflow: hidden;
    }

    /* দৌড়ানোর অ্যানিমেটেড হিউম্যান ফিগার */
    .running-human-container {
        position: absolute;
        bottom: 10px;
        animation: runAcrossFullPage 6s linear infinite;
    }

    @keyframes runAcrossFullPage {
        0% {
            left: -180px;
            transform: scaleX(1);
        }
        100% {
            left: 100vw;
            transform: scaleX(1);
        }
    }

    /* কন্টেন্ট কার্ডগুলোকে ফায়ার থিমের সাথে মানানসই করা */
    div[data-testid="stVerticalBlock"] > div {
        background-color: rgba(43, 9, 2, 0.85);
        border: 1px solid rgba(255, 69, 0, 0.4);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }

    /* হেডিং এবং টেক্সট কালার */
    h1, h2, h3, h4, h5, h6, p, label {
        color: #ffedd5 !important;
    }
</style>

<!-- ফুল স্ক্রিন রানিং এবং অ্যাস ফায়ারিং অ্যানিমেশন -->
<div class="fire-runner-track">
    <div class="running-human-container">
        <svg width="160" height="90" viewBox="0 0 160 90" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- জেট ফায়ার ফ্রম ব্যাক / অ্যাস ফায়ারিং ইফেক্ট -->
            <path d="M35 52 L5 45 L35 38 L20 45 Z" fill="#ff4500">
                <animate attributeName="d" values="M35 52 L-5 45 L35 38 L15 45 Z; M35 56 L-25 45 L35 34 L-5 45 Z; M35 52 L-5 45 L35 38 L15 45 Z" dur="0.15s" repeatCount="indefinite"/>
            </path>
            <path d="M40 55 L-10 45 L40 35 Z" fill="#ffcc00" opacity="0.9">
                <animate attributeName="d" values="M40 55 L-10 45 L40 35 Z; M40 60 L-30 45 L40 30 Z; M40 55 L-10 45 L40 35 Z" dur="0.15s" repeatCount="indefinite"/>
            </path>
            
            <!-- ফুল হিউম্যান বডি স্ট্রাকচার -->
            <circle cx="105" cy="22" r="11" fill="#ffe4c4"/>
            <path d="M95 18 Q105 10 115 18" stroke="#ff4500" stroke-width="4" stroke-linecap="round"/>
            <path d="M105 33 L98 58 L85 75" stroke="#ffe4c4" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M100 42 L120 48 L130 40" stroke="#ffe4c4" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M100 42 L80 50 L70 42" stroke
