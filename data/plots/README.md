# Default destination for plot data

The current state of a plot can be downloaded as a CSV file. By default, downloaded data will be named as `<timestamp>_<title>_ax_<i>.csv` and will be directed to this directory. The user can override both the filename and the destination from the app.

**NOTE:** for statistical plots, at least for the swarm plot, CSV is replaced by a `pickle` binary of the current plot state that can be reloaded in a Jupyter notebook.

### Example

```
default_path = "/home/jovyan/apps/aurora/data/plots"

plot title = "V & I vs. t"

default_filenames:
    V-axis = "231016-134231_V_&_I_vs._t_ax_1.csv
    I-axis = "231016-134231_V_&_I_vs._t_ax_2.csv
```
