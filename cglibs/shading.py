"""Shared shading-mode names and F/G/P/I (optional T/E) key handling."""
import glfw

SHADING_FILES = {
    'flat':    ("./shaders/flat.vert",    "./shaders/flat.frag"),
    'gouraud': ("./shaders/gouraud.vert", "./shaders/gouraud.frag"),
    'phong':   ("./shaders/phong.vert",   "./shaders/phong.frag"),
    'interp':  ("./shaders/interp.vert",  "./shaders/interp.frag"),
}

_LABELS = {
    'flat':    "FLAT",
    'gouraud': "GOURAUD",
    'phong':   "PHONG",
    'interp':  "INTERP (vertex color)",
    'texture': "TEXTURE",
    'edge':    "EDGE",
}


def handle_shading_key(obj, key):
    mapping = {
        glfw.KEY_F: 'flat',
        glfw.KEY_G: 'gouraud',
        glfw.KEY_P: 'phong',
        glfw.KEY_I: 'interp',
        glfw.KEY_T: 'texture',
        glfw.KEY_E: 'edge',
    }
    name = mapping.get(key)
    if name is None or name not in getattr(obj, 'programs', {}):
        return
    obj.shading = name
    print("Shading:", _LABELS.get(name, name.upper()))
