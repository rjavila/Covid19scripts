# Covid-19 Plots

## Grid plots
Generate figures in a grid format with bar plots of new daily cases or deaths
for the following regions:
* USA (all 50 states)
* global (hard-coded list of countries)
* Latin America countries
* EU total vs USA total
* Worst 9 USA states
* Worst 9 countries
"Worst" is defined as the regions with highest number of most recent daily cases. 

To create these plots:

```
python grid_plots.py
```

to create all plots. Or to specify only certain plots:

```
python grid_plots.py --regions worst_world
```

An example plot is found below.
![Alt text](examples/worst_global_cases.pdf?raw=true "Title")

## Bar plot for a single state/country
Genereate a bar plot for a single state or country:

```
python plot_by_region.py Florida
```

![Alt text](examples/Florida_new_cases.png?raw=true "Title")

## Overlaid plots
Generate 2 different types of plots for a hard-coded selection of states:
* Case/death numbers vs date
* Case/death numbers vs days since 100 cases/deaths 
Both types of plots are also created with log Y scales and per capita case/death
numbers, creating a total of 8 plots.

![Alt text](examples/usa_cases_date.png?raw=true "Title")
