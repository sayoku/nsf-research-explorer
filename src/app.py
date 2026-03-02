import streamlit as st
#import networkx as nx
import matplotlib.pyplot as plt
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from agent.tool import NSFAgent
from kgraph.mem import KGBuilder

st.set_page_config(page_title="NSF Research Explorer", layout="wide")

st.title("NSF Research Award Explorer")
st.markdown(
    """ 
    Explore NSF grants using natural language queries and visualize the knowledge graph 

    **There's :rainbow[so much] you can find!**
    """
)

if st.button("Send balloons!"):
    st.balloons()
