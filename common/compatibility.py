import bpy

EEVEE_RENDER_ENGINE = "BLENDER_EEVEE" if bpy.app.version < (4, 2, 0) else "BLENDER_EEVEE_NEXT"