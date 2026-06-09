cmake_minimum_required(VERSION 3.14)
project(FabForge)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

add_executable(fab_sim 
    src/cpp/simulation/Wafer.cpp
    src/cpp/simulation/FabSimulator.cpp
    src/cpp/simulation/main.cpp
    src/cpp/simulation/EquipmentStateMachine.cpp
    src/cpp/simulation/PLCEngine.cpp
)

target_include_directories(fab_sim PRIVATE src/cpp/simulation)

# PyBind11 bindings for Python integration
find_package(pybind11 REQUIRED)
pybind11_add_module(fabforge_cpp 
    src/cpp/simulation/bindings.cpp
    src/cpp/simulation/Wafer.cpp
    src/cpp/simulation/FabSimulator.cpp
    src/cpp/simulation/EquipmentStateMachine.cpp
    src/cpp/simulation/PLCEngine.cpp
)

target_include_directories(fabforge_cpp PRIVATE src/cpp/simulation)
