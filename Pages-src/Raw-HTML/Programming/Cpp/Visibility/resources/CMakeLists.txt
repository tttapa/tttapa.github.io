cmake_minimum_required(VERSION 3.24)
project(Visibility)
set(CMAKE_VERBOSE_MAKEFILE ON)
add_compile_options(-Wall -Wextra)

function(visibility_print_symbols tgt)
    string(JOIN "|" regex ${ARGN} "Symbol table" "Bind" "Vis")
    add_custom_command(TARGET ${tgt} POST_BUILD VERBATIM
        COMMAND ${CMAKE_COMMAND} -E echo
        COMMAND ${CMAKE_COMMAND} -E echo "Object file symbols ($<PATH:GET_FILENAME,$<TARGET_OBJECTS:${tgt}>>):"
        COMMAND ${CMAKE_READELF} -WCs "$<TARGET_OBJECTS:${tgt}>" | grep -E "${regex}"
        USES_TERMINAL)
    add_custom_command(TARGET ${tgt} POST_BUILD VERBATIM
        COMMAND ${CMAKE_COMMAND} -E echo
        COMMAND ${CMAKE_COMMAND} -E echo "Executable file symbols ($<PATH:GET_FILENAME,$<TARGET_FILE:${tgt}>>):"
        COMMAND ${CMAKE_READELF} -WCs "$<TARGET_FILE:${tgt}>" | grep -E "${regex}"
        USES_TERMINAL)
endfunction()

foreach(vis default hidden protected)
    foreach(vis-inl inl-hidden inl-default)
        set(vis-inl-value "Off")
        if (${vis-inl} STREQUAL "inl-hidden")
            set(vis-inl-value "On")
        endif()
        add_executable(${vis}-${vis-inl}-exe main.cpp)
        set_target_properties(${vis}-${vis-inl}-exe PROPERTIES CXX_VISIBILITY_PRESET ${vis})
        set_target_properties(${vis}-${vis-inl}-exe PROPERTIES VISIBILITY_INLINES_HIDDEN ${vis-inl-value})
        visibility_print_symbols(${vis}-${vis-inl}-exe "func")

        add_executable(${vis}-${vis-inl}-export-exe main.cpp)
        set_target_properties(${vis}-${vis-inl}-export-exe PROPERTIES CXX_VISIBILITY_PRESET ${vis})
        set_target_properties(${vis}-${vis-inl}-export-exe PROPERTIES VISIBILITY_INLINES_HIDDEN ${vis-inl-value})
        set_target_properties(${vis}-${vis-inl}-export-exe PROPERTIES ENABLE_EXPORTS ON)
        visibility_print_symbols(${vis}-${vis-inl}-export-exe "func")

        add_library(${vis}-${vis-inl}-shared SHARED main.cpp)
        set_target_properties(${vis}-${vis-inl}-shared PROPERTIES CXX_VISIBILITY_PRESET ${vis})
        set_target_properties(${vis}-${vis-inl}-shared PROPERTIES VISIBILITY_INLINES_HIDDEN ${vis-inl-value})
        visibility_print_symbols(${vis}-${vis-inl}-shared "func")
    endforeach()
endforeach()
