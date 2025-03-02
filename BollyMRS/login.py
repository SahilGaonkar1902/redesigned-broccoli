def log():
    import streamlit as st
    import pymongo as pm
    import time

    # Connect to MongoDB
    client = pm.MongoClient("mongodb://localhost:27017/")
    db = client["WebApp"]
    col = db["Users"]

    # Function to get the next unique ID
    def get_next_id():
        last_user = col.find_one({}, sort=[("_id", -1)])  # Get last inserted user by _id
        return last_user["_id"] + 1 if last_user else 1  # If no users, start from 1

    # Streamlit UI
    container1 = st.container(border=True)
    container1.text("")
    container1.header("Login", divider="red")
    container1.text("")

    username = container1.text_input(":gray[Username Or Email]")
    password = container1.text_input(":gray[Password]", type="password")

    container2 = container1.container()
    container1.text("")
    columns = container1.columns((2.25, 1, 2))
    button_pressed = columns[1].button('Enter')

    container1.text("")
    if button_pressed:
        if not username or not password:
            container2.write("\t:red[Both fields required]")
        else:
            # Check if username already exists
            existing_user = col.find_one({"name": username})

            if existing_user:
                with st.spinner("Logging In..."):
                    time.sleep(2)
                    st.success(f"Welcome {username}!")
            else:
                user_id = get_next_id()  # Get the next available ID
                user = {"_id": user_id, "name": username, "password": password}
                col.insert_one(user)
                with st.spinner("Logging In..."):
                    time.sleep(3)
                    st.success(f"User '{username}' registered successfully!")
