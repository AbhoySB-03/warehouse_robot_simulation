# warehouse_simulation

This package provides a ROS 2 simulation for wheel effort control of a warehouse mobile robot carrying a payload of unknown mass. It contains parameter estimation and state estimation problem.
## Prerequisites

Before running the simulation, make sure you have:

- ROS 2 installed
- `colcon` installed
- `git` installed
- A ROS 2 workspace created

## Setup

Replace `{ros2_workspace_dir}` with the path to your ROS 2 workspace. 

```bash
cd {ros2_workspace_dir}/src
git clone https://github.com/AbhoySB-03/warehouse_robot_simulation.git warehouse_simulation
cd {ros2_workspace_dir}
colcon build --packages-select warehouse_simulation
source install/setup.bash
```
If there isn't a ros2 workspace already, then create one as 
```bash
mkdir -p ~/ros2_ws/src
```
Use ~/ros2_ws instead of the {ros2_workspace_dir}

## Launch the simulation
The following command will launch the Gazebo simulation window along with access to all the ros2 topics and a random payload.
```bash
source {ros2_workspace_dir}/install/setup.bash
ros2 launch warehouse_simulation warehouse.launch.py
```
For a fixed payload of mass {m} kg, run the following command

```bash
source {ros2_workspace_dir}/install/setup.bash
ros2 launch warehouse_simulation warehouse_test.launch.py mass:={m}
```
Replace {m} with the value.
