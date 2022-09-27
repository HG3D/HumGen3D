import inspect
import os
from re import L

import bpy
import HumGen3D

YIELD_LAST = (
    "HG_PT_BATCH_TIPS",
    "HG_PT_EXTRAS_TIPS",
)

YIELD_LATER = (
    "HG_SETTINGS",
    "HG_OBJECT_PROPS",
)

# There are more, but I'm not using them
BPY_CLASSES = (
    bpy.types.Operator,
    bpy.types.PropertyGroup,
    bpy.types.Panel,
    bpy.types.AddonPreferences,
    bpy.types.Header,
    bpy.types.Menu,
    bpy.types.UIList,
)


def _get_bpy_classes():
    dir_path = os.path.dirname(os.path.abspath(HumGen3D.__file__))

    py_files = get_python_files_from_dir(dir_path)

    already_yielded = []
    for root, filename in py_files:
        module = import_pyfile_as_module(dir_path, root, filename)

        yield_later = []
        yield_last = []
        for name, obj in inspect.getmembers(module):
            if not inspect.isclass(obj) or not issubclass(obj, BPY_CLASSES):
                continue
            # Skip classes that have been yielded previously
            if name in already_yielded:
                continue

            # Check if the class is actually from the HumGen3D module
            if not obj.__module__.split(".")[0] == "HumGen3D":
                continue

            if obj.__name__ in YIELD_LAST:
                yield_last.append(obj)
                continue

            # Wait with yielding UI classes that depend on parent
            if obj.__name__ in YIELD_LATER or hasattr(obj, "bl_parent_id"):
                yield_later.append(obj)
                continue

            already_yielded.append(name)
            yield obj

        yield from yield_later
        yield from yield_last


def import_pyfile_as_module(dir_path, root, filename):
    abspath = os.path.join(root, filename)
    rel_path_split = os.path.normpath(os.path.relpath(abspath, dir_path)).split(os.sep)
    module_import_path = ".".join(rel_path_split)

    module = __import__(
        ".".join(["HumGen3D", module_import_path[:-3]]),
        fromlist=[module_import_path[:-3]],
    )

    return module


def get_python_files_from_dir(dir_path):
    skip_dirs = (".vscode", ".mypy", ".git", "tests")
    py_files = []
    for root, _, files in os.walk(dir_path):
        if any(dir in root for dir in skip_dirs):
            continue
        for f in [f for f in files if f.endswith(".py")]:
            if f != "__init__.py" and f != "setup.py":
                py_files.append((root, f))
    return py_files
