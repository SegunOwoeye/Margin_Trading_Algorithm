import streamlit as st

with st.container():
   col1, col2 = st.columns(2)

   with col1:
       if st.button("Button 1"):
           st.write("Button 1 was clicked!")  # Replace with your desired action

   with col2:
       if st.button("Button 2"):
           st.line_chart({"data": [1, 5, 2, 8]})  # Replace with your desired action