import os
from ament_index_python.packages import get_package_prefix, get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    RegisterEventHandler,
    SetEnvironmentVariable,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_name = 'warehouse_simulation'

    pkg_share = get_package_share_directory(pkg_name)
    pkg_install_prefix = get_package_prefix(pkg_name)

    # ----------------------------------------------------
    # 0. Launch Arguments (Manual Payload Mass for Testing)
    # ----------------------------------------------------
    payload_mass = LaunchConfiguration('mass')

    declare_payload_mass = DeclareLaunchArgument(
        'mass',
        default_value='3.0',
        description='Attached payload mass (kg) for testing and calibration'
    )

    # ----------------------------------------------------
    # 1. Environment Variables for Models & Plugins
    # ----------------------------------------------------
    models_path = os.path.join(pkg_share, 'models')
    install_share = os.path.join(pkg_install_prefix, 'share')
    plugin_lib_path = os.path.join(pkg_install_prefix, 'lib', pkg_name)

    ign_ros2_control_prefix = get_package_prefix('ign_ros2_control')
    ign_ros2_control_lib = os.path.join(ign_ros2_control_prefix, 'lib')

    ign_resource_path = (
        f'{models_path}:{install_share}:'
        + os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')
    )
    gz_resource_path = (
        f'{models_path}:{install_share}:'
        + os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    )

    ign_plugin_path = (
        f'{plugin_lib_path}:{ign_ros2_control_lib}:'
        + os.environ.get('IGN_GAZEBO_SYSTEM_PLUGIN_PATH', '')
    )
    gz_plugin_path = (
        f'{plugin_lib_path}:{ign_ros2_control_lib}:'
        + os.environ.get('GZ_SIM_SYSTEM_PLUGIN_PATH', '')
    )

    set_ign_resource_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH', value=ign_resource_path
    )
    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH', value=gz_resource_path
    )
    set_ign_plugin_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_SYSTEM_PLUGIN_PATH', value=ign_plugin_path
    )
    set_gz_plugin_path = SetEnvironmentVariable(
        name='GZ_SIM_SYSTEM_PLUGIN_PATH', value=gz_plugin_path
    )

    # ----------------------------------------------------
    # 2. Geometry Scale & Coordinate Configurations
    # ----------------------------------------------------
    scale_chassis_x = 1.0
    scale_chassis_y = 1.0
    scale_chassis_z = 1.0
    wheel_radius_scale = 1.0
    wheel_width_scale = 1.0

    spawn_x = LaunchConfiguration('x')
    spawn_y = LaunchConfiguration('y')
    spawn_z = LaunchConfiguration('z')
    spawn_yaw = LaunchConfiguration('yaw')

    declare_x = DeclareLaunchArgument(
        'x', default_value='0.0', description='Spawn X position'
    )
    declare_y = DeclareLaunchArgument(
        'y', default_value='0.0', description='Spawn Y position'
    )
    declare_z = DeclareLaunchArgument(
        'z', default_value='0.2', description='Spawn Z position'
    )
    declare_yaw = DeclareLaunchArgument(
        'yaw', default_value='0.0', description='Spawn Yaw orientation'
    )

    # ----------------------------------------------------
    # 3. Process Xacro to Robot Description
    # ----------------------------------------------------
    xacro_file = PathJoinSubstitution(
        [pkg_share, 'models', 'mobile_robot', 'model.urdf.xacro']
    )

    robot_description_content = Command([
        FindExecutable(name='xacro'),
        ' ',
        xacro_file,
        ' ',
        'scale_chassis_x:=',
        str(scale_chassis_x),
        ' ',
        'scale_chassis_y:=',
        str(scale_chassis_y),
        ' ',
        'scale_chassis_z:=',
        str(scale_chassis_z),
        ' ',
        'wheel_radius_scale:=',
        str(wheel_radius_scale),
        ' ',
        'wheel_width_scale:=',
        str(wheel_width_scale),
        ' ',
        'payload_mass:=',
        payload_mass,
    ])

    robot_description = {
        'robot_description': ParameterValue(
            robot_description_content, value_type=str
        )
    }

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}],
    )

    # ----------------------------------------------------
    # 4. Launch Gazebo Fortress with main_world.sdf
    # ----------------------------------------------------
    world_file = PathJoinSubstitution([pkg_share, 'worlds', 'main_world.sdf'])

    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py',
            ])
        ),
        launch_arguments={'gz_args': ['-r ', world_file]}.items(),
    )

    # ----------------------------------------------------
    # 5. Spawn Model Node
    # ----------------------------------------------------
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-name',
            'mobile_robot',
            '-topic',
            'robot_description',
            '-x',
            spawn_x,
            '-y',
            spawn_y,
            '-z',
            spawn_z,
            '-Y',
            spawn_yaw,
        ],
    )

    # ----------------------------------------------------
    # 6. ros2_control Controller Spawners
    # ----------------------------------------------------
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager',
            '/controller_manager',
        ],
        output='screen',
    )

    wheel_effort_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'wheel_effort_controller',
            '--controller-manager',
            '/controller_manager',
        ],
        output='screen',
    )

    delayed_controllers = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[
                joint_state_broadcaster_spawner,
                wheel_effort_controller_spawner,
            ],
        )
    )

    # ----------------------------------------------------
    # 7. Parameter Bridges (Beacons, IMU & Ground Truth Odom)
    # ----------------------------------------------------
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        arguments=[
            # Beacon ranges
            '/beacon1/range@std_msgs/msg/Float64@ignition.msgs.Double',
            '/beacon2/range@std_msgs/msg/Float64@ignition.msgs.Double',
            '/beacon3/range@std_msgs/msg/Float64@ignition.msgs.Double',
            '/beacon4/range@std_msgs/msg/Float64@ignition.msgs.Double',
            # IMU topic
            '/imu@sensor_msgs/msg/Imu[ignition.msgs.IMU',
            # Ground-truth odometry and velocities
            '/true_pos_and_vel@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
        ],
        remappings=[
            ('/imu', '/imu/data'),
        ],
    )

    return LaunchDescription([
        # Arguments
        declare_payload_mass,
        declare_x,
        declare_y,
        declare_z,
        declare_yaw,
        # Environments
        set_ign_resource_path,
        set_gz_resource_path,
        set_ign_plugin_path,
        set_gz_plugin_path,
        # Nodes & Launches
        gazebo_sim,
        node_robot_state_publisher,
        spawn_entity,
        delayed_controllers,
        bridge_node,
    ])