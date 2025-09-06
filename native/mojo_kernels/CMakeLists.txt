cmake_minimum_required(VERSION 3.18)
project(mojo_kernels LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module Development)
find_package(pybind11 REQUIRED)

pybind11_add_module(hakgal_mojo_kernels src/mojo_kernels.cpp)
set_target_properties(hakgal_mojo_kernels PROPERTIES OUTPUT_NAME "mojo_kernels")

target_include_directories(hakgal_mojo_kernels PRIVATE ${Python3_INCLUDE_DIRS})
target_link_libraries(hakgal_mojo_kernels PRIVATE pybind11::module)

if (MSVC)
  target_compile_options(hakgal_mojo_kernels PRIVATE /O2 /Zc:__cplusplus)
else()
  target_compile_options(hakgal_mojo_kernels PRIVATE -O3)
endif()

cmake_minimum_required(VERSION 3.18)
project(mojo_kernels LANGUAGES CXX)

# Optionen
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Python sauber finden (Interpreter + Development)
cmake_policy(SET CMP0148 NEW)
set(PYBIND11_FINDPYTHON ON)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# pybind11 finden (via pip install pybind11[global] oder systemweit)
find_package(pybind11 CONFIG QUIET)
if (NOT pybind11_FOUND)
  message(FATAL_ERROR "pybind11 not found. Please install with: pip install pybind11[global]")
endif()

pybind11_add_module(mojo_kernels src/mojo_kernels.cpp)

# Windows: /O2
if (MSVC)
  target_compile_options(mojo_kernels PRIVATE /O2)
else()
  target_compile_options(mojo_kernels PRIVATE -O3 -fPIC)
endif()
