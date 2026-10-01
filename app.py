import streamlit as st
from langchain_ollama import ChatOllama
import matplotlib.pyplot as plt
import pandas as pd
import json
import os

# -------------------------
# 🤖 Model
# -------------------------
llm = ChatOllama(model="llama3.2:1b")

st.title("💰 Personal Finance & Business Analysis Chatbot")

# -------------------------
# 🗑️ Reset Data
# -------------------------
if st.button("🗑️ Reset All Data"):
    st.session_state.expenses = {}
    if os.path.exists("expenses.json"):
        os.remove("expenses.json")
    st.success("Data cleared successfully!")

# -------------------------
# 💾 Load Data
# -------------------------
if "expenses" not in st.session_state:
    try:
        with open("expenses.json", "r") as f:
            st.session_state.expenses = json.load(f)
    except:
        st.session_state.expenses = {}

# -------------------------
# 💸 Expense Input
# -------------------------
st.subheader("Add Expense")

with st.form("expense_form"):
    user_input = st.text_input("Type like: spent 200 on food")
    submitted = st.form_submit_button("Add")

    if submitted:
        if "spent" in user_input.lower():
            try:
                words = user_input.lower().split()

                # extract amount
                amount = None
                for w in words:
                    if w.isdigit():
                        amount = int(w)
                        break

                # extract category
                if "on" in words:
                    category = words[words.index("on") + 1]
                else:
                    category = "other"

                # store
                if category in st.session_state.expenses:
                    st.session_state.expenses[category] += amount
                else:
                    st.session_state.expenses[category] = amount

                st.success(f"Added ₹{amount} to {category}")

                # save to file
                with open("expenses.json", "w") as f:
                    json.dump(st.session_state.expenses, f)

            except:
                st.error("Use format: spent 200 on food")

# -------------------------
# 📊 Graph + Analysis
# -------------------------
if st.session_state.expenses:
    st.subheader("📊 Expense Analysis")

    categories = list(st.session_state.expenses.keys())
    amounts = list(st.session_state.expenses.values())

    # graph
    fig, ax = plt.subplots()
    ax.pie(amounts, labels=categories, autopct='%1.1f%%')
    st.pyplot(fig)

    # basic analysis
    total = sum(amounts)
    highest = max(st.session_state.expenses, key=st.session_state.expenses.get)

    st.write(f"**Total Spending:** ₹{total}")
    st.write(f"**Highest Category:** {highest}")

# -------------------------
# 🤖 Chatbot
# -------------------------
st.subheader("🤖 Finance Chatbot")

question = st.text_input("Ask something (e.g., How to save money?)")

if question:
    response = llm.invoke(
        "You are a simple finance assistant for students. Give short, clear advice.\nUser: "
        + question
    )
    st.write(response.content)

# -------------------------
# 📂 CSV Upload (Excel-style analysis)
# -------------------------
st.subheader("📂 Upload CSV for Analysis")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.write("### 📄 Data Preview")
    st.dataframe(df)

    if "Category" in df.columns and "Amount" in df.columns:

        grouped = df.groupby("Category")["Amount"].sum()

        st.write("### 📊 Category-wise Spending")
        st.write(grouped)

        # graph
        fig, ax = plt.subplots()
        ax.pie(grouped.values, labels=grouped.index, autopct='%1.1f%%')
        st.pyplot(fig)

        # analysis
        total = grouped.sum()
        highest = grouped.idxmax()

        st.write(f"**Total Spending:** ₹{total}")
        st.write(f"**Highest Category:** {highest}")

        st.write("💡 Suggestion: Try reducing spending in high category.")

    else:
        st.error("CSV must contain 'Category' and 'Amount' columns")