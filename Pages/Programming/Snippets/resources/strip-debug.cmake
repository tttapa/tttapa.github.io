# Strip and install debug information
function(myproject_install_debug_syms target component dest_lib dest_bin)
    if (MSVC)
        install(FILES "$<TARGET_PDB_FILE:${target}>"
            DESTINATION ${dest_bin}
            CONFIGURATIONS Debug RelWithDebInfo
            COMPONENT ${component} 
            OPTIONAL EXCLUDE_FROM_ALL)
    elseif (CMAKE_STRIP AND CMAKE_OBJCOPY)
        set(DEBUG_FILE "$<TARGET_FILE_NAME:${target}>.debug")
        add_custom_command(TARGET ${target} POST_BUILD
            COMMAND "${CMAKE_STRIP}" "--only-keep-debug" "$<TARGET_FILE:${target}>" "-o" "${DEBUG_FILE}"
            COMMAND "${CMAKE_STRIP}" "--strip-debug" "$<TARGET_FILE:${target}>"
            COMMAND "${CMAKE_OBJCOPY}" "--add-gnu-debuglink=${DEBUG_FILE}" "$<TARGET_FILE:${target}>"
            COMMAND "${CMAKE_COMMAND}" "-E" "echo" "Stripped into ${DEBUG_FILE}"
            WORKING_DIRECTORY $<TARGET_FILE_DIR:${target}>)
        install(FILES "$<TARGET_FILE_DIR:${target}>/${DEBUG_FILE}"
            DESTINATION ${dest_lib}
            CONFIGURATIONS Debug RelWithDebInfo
            COMPONENT ${component}
            EXCLUDE_FROM_ALL)
    endif()
endfunction()

# Usage
include(GNUInstallDirs)
foreach(target IN LISTS MYPROJECT_INSTALL_TARGETS)
    get_target_property(target_TYPE ${target} TYPE)
    if (${target_TYPE} STREQUAL "SHARED_LIBRARY")
        myproject_install_debug_syms(${target} debug
                                     ${CMAKE_INSTALL_LIBDIR}
                                     ${CMAKE_INSTALL_BINDIR})
    endif()
endforeach()
