cmake_minimum_required(VERSION 3.8)
project(warehouse_simulation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# -----------------------------------------------------------------------------
# Dependencies
# -----------------------------------------------------------------------------
find_package(ament_cmake REQUIRED)

find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nlohmann_json REQUIRED)
find_package(ignition-gazebo6 REQUIRED)
find_package(ignition-math6 REQUIRED)
find_package(ignition-msgs8 REQUIRED)
find_package(ignition-transport11 REQUIRED)
find_package(ignition-plugin1 REQUIRED)
find_package(sdformat12 REQUIRED)

# -----------------------------------------------------------------------------
# Build Plugin
# -----------------------------------------------------------------------------
# add_library(RangeBeaconPlugin SHARED
#   src/RangeBeaconPlugin.cc
# )

# target_compile_definitions(RangeBeaconPlugin PRIVATE RADAR_IGNITION_API=1 BEACON_IGNITION_API=1)

# target_link_libraries(RangeBeaconPlugin PRIVATE
#   ignition-gazebo6::core
#   ignition-math6::ignition-math6
#   ignition-msgs8::ignition-msgs8
#   ignition-transport11::ignition-transport11
#   ignition-plugin1::ignition-plugin1
#   sdformat12::sdformat12
# )

# -----------------------------------------------------------------------------
# Install
# -----------------------------------------------------------------------------
#install(TARGETS RangeBeaconPlugin
#  LIBRARY DESTINATION lib/${PROJECT_NAME}
#)

install(DIRECTORY
  launch
  worlds
  models
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY
lib/${PROJECT_NAME}

DESTINATION lib)

# -----------------------------------------------------------------------------
# Testing & Export
# -----------------------------------------------------------------------------
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()