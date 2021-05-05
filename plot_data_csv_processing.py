#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


df = pd.read_csv('support_files/plot_details.csv')


# In[28]:


df[df['UID'] == 'SPP_1_A'].dropna(axis='columns')


# In[19]:


df


# In[ ]:




