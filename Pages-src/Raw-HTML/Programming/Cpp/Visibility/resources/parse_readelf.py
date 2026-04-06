#!/usr/bin/env python3

"""Parse readelf output from readelf.txt into JSON for the Visibility tables."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import cast


OBJECT_HEADER_RE = re.compile(r"^Object file symbols \((?P<object_file>[^)]+)\):$")
EXECUTABLE_HEADER_RE = re.compile(r"^Executable file symbols \((?P<binary_name>[^)]+)\):$")
SECTION_HEADER_RE = re.compile(r"^Symbol table '(?P<section>\.dynsym|\.symtab)' contains\s+\d+\s+entries:$")
SYMBOL_RE = re.compile(
    r"^\s*\d+:\s+[0-9a-fA-F]+\s+\d+\s+FUNC\s+"
    r"(?P<bind>\w+)\s+(?P<vis>\w+)\s+\d+\s+(?P<name>.+?)\s*$"
)

TEMPLATE_MEMBER_RE = re.compile(
    r"^(?P<class>(?:Class|DefaultClass))<(?P<arg>[^>]+)>::(?P<member>func|out_of_line_func|static_func)\(\)$"
)

def _build_target_meta() -> dict[str, dict[str, object]]:
    """Build TARGET_META with all visibility x inlines_hidden combinations."""
    meta: dict[str, dict[str, object]] = {}
    for vis in ["default", "protected", "hidden"]:
        for inl in ["inl-hidden", "inl-default"]:
            inlines_hidden = inl == "inl-hidden"
            vis_flag = "" if vis == "default" else f" -fvisibility={vis}"
            inl_flag = " -fvisibility-inlines-hidden" if inlines_hidden else ""
            
            # Executables
            exe_name = f"{vis}-{inl}-exe"
            meta[exe_name] = {
                "link_type": "executable",
                "visibility": vis,
                "inlines_hidden": inlines_hidden,
                "compile": f"g++{vis_flag}{inl_flag}",
                "link": "g++",
            }
            
            # Export executables
            export_exe_name = f"{vis}-{inl}-export-exe"
            meta[export_exe_name] = {
                "link_type": "exports",
                "visibility": vis,
                "inlines_hidden": inlines_hidden,
                "compile": f"g++{vis_flag}{inl_flag}",
                "link": "g++ -Wl,--export-dynamic -rdynamic",
            }
            
            # Shared libraries
            shared_name = f"{vis}-{inl}-shared"
            meta[shared_name] = {
                "link_type": "shared",
                "visibility": vis,
                "inlines_hidden": inlines_hidden,
                "compile": f"g++ -fPIC{vis_flag}{inl_flag}",
                "link": "g++ -fPIC -shared",
            }
    return meta


TARGET_META = _build_target_meta()


BASE_SYMBOL_ORDER = {
    "func()": 0,
    "inline_func()": 1,
    "static_func()": 2,
    "(anonymous namespace)::anonymous_func()": 3,
    "default_func()": 4,
    "protected_func()": 5,
    "hidden_func()": 6,
}


def symbol_sort_key(name: str) -> tuple[object, ...]:
    if name in BASE_SYMBOL_ORDER:
        return (0, BASE_SYMBOL_ORDER[name], name)

    if "inline_template_func<" in name:
        return (1, 1, name)

    if "template_func<" in name:
        return (1, 0, name)

    template_member = TEMPLATE_MEMBER_RE.match(name)
    if template_member:
        class_name = template_member.group("class")
        argument = template_member.group("arg")
        member = template_member.group("member")
        class_rank = 0 if class_name == "Class" else 1
        arg_rank = 0 if argument == "NoInst" else 1
        member_rank = {"func": 0, "out_of_line_func": 1, "static_func": 2}.get(member, 9)
        return (2, class_rank, arg_rank, argument, member_rank, name)

    return (9, name)


def describe_symbol(name: str) -> tuple[str, str] | None:
    if name == "func()":
        return ("Normal function", "void func() { … }")
    if name == "static_func()":
        return ("Static function", "static void func() { … }")
    if name == "(anonymous namespace)::anonymous_func()":
        return ("Anonymous namespace function", "namespace {\nvoid func() { … }\n}")
    if name == "inline_func()":
        return ("Inline function", "inline void func() { … }")
    if name == "default_func()":
        return ("Explicit default visibility", 'void [[gnu::visibility("default")]] func() { … }')
    if name == "protected_func()":
        return ("Explicit protected visibility", 'void [[gnu::visibility("protected")]] func() { … }')
    if name == "hidden_func()":
        return ("Explicit hidden visibility", 'void [[gnu::visibility("hidden")]] func() { … }')
    if "inline_template_func<" in name:
        return (
            "Inline function template",
            "template <class T>\ninline void inline_template_func() { … }",
        )
    if "template_func<" in name:
        return (
            "Function template",
            "template <class T>\nvoid template_func() { … }",
        )
    template_member = TEMPLATE_MEMBER_RE.match(name)
    if template_member:
        class_name = template_member.group("class")
        argument = template_member.group("arg")
        member = template_member.group("member")
        if member == "func":
            if class_name == "Class" and argument == "NoInst":
                return (
                    "Member function of class template without attribute, implicitly instantiated",
                    "template <class T>\nstruct Class {\n    void func() { … }\n};\n\nClass<int> obj;  // implicitly instantiated\nobj.func();",
                )
            if class_name == "Class" and argument != "NoInst":
                return (
                    "Member function of class template without attribute, explicitly instantiated with default visibility",
                    "template <class T>\nstruct Class {\n    void func() { … }\n};\n\nstruct InstDefault;\ntemplate struct [[gnu::visibility(\"default\")]]\n    Class<InstDefault>;\n\nClass<InstDefault> obj;\nobj.func();",
                )
            if class_name == "DefaultClass" and argument == "NoInst":
                return (
                    "Member function of class template with default visibility, implicitly instantiated",
                    'template <class T>\nstruct [[gnu::visibility("default")]] DefaultClass {\n    void func() { … }\n};\n\nDefaultClass<int> obj;  // implicitly instantiated\nobj.func();',
                )
            if class_name == "DefaultClass" and argument == "InstDefault":
                return (
                    "Member function of class template with default visibility, explicitly instantiated with default visibility",
                    'template <class T>\nstruct [[gnu::visibility("default")]] DefaultClass {\n    void func() { … }\n};\n\nstruct InstDefault;\ntemplate struct [[gnu::visibility("default"))]]\n    DefaultClass<InstDefault>;\n\nDefaultClass<InstDefault> obj;\nobj.func();',
                )
            if class_name == "DefaultClass" and argument == "InstProtected":
                return (
                    "Member function of class template with default visibility, explicitly instantiated with protected visibility",
                    'template <class T>\nstruct [[gnu::visibility("default")]] DefaultClass {\n    void func() { … }\n};\n\nstruct InstProtected;\ntemplate struct [[gnu::visibility("protected"))]]\n    DefaultClass<InstProtected>;\n\nDefaultClass<InstProtected> obj;\nobj.func();',
                )
            if class_name == "DefaultClass" and argument == "Inst":
                return (
                    "Member function of class template with default visibility, explicitly instantiated without attribute",
                    'template <class T>\nstruct [[gnu::visibility("default")]] DefaultClass {\n    void func() { … }\n};\n\nstruct Inst;\ntemplate struct DefaultClass<Inst>;\n\nDefaultClass<Inst> obj;\nobj.func();',
                )
            assert False, f"Unexpected template member function: {name}"
        if member == "out_of_line_func":
            if class_name == "Class" and argument == "NoInst":
                return (
                    "Out-of-line member function of class template without attribute, implicitly instantiated",
                    "template <class T>\nstruct Class {\n    void out_of_line_func();\n};\n\ntemplate <class T>\nvoid Class<T>::out_of_line_func() { … }\n\nClass<int> obj;\nobj.out_of_line_func();",
                )
            if class_name == "Class" and argument != "NoInst":
                return (
                    "Out-of-line member function of class template without attribute, explicitly instantiated with default visibility",
                    "template <class T>\nstruct Class {\n    void out_of_line_func();\n};\n\ntemplate <class T>\nvoid Class<T>::out_of_line_func() { … }\n\nstruct InstDefault;\ntemplate struct [[gnu::visibility(\"default\")]]\n    Class<InstDefault>;\n\nClass<InstDefault> obj;\nobj.out_of_line_func();",
                )
            if class_name == "DefaultClass" and argument == "NoInst":
                return (
                    "Out-of-line member function of class template with default visibility, implicitly instantiated",
                    'template <class T>\nstruct [[gnu::visibility("default")]] DefaultClass {\n    void out_of_line_func();\n};\n\ntemplate <class T>\nvoid DefaultClass<T>::out_of_line_func() { … }\n\nDefaultClass<int> obj;\nobj.out_of_line_func();',
                )
            if class_name == "DefaultClass" and argument == "InstDefault":
                return (
                    "Out-of-line member function of class template with default visibility, explicitly instantiated with default visibility",
                    'template <class T>\nstruct [[gnu::visibility("default")]] DefaultClass {\n    void out_of_line_func();\n};\n\ntemplate <class T>\nvoid DefaultClass<T>::out_of_line_func() { … }\n\nstruct InstDefault;\ntemplate struct [[gnu::visibility("default")]]\n    DefaultClass<InstDefault>;\n\nDefaultClass<InstDefault> obj;\nobj.out_of_line_func();',
                )
            if class_name == "DefaultClass" and argument == "InstProtected":
                return (
                    "Out-of-line member function of class template with default visibility, explicitly instantiated with protected visibility",
                    'template <class T>\nstruct [[gnu::visibility("default")]] DefaultClass {\n    void out_of_line_func();\n};\n\ntemplate <class T>\nvoid DefaultClass<T>::out_of_line_func() { … }\n\nstruct InstProtected;\ntemplate struct [[gnu::visibility("protected")]]\n    DefaultClass<InstProtected>;\n\nDefaultClass<InstProtected> obj;\nobj.out_of_line_func();',
                )
            if class_name == "DefaultClass" and argument == "Inst":
                return (
                    "Out-of-line member function of class template with default visibility, explicitly instantiated without attribute",
                    'template <class T>\nstruct [[gnu::visibility("default")]] DefaultClass {\n    void out_of_line_func();\n};\n\ntemplate <class T>\nvoid DefaultClass<T>::out_of_line_func() { … }\n\nstruct Inst;\ntemplate struct DefaultClass<Inst>;\n\nDefaultClass<Inst> obj;\nobj.out_of_line_func();',
                )
            assert False, f"Unexpected template out-of-line member function: {name}"
        if member == "static_func":
            return None  # Skip static member functions since they have the same visibility as non-static ones, and we want to avoid cluttering the table with more entries
            if class_name == "Class" and argument == "NoInst":
                return (
                    "Static member function of class template without attribute, implicitly instantiated",
                    "template <class T>\nstruct Class {\n    static void static_func() { … }\n};\n\nClass<int> obj;  // implicitly instantiated\nobj.static_func();",
                )
            if class_name == "Class" and argument != "NoInst":
                return (
                    "Static member function of class template without attribute, explicitly instantiated with default visibility",
                    "template <class T>\nstruct Class {\n    static void static_func() { … }\n};\n\nstruct InstDefault;\ntemplate struct __attribute__((visibility(\"default\")))\n    Class<InstDefault>;",
                )
            if class_name == "DefaultClass" and argument == "NoInst":
                return (
                    "Static member function of class template with default visibility, implicitly instantiated",
                    'template <class T>\nstruct [[gnu::visibility("default")]] DefaultClass {\n    static void static_func() { … }\n};\n\nDefaultClass<int> obj;  // implicitly instantiated\nobj.static_func();',
                )
            if class_name == "DefaultClass" and argument == "Inst":
                return (
                    "Static member function of class template with default visibility, explicitly instantiated without attribute",
                    'template <class T>\nstruct [[gnu::visibility("default")]] DefaultClass {\n    static void static_func() { … }\n};\n\nstruct Inst;\ntemplate struct DefaultClass<Inst>;',
                )
            assert False, f"Unexpected template static member function: {name}"
    return ("Function symbol", name)


def parse_readelf_log(text: str) -> dict[str, object]:
    targets: list[dict[str, object]] = []
    seen_symbols: set[str] = set()
    current_target: dict[str, object] | None = None
    current_section: str | None = None
    current_phase: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        object_match = OBJECT_HEADER_RE.match(line)
        if object_match:
            current_target = {
                "object_file_name": object_match.group("object_file"),
                "binary_name": "",
                "symbols": {},
            }
            targets.append(current_target)
            current_phase = "object"
            current_section = None
            continue

        executable_match = EXECUTABLE_HEADER_RE.match(line)
        if executable_match:
            if current_target is None:
                continue
            current_target["binary_name"] = executable_match.group("binary_name")
            current_phase = "binary"
            current_section = "binary"
            continue

        section_match = SECTION_HEADER_RE.match(line)
        if section_match:
            current_section = section_match.group("section")
            continue

        symbol_match = SYMBOL_RE.match(line)
        if symbol_match and current_target is not None and current_section is not None:
            key = symbol_match.group("name")
            seen_symbols.add(key)

            symbols = cast(dict[str, dict[str, object]], current_target["symbols"])
            entry = symbols.setdefault(key, {"key": key})

            if current_phase == "object" and current_section == ".symtab":
                entry["object_bind"] = symbol_match.group("bind")
                entry["object_vis"] = symbol_match.group("vis")
            elif current_phase == "binary" and current_section == ".symtab":
                entry["binary_bind"] = symbol_match.group("bind")
                entry["binary_vis"] = symbol_match.group("vis")
            elif current_phase == "binary" and current_section == ".dynsym":
                entry["dynsym"] = True

    output_targets: dict[str, dict[str, dict[str, dict[str, object]]]] = {
        "executable": {},
        "shared": {},
        "exports": {},
    }
    symbol_order = sorted(seen_symbols, key=symbol_sort_key)

    for target in targets:
        symbols = cast(dict[str, dict[str, object]], target.pop("symbols"))
        binary_name = cast(str, target["binary_name"])
        
        # Try direct lookup first, then try stripping lib prefix for shared libraries
        meta = TARGET_META.get(binary_name)
        if meta is None and binary_name.startswith("lib") and binary_name.endswith(".so"):
            # Try without lib prefix and .so suffix
            base_name = binary_name[3:-3]  # Remove "lib" and ".so"
            meta = TARGET_META.get(base_name)
        
        if meta is None:
            continue

        rows = []
        for key in symbol_order:
            t = describe_symbol(key)
            if t is None:
                continue
            description, definition = t
            entry = symbols.get(key, {})
            rows.append(
                {
                    "key": key,
                    "description": description,
                    "definition": definition,
                    "object_bind": entry.get("object_bind"),
                    "object_vis": entry.get("object_vis"),
                    "binary_bind": entry.get("binary_bind"),
                    "binary_vis": entry.get("binary_vis"),
                    "dynsym": bool(entry.get("dynsym", False)),
                }
            )

        link_type = cast(str, meta["link_type"])
        visibility = cast(str, meta["visibility"])
        inlines_hidden = cast(bool, meta["inlines_hidden"])
        inl_key = "hidden" if inlines_hidden else "default"
        
        if visibility not in output_targets[link_type]:
            output_targets[link_type][visibility] = {}
        
        output_targets[link_type][visibility][inl_key] = {
            "title": binary_name,
            "object_file_name": target["object_file_name"],
            "binary_name": binary_name,
            "inlines_hidden": inlines_hidden,
            "compile": meta["compile"],
            "link": meta["link"],
            "rows": rows,
        }

    return {
        "symbols": [
            {
                "key": key,
                "description": t[0],
                "definition": t[1],
            }
            for key in symbol_order
            if (t := describe_symbol(key)) is not None
        ],
        "targets": output_targets,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="readelf.txt", help="path to the readelf log")
    parser.add_argument("output", nargs="?", default="readelf.json", help="path to the JSON output")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    data = parse_readelf_log(input_path.read_text(encoding="utf-8"))
    output_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()