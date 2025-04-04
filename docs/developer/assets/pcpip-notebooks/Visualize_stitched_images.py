#!/usr/bin/env python
# coding: utf-8

# In[1]:


import skimage
import numpy as np
import os
import matplotlib.pyplot as plt


# # Quadrant stitches

# In[4]:


# Download images to root
root = "/Users/eweisbar/Desktop/images_corrected_stitched_10X/"

wells = os.listdir(root)
count_dict = {2: [0, 0], 0: [0, 1], 3: [1, 0], 1: [1, 1]}

wells = [x for x in wells if os.path.isdir(os.path.join(root, x))]
print(f"Inspecting {len(wells)} wells")
for well in wells:
    print(well)
    ims = os.listdir(os.path.join(root, well))
    fig, axs = plt.subplots(nrows=2, ncols=2, layout="compressed")
    for count, im in enumerate(ims):
        if "BottomLeft" in im:
            loc = [1, 0]
        if "BottomRight" in im:
            loc = [1, 1]
        if "TopLeft" in im:
            loc = [0, 0]
        if "TopRight" in im:
            loc = [0, 1]
        im = skimage.io.imread(os.path.join(root, well, im))
        # axs[count_dict[count]] = skimage.io.imshow(np.sqrt(im),cmap="gray")
        axs[loc[0], loc[1]].imshow(np.sqrt(im), cmap="gray")
        axs[loc[0], loc[1]].set_xticks([])
        axs[loc[0], loc[1]].set_yticks([])
    plt.tight_layout()
    plt.show()


# In[ ]:
