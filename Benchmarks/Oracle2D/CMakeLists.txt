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

add_executable(gfx_physics_box2d_contact_policies_oracle ContactPoliciesOracle.c)
target_compile_features(gfx_physics_box2d_contact_policies_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_contact_policies_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_contact_snapshots_oracle ContactSnapshotsOracle.c)
target_compile_features(gfx_physics_box2d_contact_snapshots_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_contact_snapshots_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_continuous_collision_oracle ContinuousCollisionOracle.c)
target_compile_features(gfx_physics_box2d_continuous_collision_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_continuous_collision_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_world_queries_oracle WorldQueriesOracle.c)
target_compile_features(gfx_physics_box2d_world_queries_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_world_queries_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_character_mover_oracle CharacterMoverOracle.c)
target_compile_features(gfx_physics_box2d_character_mover_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_character_mover_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_explosion_oracle ExplosionOracle.c)
target_compile_features(gfx_physics_box2d_explosion_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_explosion_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_joints_oracle JointsOracle.c)
target_compile_features(gfx_physics_box2d_joints_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_joints_oracle PRIVATE box2d)

# Internal one-point solver comparison. POSIX timing, opt-in build only;
# neither this harness nor Box2D enters the Silex runtime.
if(UNIX AND CMAKE_C_COMPILER_ID MATCHES "Clang")
    foreach(layout IN ITEMS slots packed)
        add_executable(gfx_physics_contact_kernel_${layout} EXCLUDE_FROM_ALL ContactKernel.c)
        target_compile_features(gfx_physics_contact_kernel_${layout} PRIVATE c_std_17)
        target_compile_options(gfx_physics_contact_kernel_${layout} PRIVATE
            -O3 -ffp-contract=fast -Wall -Wextra -Wpedantic)
        target_compile_definitions(gfx_physics_contact_kernel_${layout} PRIVATE NDEBUG)
    endforeach()
    target_compile_definitions(gfx_physics_contact_kernel_slots PRIVATE SLOT8)
    add_executable(gfx_physics_contact_kernel_reference EXCLUDE_FROM_ALL ContactKernel.c)
    target_compile_features(gfx_physics_contact_kernel_reference PRIVATE c_std_17)
    target_compile_definitions(gfx_physics_contact_kernel_reference PRIVATE BOX2D_CHECK)
    target_include_directories(gfx_physics_contact_kernel_reference PRIVATE ${box2d_SOURCE_DIR}/src)
    target_link_libraries(gfx_physics_contact_kernel_reference PRIVATE box2d)
endif()

find_package(Python3 COMPONENTS Interpreter)
if(Python3_Interpreter_FOUND)
    add_test(
        NAME gfx_physics_contact_kernel_checks
        COMMAND ${Python3_EXECUTABLE} -B -m unittest discover
            -s ${CMAKE_CURRENT_SOURCE_DIR} -p TestContactKernel.py
    )
    add_test(
        NAME gfx_physics_box2d_comparison_checks
        COMMAND ${Python3_EXECUTABLE} -B -m unittest discover
            -s ${CMAKE_CURRENT_SOURCE_DIR} -p TestCompareCorpus.py
    )
    add_test(
        NAME gfx_physics_box2d_completeness
        COMMAND
            ${Python3_EXECUTABLE}
            ${CMAKE_CURRENT_SOURCE_DIR}/CheckCompleteness.py
            --box2d-source ${box2d_SOURCE_DIR}
            --final
    )
endif()

if(MSVC)
    target_compile_options(gfx_physics_box2d_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_geometry_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_body_control_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_dynamic_shapes_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_contact_policies_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_contact_snapshots_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_continuous_collision_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_world_queries_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_character_mover_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_explosion_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_joints_oracle PRIVATE /W4)
else()
    target_compile_options(gfx_physics_box2d_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_geometry_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_body_control_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_dynamic_shapes_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_contact_policies_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_contact_snapshots_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_continuous_collision_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_world_queries_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_character_mover_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_explosion_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_joints_oracle PRIVATE -Wall -Wextra -Wpedantic)
endif()
