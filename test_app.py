import streamlit as st

st.title("ChatBot26 - Test")
st.write("If you see this, the app loaded successfully!")

if "test" not in st.session_state:
    st.session_state.test = 0

st.write(f"Counter: {st.session_state.test}")
if st.button("Increment"):
    st.session_state.test += 1
    st.rerun()
