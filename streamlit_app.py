'''
# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests 
import pandas as pd


# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)
import streamlit as st

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

cnx= st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#Convert the Snowpark Dataframe to pandas Dataframe so we can use the LOC Function 
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
    )

if ingredients_list:
    #st.write(ingredients_list)
    #st.text(ingredients_list)
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")  
        sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)
        
        my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','"""+name_on_order+"""')"""
    #st.write(my_insert_stmt)
    #st.stop()

  
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered Betty Jean!,', icon="✅")


 
#smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")  
#sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)
'''

# -*- coding: utf-8 -*-
# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
 
# App header
st.title("🧋 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")
 
# Name entry
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be: ", name_on_order)
 
# Snowflake session (works in Snowsight / Streamlit in Snowflake)
session = get_active_session()
 
# 1) Pull both columns we need (FRUIT_NAME for UI, SEARCH_ON for API/search)
my_dataframe = (
    session.table("smoothies.public.fruit_options")
           .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)
 
# 2) Convert Snowpark -> pandas so we can use .loc / .iloc as per the course
pd_df = my_dataframe.to_pandas()
 
# 🔎 Show the two columns in the UI so you can see "where is the column"
with st.expander("Show Fruit Options (FRUIT_NAME & SEARCH_ON)"):
    st.dataframe(pd_df, use_container_width=True)
 
# 3) Multiselect displays FRUIT_NAME
fruit_names = pd_df["FRUIT_NAME"].tolist()
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_names,
    max_selections=5,
)
 
if ingredients_list:
    # a) Display string (what user sees)
    display_string = " ".join(ingredients_list).strip()
 
    st.caption("**Chosen Fruit Names (display):**")
    st.write(display_string)
 
    # b) For each chosen fruit, look up SEARCH_ON using the 'strange-looking' .loc/.iloc pattern
    search_on_values = []
    with st.expander("Per-fruit SEARCH_ON lookups (via pandas .loc/.iloc)"):
        for fruit_chosen in ingredients_list:
            # 👉 This matches the course snippet:
            search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]
            search_on_values.append(search_on)
            st.write(f"The search value for **{fruit_chosen}** is **{search_on}**.")
 
    # c) Internal string for API/search (space-separated SEARCH_ON tokens)
    search_on_string = " ".join(search_on_values).strip()
 
    st.caption("**Search-On Tokens (used for API/search logic):**")
    st.write(search_on_string)
 
    # d) Basic escaping for SQL string literals
    safe_ingredients = search_on_string.replace("'", "''")
    safe_name = (name_on_order or "").replace("'", "''")
 
    # e) Insert TWO columns: INGREDIENTS (the SEARCH_ON tokens) and NAME_ON_ORDER
    insert_sql = f"""
        INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{safe_ingredients}', '{safe_name}')
    """
 
    st.code(insert_sql, language="sql")
 
    # Submit button
    if st.button("Submit Order"):
        if not safe_name.strip():
            st.error("Please enter a name for the smoothie before submitting.")
        else:
            try:
                session.sql(insert_sql).collect()
                st.success("Your Smoothie is ordered! ✅")
            except Exception as e:
                st.error(f"Insert failed: {e}")
