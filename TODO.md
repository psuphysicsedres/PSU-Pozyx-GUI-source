# Pozyx To Do List

## Short Term
- Look through code to find out why 3D sometimes won't run. Thinking first velocity empty or zero
- DONE: Change "center" to "earth" and "outer" to "observed" in graphing 2D
- DONE: Plot points and lines rather than just lines
  - Ask whether want black points and colored lines when change color
- Plot the (0,0) Earth tag under the Earth Center transform
  - Figuring out how to plot multiple data sets on same graph
- MYSTERIOUSLY RESOLVED: Figure out why when Angular Earth Center transform on, and one tag accurate and other invalid, plots angle 0
- DONE: Number of points option on graphing 2D not working
- DONE: Pathing with new script doesn't work
  - FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Users\\physicslab-admin/Documents/PSUPozyx/Producer File/producer_file.csv'

## Medium Term
- Research and test whether Ptolemaic Model (wrong model) gives same retrograde data
- We commented out a line 117 os.remove(producer_name) in 1D Ranging file to fix pathing issue. Figure out how to better fix this?
- When closing 1D Ranging script dialogue box, get thread exceptions (when wrong Device ID name inputted in GUI)
  - Exception in thread "JavaFX Application Thread" java.lang.NullPointerException

## Long Term
- Writing up math of coordinate transforms
- Adding -pi to pi ticks on the Angle transform
- Linex and MacOSX pathing differences
