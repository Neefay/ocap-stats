import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import pandas as pd

import json

# Open the JSON file
with open('output/sample_output.json') as f:
    # Load the data
    data = json.load(f)

ai_stats = data["stats"]["ai"]

mission = data["mission"]

df = pd.DataFrame(ai_stats)

# Set a color palette
sns.set_palette('Set3')

fig, axs = plt.subplots(3, 4, figsize=(18, 20))

fig.suptitle(
    f"AI Eval - {mission['name']} ({mission['worldName']}) by {mission['author']} @ {mission['time']}", fontsize=27, y=0.9)

# Histogram for 'totalMovement'
sns.histplot(df['totalMovement'], bins=20, ax=axs[0, 0])
axs[0, 0].set_title('Total Movement (meters)')

# Histogram for 'shotsFired'
sns.histplot(df['shotsFired'], bins=20, ax=axs[1, 0])
axs[1, 0].set_title('Shots Fired')

# Histogram for 'hits'
sns.histplot(df['hits'], bins=20, ax=axs[2, 0])
axs[2, 0].set_title('Hits')

# Histogram for 'avgHitDistance'
sns.histplot(df['avgHitDistance'], bins=20, ax=axs[0, 1])
axs[0, 1].set_title('Average Hit Distance')

# Histogram for 'kills'
sns.histplot(df['kills'], bins=20, ax=axs[1, 1])
axs[1, 1].set_title('Kills')

# Histogram for 'accuracy'
sns.histplot(df['accuracy'], bins=20, ax=axs[2, 1])
axs[2, 1].set_title('Accuracy')

# Scatter plot to understand the relationship between accuracy and mobility
sns.scatterplot(x='accuracy', y='totalMovement', data=df, ax=axs[0, 2])
axs[0, 2].set_title('Accuracy and Mobility')

# Scatter plot to check if units with fewer shots are more accurate
sns.scatterplot(x='shotsFired', y='accuracy', data=df, ax=axs[1, 2])
axs[1, 2].set_title('Number of Shots Fired and Accuracy')

# Scatter plot of total movement vs average hit distance
sns.scatterplot(x='totalMovement', y='avgHitDistance', data=df, ax=axs[0, 3])
axs[0, 3].set_title('Total Movement vs Average Hit Distance')

# Scatter plot of shots fired vs kills
sns.scatterplot(x='shotsFired', y='kills', data=df, ax=axs[1, 3])
axs[1, 3].set_title('Shots Fired vs Kills')

# Scatter plot of accuracy vs average hit distance
sns.scatterplot(x='accuracy', y='avgHitDistance', data=df, ax=axs[2, 2])
axs[2, 2].set_title('Accuracy vs Average Hit Distance')


plt.subplots_adjust(left=0.1,
                    bottom=0.1,
                    right=0.9,
                    top=0.85,
                    wspace=0.5,
                    hspace=0.3)

plt.show()
