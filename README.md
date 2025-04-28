# Disaster Response Visualization Redesign

This project presents an interactive redesign of a static disaster response asset tracking visualization. Originally part of the INFOSCI 301 course at Duke Kunshan University, it utilizes Python (Folium, Pandas) to transform a dense, static map into an interactive tool for improved situational awareness.

## Project Overview

- **Title:** Interactive Disaster Response Asset Tracker Redesign
- **Author:** Loe
- **Course:** INFOSCI 301-001-LEC (1066): Data Visualization and Information Aesthetics
- **Instructor**: Prof. Luyao Zhang
- **Institution:** Duke Kunshan University

## Objectives

- **Critique:** Analyze an existing static disaster response visualization (Novetta Ageon ISR display) based on established visualization principles.
- **Redesign:** Develop an interactive map-based visualization using Python and Folium to address the original's limitations.
- **Improve Clarity:** Reduce visual clutter and improve the distinguishability of individual assets through techniques like marker clustering.
- **Enhance Insight:** Incorporate interactivity and temporal controls (time slider) to allow exploration of asset movements and patterns over time.
- **Apply Theory:** Ground the redesign in principles from visualization literature and relevant research.

## Redesign Goals (vs. Original Static Display)

This project improves upon the original static Novetta Ageon ISR display by:

- Adding **full interactivity:** Zoom, pan, hover tooltips (quick ID), and click popups (detailed info).
- Implementing **Marker Clustering:** Dynamically grouping markers at higher zoom levels to manage data density and reduce clutter.
- Providing an **Explicit Legend:** Clearly defining color-coding (affiliation) and icon symbology (asset type).
- Incorporating **Temporal Analysis:** Adding a time slider to filter data by time and observe dynamic movement patterns.
- Enhancing **Readability:** Using a cleaner base map (`CartoDB positron`) and clearer information presentation compared to the original's text-heavy sidebar and dense overlay.
- Ensuring **Better Usability:** Following modern web-mapping conventions for a more intuitive user experience.
<!-- 
## Result Preview

*(Instruction: Add a screenshot of your final interactive Folium map here)*
```markdown
![Redesigned Map Preview](images/redesigned_map_preview.png)
```
*(Make sure you have an `images` folder in your repo or adjust the path)* -->

## Dataset

The visualization uses **simulated data** (`simulated_disaster_response_data.csv`) as the original dataset from the Novetta system was not publicly available.

- **Simulation Approach:**
    - Defined a geographic bounding box approximating Hampton Roads, VA.
    - Generated tracks for multiple assets (Vessels, Vehicles, Personnel) over a defined time period.
    *   Simulated movement often involved random walks within the area.
    *   Included timestamps, Asset IDs, Asset Types, Latitude, Longitude, and Affiliation (Friend, Unknown, Neutral).
- **Details:** Further details on the simulation methodology can be found within the comments of the Python script (`your_script_name.py`).

## Theoretical Grounding

The redesign process was informed by core visualization principles:

- **Clutter Reduction & Data Density** (Tufte): Directly addressed the original's high density and visual clutter through marker clustering and clearer presentation.
- **Interaction Frameworks** (Munzner): Guided the incorporation of interactive features like zoom, pan, filter (via time slider), and details-on-demand (tooltips/popups).
- **Visual Encoding:** Employed distinct colors and icons with an explicit legend for effective categorical differentiation (affiliation, asset type).

## Research Inspiration

Insights were drawn from the research paper:
**"A Visual Analytics Framework for the Detection of Anomalous Call Stack Trees in High Performance Computing Applications"** by Xie, Cong, Wei Xu, and Klaus Mueller (IEEE TVCG, Vol. 25, No. 1, Jan. 2019).

This paper inspired the redesign by highlighting:

- **Handling Data Density:** While the methods differ (scatter plots vs. map clustering), the principle of managing visual density in large datasets was key.
- **Importance of Context:** Emphasized the need for context (like time in disaster response), reinforcing the value of the time slider feature.
- **Value of Multiple Coordinated Views / Interaction:** Underscored the power of combining computational analysis (even simple filtering) with interactive visualization for exploration and insight generation.

## Getting started

Install required Python packages in requirements.txt

```bash
pip install -r requirements.txt
```

Execute the Python script to generate the visualization HTML

```bash
python3 src/visualization.py
```

Note: A pre-compiled HTML is included in `static` folder.

## SDG Goal Contribution

This project contributes to [SDG 11.5](https://sdgs.un.org/goals/goal11#targets_and_indicators)

<p align="center">
<img src="https://www.un.org/sustainabledevelopment/wp-content/uploads/2019/08/E-Inverted-Icons_WEB-11-1024x1024.png" alt="SDG Logo" width="150"/>
</p>

## Acknowledgement

This project has benefitted from the conversations at the Digital Technology for Sustainability
Symposium at Duke Kunshan University on April 18. We especially thank Prof. Ming-Chun Huang 
for their insights that helped improve the work, and the conference
organizers Profs. Luyao Zhang for making the symposium happen.

Again, special thanks to Prof. Ming-Chun Huang, Prof. Luyao Zhang.

## Disclaimer

Course project for INFOSCI 301 – Data Visualization and Information Aesthetics, instructed by Prof. Luyao Zhang at Duke Kunshan University, Spring 2025.


## License

This project is licensed under the MIT License - see the LICENSE file for details.
