cmake_minimum_required(VERSION 3.20.0)

include(FindPythonInterp)

add_executable(5FX-IO 5FX-IO.cpp)
# add_executable(Test-5FX-IO 5FX-IO.cpp tests/Test-5FX-IO.cpp)
# target_link_libraries(Test-5FX-IO PRIVATE nlohmann_json::nlohmann_json)
# target_precompile_headers(TestCtrl PRIVATE ${HEADERS} ${STD_PERCOMPILED_HEADERS})
add_test(
    NAME Test-5FX-IO 
    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/Test-5FX-IO.py
    WORKING_DIRECTORY ${EXECUTABLE_OUTPUT_PATH})