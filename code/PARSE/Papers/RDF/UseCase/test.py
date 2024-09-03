import matplotlib.pyplot as plt

# Given data
research_problems = ["Optical Flow", "Modal Logic", "Image Captioning", "Blur Kernel", "SHAP Value",
                     "Action Recognition", "Persistence Diagrams", "Data Compression", "Scene Flow",
                     "Deep Learning", "Neural Network", "Semantic Segmentation", "Carrier Synchronization",
                     "Artificial Intelligence", "Cloud Services Evaluation"]

July_20x2 = [230, 231, 144, 101, 168, 82, 91, 85, 81, 72, 71, 64, 62, 61, 52]
January_20x3 = [260, 258, 180, 173, 171, 124, 120, 105, 100, 90, 87, 80, 75, 75, 65]

# Create a figure and a set of subplots
fig, ax = plt.subplots()

# Plot data
for i in range(len(research_problems)):
    ax.plot(["July 20x2", "January 20x3"], [July_20x2[i], January_20x3[i]], label=research_problems[i])

# Add title and labels
ax.set_title('Research Problems Trend Analysis')
ax.set_xlabel('Time')
ax.set_ylabel('Count')

# Add a legend
ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))

# Display the plot
plt.tight_layout()
plt.show()

