import streamlit.components.v1 as components
import os

_component_func = components.declare_component(
    "connect_phantom",
    path=os.path.join(os.path.dirname(__file__), "frontend/build")  # <-- Must match real path
)

def connect_phantom():
    return _component_func(default=None)
