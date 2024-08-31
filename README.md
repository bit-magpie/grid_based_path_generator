# Grid-based Path Generator

This code generates possible paths in the given 2D LiDAR map (.pgm format).
Genarated map can be used to find shortest path using A-star algorithm efficiently.
This method is faster than the path computation in SLAM package in ROS.

Paper: [https://doi.org/10.20965/jrm.2022.p0086](https://doi.org/10.20965/jrm.2022.p0086)

### Setup
```shell
pip install -r requirements.txt
python grid_generator.py
```
