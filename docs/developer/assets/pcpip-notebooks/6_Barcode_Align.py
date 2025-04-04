#!/usr/bin/env python
# coding: utf-8

# In[47]:


import os
import pandas as pd
import seaborn as sns
import datetime

# get_ipython().run_line_magic("matplotlib", "inline")


# In[48]:


# Set variables
numcycles = 10
imperwell = 1025
row_widths = [
    5,
    11,
    17,
    19,
    23,
    25,
    27,
    29,
    29,
    31,
    33,
    33,
    33,
    35,
    35,
    35,
    37,
    37,
    37,
    37,
    37,
    35,
    35,
    35,
    33,
    33,
    33,
    31,
    29,
    29,
    27,
    25,
    23,
    19,
    17,
    11,
    5,
]


# In[49]:


def merge_csvs(csvfolder, filename, column_list=None, filter_string=None):
    df_dict = {}
    count = 0
    folderlist = os.listdir(csvfolder)
    if filter_string:
        folderlist = [x for x in folderlist if filter_string in x]
    print(count, datetime.datetime.ctime(datetime.datetime.now()))
    for eachfolder in folderlist:
        if os.path.isfile(os.path.join(csvfolder, eachfolder, filename)):
            if not column_list:
                df_dict[eachfolder] = pd.read_csv(
                    os.path.join(csvfolder, eachfolder, filename), index_col=False
                )
            else:
                df_dict[eachfolder] = pd.read_csv(
                    os.path.join(csvfolder, eachfolder, filename),
                    index_col=False,
                    usecols=column_list,
                )
            count += 1
            if count % 500 == 0:
                print(count, datetime.datetime.ctime(datetime.datetime.now()))
    print(count, datetime.datetime.ctime(datetime.datetime.now()))
    df_merged = pd.concat(df_dict, ignore_index=True)
    print("done concatenating at", datetime.datetime.ctime(datetime.datetime.now()))

    return df_merged


# In[50]:


max_width = max(row_widths)
pos_dict = {}
count = 0
# creates dict of (xpos,ypos) = imnumber
for row in range(len(row_widths)):
    row_width = row_widths[row]
    left_pos = int((max_width - row_width) / 2)
    for col in range(row_width):
        if row % 2 == 0:
            pos_dict[(int(left_pos + col), row)] = count
            count += 1
        else:
            right_pos = left_pos + row_width - 1
            pos_dict[(int(right_pos - col), row)] = count
            count += 1
# make dict into df
pos_df = (
    pd.DataFrame.from_dict(pos_dict, orient="index")
    .reset_index()
    .rename(columns={"index": "loc", 0: "Metadata_Site"})
)
pos_df[["x_loc", "y_loc"]] = pd.DataFrame(pos_df["loc"].tolist(), index=pos_df.index)


# # Check Alignment - Plate45

# In[ ]:


csvfolder = "/LOCATION/images_aligned/barcoding"

shift_list = []
corr_list = []
for cycle in range(1, numcycles + 1):
    if cycle != 1:
        shift_list.append(f"Align_Xshift_Cycle{cycle:02d}_DAPI")
        shift_list.append(f"Align_Yshift_Cycle{cycle:02d}_DAPI")
    for cycle2 in range(cycle + 1, numcycles + 1):
        corr_list.append(
            f"Correlation_Correlation_Cycle{cycle:02d}_DAPI_Cycle{cycle2:02d}_DAPI"
        )
id_list = ["Metadata_Well", "Metadata_Plate", "Metadata_Site"]
column_list = id_list + shift_list + corr_list

df_image = merge_csvs(
    csvfolder, "BarcodingApplication_Image.csv", column_list, filter_string="Plate45"
)


# In[52]:


df_shift = df_image[shift_list + id_list]
df_shift = pd.melt(df_shift, id_vars=id_list)
df_corr = df_image[corr_list + id_list]
df_corr = pd.melt(df_corr, id_vars=id_list)
df_corr_crop = df_image[[x for x in corr_list if "Correlation_Cycle01" in x] + id_list]
df_corr_crop = pd.melt(df_corr_crop, id_vars=id_list)


# In[53]:


# Pixels shifted to align each cycle to Cycle01
sns.catplot(
    data=df_shift,
    x="value",
    y="variable",
    orient="h",
    col="Metadata_Well",
    row="Metadata_Plate",
)


# In[54]:


# Pixels shifted to align each cycle to Cycle01 - x axis limits
g = sns.catplot(
    data=df_shift,
    x="value",
    y="variable",
    orient="h",
    col="Metadata_Well",
    row="Metadata_Plate",
)
g.set(xlim=(-200, 200))


# In[55]:


value = 50
temp = (
    df_shift.loc[df_shift["value"] > value]
    .groupby(["Metadata_Plate", "Metadata_Well", "Metadata_Site"])
    .count()
    .reset_index()
)
for well in temp["Metadata_Well"].unique():
    print(
        f"{well} has {len(temp.loc[temp['Metadata_Well'] == well])} site with shift more than {value} (out of {imperwell})"
    )


# In[56]:


# plot size of shift by location, ignoring shifts >200
temp = (
    df_shift.loc[df_shift["value"] > value]
    .groupby(["Metadata_Plate", "Metadata_Well", "Metadata_Site"])
    .max()
    .reset_index()
    .merge(pos_df)
)
temp = temp.loc[temp["value"] < 200]
g = sns.relplot(
    data=temp,
    x="x_loc",
    y="y_loc",
    hue="value",  # hue_norm=(0,200),
    col="Metadata_Well",
    col_wrap=3,
    palette="viridis",
    marker="s",
    s=150,
)
print(g._legend_data)
# display(g)


# In[57]:


# DAPI correlations after alignment (using "Correlation")
# Need all points to be better than red line
g = sns.catplot(
    data=df_corr,
    x="value",
    y="variable",
    orient="h",
    col="Metadata_Well",
    row="Metadata_Plate",
)
g.refline(x=0.9, color="red")
g.set(xlim=(0, None))


# In[58]:


# DAPI correlations after alignment (using "Correlation") - only correlations to Cycle01
# Need all points to be better than red line
g = sns.catplot(
    data=df_corr_crop,
    x="value",
    y="variable",
    orient="h",
    col="Metadata_Well",
    row="Metadata_Plate",
)
g.refline(x=0.9, color="red")
g.set(xlim=(0, None))


# In[59]:


print("For correlations to Cycle01")
print(
    f"{len(df_corr_crop.groupby(['Metadata_Plate', 'Metadata_Well', 'Metadata_Site']))} total sites"
)
print(
    f"{len(df_corr_crop.loc[df_corr_crop['value'] < 0.9])} sites with correlation <.9"
)
print(
    f"{len(df_corr_crop.loc[df_corr_crop['value'] < 0.8])} sites with correlation <.8"
)
# Print Awful alignment scores after alignment
df_corr_crop.sort_values(by="value").head(20)


# In[60]:


# Print mediocre alignment score after alignment
df_corr_crop.loc[df_corr_crop["value"] < 0.5].sort_values(
    by="value", ascending=False
).head(20)


# In[61]:


# Print huge pixel shifts
print(
    f"{len(df_shift.loc[df_shift['value'] > 100])} images shifted with huge pixel shifts"
)

df_shift.loc[df_shift["value"] > 100].sort_values(by="value", ascending=False).head(20)


# In[ ]:
