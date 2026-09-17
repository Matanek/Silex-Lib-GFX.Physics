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

add_executable(gfx_physics_box2d_units_oracle UnitsOracle.c)
target_compile_features(gfx_physics_box2d_units_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_units_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_geometry_values_oracle GeometryValuesOracle.c)
target_compile_features(gfx_physics_box2d_geometry_values_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_geometry_values_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_geometric_validity_oracle GeometricValidityOracle.c)
target_compile_features(gfx_physics_box2d_geometric_validity_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_geometric_validity_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_geometry_oracle GeometryOracle.c)
target_compile_features(gfx_physics_box2d_geometry_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_geometry_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_speculative_contacts_oracle SpeculativeContactsOracle.c)
target_compile_features(gfx_physics_box2d_speculative_contacts_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_speculative_contacts_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_compound_contacts_oracle CompoundContactsOracle.c)
target_compile_features(gfx_physics_box2d_compound_contacts_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_compound_contacts_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_body_events_oracle BodyEventsOracle.c)
target_compile_features(gfx_physics_box2d_body_events_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_body_events_oracle PRIVATE box2d)

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

add_executable(gfx_physics_box2d_zero_step_oracle ZeroStepOracle.c)
target_compile_features(gfx_physics_box2d_zero_step_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_zero_step_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_distance_tuning_oracle DistanceTuningOracle.c)
target_compile_features(gfx_physics_box2d_distance_tuning_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_distance_tuning_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_joint_tuning_oracle JointConstraintTuningOracle.c)
target_compile_features(gfx_physics_box2d_joint_tuning_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_joint_tuning_oracle PRIVATE box2d)

add_executable(gfx_physics_box2d_joint_combinations_oracle JointCombinationsOracle.c)
target_compile_features(gfx_physics_box2d_joint_combinations_oracle PRIVATE c_std_17)
target_link_libraries(gfx_physics_box2d_joint_combinations_oracle PRIVATE box2d)

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

    foreach(layout IN ITEMS slots packed)
        add_executable(gfx_physics_integration_kernel_${layout} EXCLUDE_FROM_ALL IntegrationKernel.c)
        target_compile_features(gfx_physics_integration_kernel_${layout} PRIVATE c_std_17)
        target_compile_options(gfx_physics_integration_kernel_${layout} PRIVATE
            -O3 -ffp-contract=fast -Wall -Wextra -Wpedantic)
        target_compile_definitions(gfx_physics_integration_kernel_${layout} PRIVATE NDEBUG)
    endforeach()
    target_compile_definitions(gfx_physics_integration_kernel_slots PRIVATE SLOT8)
    add_executable(gfx_physics_integration_kernel_reference EXCLUDE_FROM_ALL IntegrationKernel.c)
    target_compile_features(gfx_physics_integration_kernel_reference PRIVATE c_std_17)
    target_compile_definitions(gfx_physics_integration_kernel_reference PRIVATE BOX2D_CHECK)
    target_compile_options(gfx_physics_integration_kernel_reference PRIVATE -ffp-contract=off)
    target_include_directories(gfx_physics_integration_kernel_reference PRIVATE ${box2d_SOURCE_DIR}/src)
    target_link_libraries(gfx_physics_integration_kernel_reference PRIVATE box2d)

    foreach(layout IN ITEMS slots packed)
        add_executable(gfx_physics_preparation_kernel_${layout} EXCLUDE_FROM_ALL PreparationKernel.c)
        target_compile_features(gfx_physics_preparation_kernel_${layout} PRIVATE c_std_17)
        target_compile_options(gfx_physics_preparation_kernel_${layout} PRIVATE
            -O3 -ffp-contract=fast -Wall -Wextra -Wpedantic)
        target_compile_definitions(gfx_physics_preparation_kernel_${layout} PRIVATE NDEBUG)
    endforeach()
    target_compile_definitions(gfx_physics_preparation_kernel_slots PRIVATE SLOT8)
    add_executable(gfx_physics_preparation_kernel_reference EXCLUDE_FROM_ALL PreparationKernel.c)
    target_compile_features(gfx_physics_preparation_kernel_reference PRIVATE c_std_17)
    target_compile_definitions(gfx_physics_preparation_kernel_reference PRIVATE BOX2D_CHECK)
    target_compile_options(gfx_physics_preparation_kernel_reference PRIVATE -ffp-contract=off)
    target_include_directories(gfx_physics_preparation_kernel_reference PRIVATE ${box2d_SOURCE_DIR}/src)
    target_link_libraries(gfx_physics_preparation_kernel_reference PRIVATE box2d)
endif()

find_package(Python3 COMPONENTS Interpreter)
if(Python3_Interpreter_FOUND)
    add_test(
        NAME gfx_physics_compound_contacts_checks
        COMMAND ${Python3_EXECUTABLE} -B -m unittest discover
            -s ${CMAKE_CURRENT_SOURCE_DIR} -p TestCompoundContacts.py
    )
    add_test(
        NAME gfx_physics_body_events_checks
        COMMAND ${Python3_EXECUTABLE} -B -m unittest discover
            -s ${CMAKE_CURRENT_SOURCE_DIR} -p TestBodyEvents.py
    )
    add_test(
        NAME gfx_physics_geometry_values_checks
        COMMAND ${Python3_EXECUTABLE} -B -m unittest discover
            -s ${CMAKE_CURRENT_SOURCE_DIR} -p TestGeometryValues.py
    )
    add_test(
        NAME gfx_physics_units_checks
        COMMAND ${Python3_EXECUTABLE} -B -m unittest discover
            -s ${CMAKE_CURRENT_SOURCE_DIR} -p TestUnits.py
    )
    add_test(
        NAME gfx_physics_contact_pair_checks
        COMMAND ${Python3_EXECUTABLE} -B -m unittest discover
            -s ${CMAKE_CURRENT_SOURCE_DIR} -p TestContactPairs.py
    )
    add_test(
        NAME gfx_physics_zero_step_checks
        COMMAND ${Python3_EXECUTABLE} -B -m unittest discover
            -s ${CMAKE_CURRENT_SOURCE_DIR} -p TestZeroStep.py
    )
    add_test(
        NAME gfx_physics_distance_tuning_checks
        COMMAND ${Python3_EXECUTABLE} -B -m unittest discover
            -s ${CMAKE_CURRENT_SOURCE_DIR} -p TestDistanceTuning.py
    )
    add_test(
        NAME gfx_physics_speculative_contact_checks
        COMMAND ${Python3_EXECUTABLE} -B -m unittest discover
            -s ${CMAKE_CURRENT_SOURCE_DIR} -p TestSpeculativeContacts.py
    )
    add_test(
        NAME gfx_physics_joint_constraint_checks
        COMMAND ${Python3_EXECUTABLE} -B -m unittest discover
            -s ${CMAKE_CURRENT_SOURCE_DIR} -p TestJointConstraints.py
    )
    add_test(
        NAME gfx_physics_stage_kernel_checks
        COMMAND ${Python3_EXECUTABLE} -B -m unittest discover
            -s ${CMAKE_CURRENT_SOURCE_DIR} -p TestStageKernels.py
    )
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
    target_compile_options(gfx_physics_box2d_compound_contacts_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_body_events_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_units_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_geometry_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_geometry_values_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_geometric_validity_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_body_control_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_dynamic_shapes_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_contact_policies_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_contact_snapshots_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_continuous_collision_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_world_queries_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_character_mover_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_explosion_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_joints_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_distance_tuning_oracle PRIVATE /W4)
    target_compile_options(gfx_physics_box2d_zero_step_oracle PRIVATE /W4)
else()
    target_compile_options(gfx_physics_box2d_compound_contacts_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_body_events_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_units_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_geometry_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_geometry_values_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_geometric_validity_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_body_control_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_dynamic_shapes_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_contact_policies_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_contact_snapshots_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_continuous_collision_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_world_queries_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_character_mover_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_explosion_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_joints_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_distance_tuning_oracle PRIVATE -Wall -Wextra -Wpedantic)
    target_compile_options(gfx_physics_box2d_zero_step_oracle PRIVATE -Wall -Wextra -Wpedantic)
endif()
