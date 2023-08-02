import streamlit as st
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from utils import Smart_Agent, HR_PERSONA, HR_AVAILABLE_FUNCTIONS, HR_FUNCTIONS_SPEC
import concurrent.futures
import time
import random
import openai
import os
from pathlib import Path  
import json
hr_agent = Smart_Agent(persona=HR_PERSONA,functions_list=HR_AVAILABLE_FUNCTIONS, functions_spec=HR_FUNCTIONS_SPEC, init_message="Hi there, this is Lucy, HR specialist helping with answering questions about HR & Payroll and handle personal information updates, may I have your name and employee ID?")

st.set_page_config(layout="wide",page_title="Enterprise Copilot- A demo of Copilot application using GPT")
styl = f"""
<style>
    .stTextInput {{
      position: fixed;
      bottom: 3rem;
    }}
</style>
"""
st.markdown(styl, unsafe_allow_html=True)


MAX_HIST= 5
# Sidebar contents
with st.sidebar:
    st.title('HR/Payroll Copilot')
    st.markdown('''
    This is a demo of Copilot Concept for HR/Payroll. The Copilot helps employees answer questions and update personal information.

    Copilot will first validate the identity of the employee before answering any questions or updating any information.
    Use ids such as 1234 or 5678 to test the demo.
   
    Example questions to ask:
    - When do I receive W2 form?
    - What are deducted from my paycheck?    
    
    These questions are answered by the Copilot by searching a knowledge base and providing the answer.
                
    Copilot also can help update information. 
    - For address update, the Copilot will update the information in the system. 
    - For other information update requests, the Copilot will log a ticket to the HR team to update the information.
    
    ''')
    add_vertical_space(5)
    st.write('Created by James N')
    if st.button('Clear Chat'):

        if 'history' in st.session_state:
            st.session_state['history'] = []

    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'input' not in st.session_state:
        st.session_state['input'] = ""




# User input
## Function for taking user provided prompt as input
def clear():
    st.session_state.input_var = st.session_state.input
    st.session_state.input = ''

def get_text():
    st.text_input("You: ", "", key="input", on_change= clear())
    return st.session_state.input_var
## Applying the user input box
# with input_container:
user_input = get_text()

## Conditional display of AI generated responses as a function of user provided prompts
history = st.session_state['history']
      
if len(history) > 0:
    bot_history = [item['content'] for item in history if (item['role'] == 'assistant') and (item.get("name") is  None)]
    #trim history
    # bot_history = bot_history[-MAX_HIST-1:]
    user_history = [item['content'] for item in history if item['role'] == 'user']
    # user_history = user_history[-MAX_HIST-1:]

    for i in range(len(bot_history)):
        if i>0:
            if len(user_history) > i-1:
                message(user_history[i-1], is_user=True, key=str(i) + '_user') #this is because the bot starts first.
        message(bot_history[i], key=str(i))
else:
    history, agent_response = hr_agent.run(user_input=None)
    message(agent_response, is_user=False, key=str(0) + '_assistant')
    user_history=[]
if user_input:
    message(user_input,  is_user=True,key=str(len(user_history)+1)+ '_user')
    history, agent_response = hr_agent.run(user_input=user_input, conversation=history)
    message(agent_response,  is_user=False,key=str(len(bot_history)+1)+ '_assistant')
st.session_state['history'] = history