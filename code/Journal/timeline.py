#!/usr/bin/env python
"""
PARSE-DDM Integration Journal Paper Timeline
April 2024 - June 2024 (3 months)

This timeline outlines the schedule for completing the journal paper on integrating
PARSE (automated knowledge graph construction) with DDM (Deep Document Model ontology)
across Computer Science and Astronomy domains.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

timeline = {
    # PHASE 1: DATA PREPARATION (April 2024)
    "Phase 1 - Data Preparation": {
        "duration": "April 1 - April 30, 2024",
        "milestones": [
            {
                "name": "Computer Science Dataset Processing",
                "deadline": "April 15, 2024",
                "tasks": [
                    "Finalize CS papers selection",
                    "Run complete PARSE pipeline on CS papers",
                    "Generate DDM ontology from CS data",
                    "Validate and refine CS knowledge graph",
                ]
            },
            {
                "name": "Astronomy Dataset Processing",
                "deadline": "April 30, 2024",
                "tasks": [
                    "Obtain TPD astronomy data",
                    "Run complete PARSE pipeline on astronomy papers",
                    "Generate DDM ontology from astronomy data",
                    "Validate and refine astronomy knowledge graph",
                ]
            }
        ],
        "deliverables": [
            "Complete knowledge graphs for both CS and Astronomy domains",
            "Documentation of data processing methods",
            "Initial evaluation metrics of KG quality"
        ]
    },
    
    # PHASE 2: EXPERIMENTATION (May 2024)
    "Phase 2 - Experimentation": {
        "duration": "May 1 - May 31, 2024",
        "milestones": [
            {
                "name": "LLM Integration for SPARQL Query Generation",
                "deadline": "May 15, 2024",
                "tasks": [
                    "Implement LLM-based approach for SPARQL query construction",
                    "Test query precision and recall metrics",
                    "Optimize LLM prompting for query accuracy",
                    "Compare performance across domains"
                ]
            },
            {
                "name": "Cross-Domain Knowledge Integration",
                "deadline": "May 31, 2024",
                "tasks": [
                    "Design experiments to evaluate cross-domain capabilities",
                    "Evaluate knowledge transfer between CS and Astronomy domains",
                    "Perform ablation studies on different components",
                    "Compile comprehensive experimental results",
                    "Prepare visualizations and tables for paper"
                ]
            }
        ],
        "deliverables": [
            "Complete experimental results and analysis",
            "Comparative evaluation metrics",
            "Visualizations of knowledge graph structures",
            "Technical limitations and future improvements document"
        ]
    },
    
    # PHASE 3: PAPER WRITING (June 2024)
    "Phase 3 - Paper Writing": {
        "duration": "June 1 - June 30, 2024",
        "milestones": [
            {
                "name": "Initial Draft Completion",
                "deadline": "June 15, 2024",
                "tasks": [
                    "Complete introduction and related work sections",
                    "Write methodology section based on Phases 1 and 2",
                    "Draft results and discussion sections",
                    "Prepare initial figures and tables"
                ]
            },
            {
                "name": "Final Paper Submission",
                "deadline": "June 30, 2024",
                "tasks": [
                    "Revise draft based on co-author feedback",
                    "Finalize all figures and tables",
                    "Complete conclusion and future work sections",
                    "Ensure all references are correctly formatted",
                    "Prepare submission package"
                ]
            }
        ],
        "deliverables": [
            "Complete journal paper manuscript",
            "All supporting materials and supplementary information",
            "Submission to selected journal"
        ]
    }
}

# Summary of key dates
key_dates = {
    "Project Start": "April 1, 2024",
    "Phase 1 Completion": "April 30, 2024",
    "Phase 2 Completion": "May 31, 2024",
    "Initial Draft": "June 15, 2024",
    "Final Submission": "June 30, 2024"
}

def visualize_timeline():
    """Create a Gantt chart visualization of the timeline."""
    # Create figure and axis with larger figure size and adjusted margins
    plt.figure(figsize=(15, 10))  # Increase figure width
    ax = plt.subplot(111)
    
    # Define the date range
    months = ['April', 'May', 'June']
    weeks = []
    for month in months:
        for week in range(1, 5):
            weeks.append(f"{month}\nW{week}")  # Add newline between month and week
    
    # Set up the x-axis
    x_pos = np.arange(len(weeks))
    ax.set_xlim(-0.5, len(weeks) - 0.5)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(weeks, rotation=0, ha='center')  # Remove rotation, center align
    
    # Colors for each phase
    colors = {
        "Phase 1 - Data Preparation": "#4285F4",  # Google Blue
        "Phase 2 - Experimentation": "#FBBC05",   # Google Yellow
        "Phase 3 - Paper Writing": "#34A853"      # Google Green
    }
    
    # Increase spacing between items
    y_spacing = 2  # Increase vertical spacing between items
    y_pos = 0
    y_ticks = []
    y_labels = []
    
    # Add phases and milestones
    min_y_pos = 0  # Track the minimum y position
    
    # Add phases and milestones
    for phase_idx, (phase_name, phase_details) in enumerate(timeline.items()):
        # Determine phase position
        if phase_idx == 0:  # Phase 1 - April
            phase_start_idx = 0
            phase_end_idx = 3
        elif phase_idx == 1:  # Phase 2 - May
            phase_start_idx = 4
            phase_end_idx = 7
        else:  # Phase 3 - June
            phase_start_idx = 8
            phase_end_idx = 11
        
        # Plot phase bar
        ax.barh(y_pos, phase_end_idx - phase_start_idx + 1, left=phase_start_idx, 
                height=0.6, color=colors[phase_name], alpha=0.6)
        
        # Add phase label with more left margin
        ax.text(-2.0, y_pos, phase_name, 
                ha='right', va='center', fontweight='bold')
        
        y_ticks.append(y_pos)
        y_labels.append("")
        
        # Add milestones with increased spacing
        for milestone_idx, milestone in enumerate(phase_details["milestones"]):
            y_pos -= y_spacing  # Increase space between milestones
            min_y_pos = min(min_y_pos, y_pos)  # Update minimum y position
            
            # Determine milestone position
            if phase_idx == 0:  # Phase 1
                if milestone_idx == 0:  # CS Dataset - first half of April
                    milestone_start_idx = 0
                    milestone_end_idx = 1
                else:  # Astronomy Dataset - second half of April
                    milestone_start_idx = 2
                    milestone_end_idx = 3
            elif phase_idx == 1:  # Phase 2
                if milestone_idx == 0:  # LLM Integration - first half of May
                    milestone_start_idx = 4
                    milestone_end_idx = 5
                else:  # Cross-Domain - second half of May
                    milestone_start_idx = 6
                    milestone_end_idx = 7
            else:  # Phase 3
                if milestone_idx == 0:  # Initial Draft - first half of June
                    milestone_start_idx = 8
                    milestone_end_idx = 9
                else:  # Final Paper - second half of June
                    milestone_start_idx = 10
                    milestone_end_idx = 11
            
            # Plot milestone bar
            ax.barh(y_pos, milestone_end_idx - milestone_start_idx + 1, left=milestone_start_idx, 
                    height=0.4, color=colors[phase_name], alpha=0.9)
            
            # Add milestone label with more left margin
            ax.text(-2.0, y_pos, milestone["name"], 
                    ha='right', va='center')
            
            # Add milestone end marker
            ax.scatter(milestone_end_idx, y_pos, s=80, color=colors[phase_name], 
                       marker='D', edgecolors='black', zorder=5)
            
            # Add milestone tasks as annotations with adjusted position
            task_y_offset = 0.3  # Increase task spacing
            for task_idx, task in enumerate(milestone["tasks"]):
                if task_idx < 2:  # Only show first 2 tasks for space
                    task_y = y_pos - task_y_offset * (task_idx + 1)
                    ax.text(milestone_start_idx + 0.1, task_y, task, 
                            fontsize=8, alpha=0.7, ha='left', va='top')
            
            y_ticks.append(y_pos)
            y_labels.append("")
        
        y_pos -= y_spacing  # Add extra space between phases
    
    # Add key dates as vertical lines with adjusted position
    key_weeks = {
        "Phase 1\nCompletion": 3,  # End of April
        "Phase 2\nCompletion": 7,  # End of May
        "Initial\nDraft": 9,       # Mid-June
        "Final\nSubmission": 11    # End of June
    }
    
    # Calculate the bottom position for milestone labels - closer to x-axis
    bottom_pos = min_y_pos - 1  # Reduce the gap
    
    # Set y-axis limit to include the bottom labels
    ax.set_ylim(bottom_pos - 1, 1)  # Add some padding at top and bottom
    
    for event, week_idx in key_weeks.items():
        ax.axvline(x=week_idx, color='black', linestyle='--', alpha=0.7, zorder=0)
        ax.text(week_idx, bottom_pos, event, rotation=0, ha='center', va='top', alpha=0.7)
    
    # Set y-axis properties
    ax.set_yticks([])
    ax.grid(True, axis='x', alpha=0.3)
    
    # Adjust plot margins to accommodate longer labels
    plt.subplots_adjust(left=0.3, bottom=0.15)  # Reduce bottom margin
    
    # Set title and labels
    ax.set_title('PARSE-DDM Integration Journal Paper Timeline (April-June 2024)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Remove y-axis line
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    # Add today's marker 
    today_week = 1  # Second week of April
    ax.axvline(x=today_week, color='red', linestyle='-', linewidth=2, zorder=10)
    ax.text(today_week, bottom_pos, 'Today', rotation=0, color='red', 
            ha='center', va='top', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('PARSE_DDM_Timeline.png', dpi=300, bbox_inches='tight')
    print("Timeline visualization saved as 'PARSE_DDM_Timeline.png'")
    plt.show()

if __name__ == "__main__":
    print("PARSE-DDM Integration Journal Timeline (3 months)")
    print("=================================================")
    for phase, details in timeline.items():
        print(f"\n{phase}: {details['duration']}")
        print("-" * 50)
        
        for milestone in details['milestones']:
            print(f"  • {milestone['name']} (Due: {milestone['deadline']})")
            for task in milestone['tasks']:
                print(f"    - {task}")
        
        print("\n  Deliverables:")
        for deliverable in details['deliverables']:
            print(f"    - {deliverable}")
    
    print("\n\nKey Dates Summary")
    print("================")
    for event, date in key_dates.items():
        print(f"{event}: {date}")
    
    # Create visualization
    print("\nGenerating timeline visualization...")
    try:
        visualize_timeline()
    except Exception as e:
        print(f"Error generating visualization: {e}")
        print("Make sure matplotlib is installed: pip install matplotlib")
