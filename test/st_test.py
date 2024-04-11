import streamlit as st
import threading
import time

def loop_1():
    st.write("Loop 1")
    i = 0
    while True:
        st.write("Iteration:", i)
        time.sleep(1)
        i += 1

def loop_2():
    st.write("Loop 2")
    j = 0
    while True:
        st.write("Iteration:", j)
        time.sleep(1)
        j += 1

def main():
    st.title("Two Loop Tabs")

    thread_1 = threading.Thread(target=loop_1)
    thread_2 = threading.Thread(target=loop_2)

    tabs = st.multiselect(
        "Select Tabs",
        options=["Loop 1", "Loop 2"],
        default=["Loop 1"]
    )

    if "Loop 1" in tabs:
        thread_1.start()

    if "Loop 2" in tabs:
        thread_2.start()

if __name__ == "__main__":
    main()
