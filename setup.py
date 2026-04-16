import os
from setuptools import setup, find_packages, Extension
try:
    from Cython.Build import cythonize
except ImportError:
    # Fallback to no cythonize for tools that just want to read metadata
    def cythonize(extensions, **kwargs):
        return extensions

# Find all .py files in the package except __init__.py if we want to keep it as Python
# Actually, we can cythonize everything. 
# But for Flask/SQLAlchemy patterns, it's safer to keep __init__.py as Python
# and compile the rest. 

def get_ext_modules():
    extensions = []
    for root, dirs, files in os.walk("ortus_flask"):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                path = os.path.join(root, file)
                module_name = path.replace(os.path.sep, ".").replace(".py", "")
                extensions.append(Extension(module_name, [path]))
    return cythonize(extensions, compiler_directives={'language_level': "3"})

setup(
    ext_modules=get_ext_modules(),
)
