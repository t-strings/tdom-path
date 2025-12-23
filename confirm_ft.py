import sysconfig

is_free_threaded_build = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
print(f"Is this a free-threaded build? {is_free_threaded_build}")

if is_free_threaded_build:
    print("The Python executable was compiled with free-threading support.")
else:
    print("The Python executable is a standard GIL-enabled build.")
