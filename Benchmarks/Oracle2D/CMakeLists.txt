cmake_minimum_required(VERSION 3.20)

project(GFXPhysicsBox2DOracle LANGUAGES C)

include(FetchContent)
include(CTest)

set(BOX2D_SAMPLES OFF CACHE BOOL "" FORCE)
set(BOX2D_UNIT_TESTS OFF CACHE BOOL "" FORCE)
set(BOX2D_BENCHMARKS OFF CACHE BOOL "" FORCE)
set(BOX2D_DOCS OFF CACHE BOOL "" FORCE)

# Box2D v3.1.1. The immutable commit is intentional: a moving tag is not an
# acceptable differential oracle.
FetchContent_Declare(
    box2d
    GIT_REPOSITORY https://github.com/erincatto/box2d.git
    GIT_TAG 8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3
    GIT_SHALLOW FALSE
)
FetchContent_MakeAvailable(box2d)

add_executable(gfx_physics_box2d_oracle Box2DOracle.c)
target_compile_features(gfx_physics_box2d_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_geometry_oracle GeometryOracle.c)
target_compile_features(gfx_physics_box2d_geometry_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_geometry_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_body_control_oracle BodyControlOracle.c)
target_compile_features(gfx_physics_box2d_body_control_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_body_control_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_dynamic_shapes_oracle DynamicShapesOracle.c)
target_compile_features(gfx_physics_box2d_dynamic_shapes_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_dynamic_shapes_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_continuous_collision_oracle ContinuousCollisionOracle.c)
target_compile_features(gfx_physics_box2d_continuous_collision_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_continuous_collision_oracle PRIVATE box2d)

find_package(Python3 COMPONENTS Interpreter)
if(Python3_Interpreter_FOUND)
    add_test(
        NAME gfx_physics_box2d_completeness
        COMMAND
            ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/CheckCompleteness.py
            --box2d-source ${box2d_SOURCE_DIR}
    )
endif()

if(MSVC)
    target_compile_options(gfx_physics_box2d_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_geometry_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_body_control_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_dynamic_shapes_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_continuous_collision_oracle PRIVATE /W4)
else()
    target_compile_options(gfx_physics_box2d_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_geometry_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_body_control_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_dynamic_shapes_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_continuous_collision_oracle PRIVATE -Wall -Wextra -Wpedantic)
endif()
