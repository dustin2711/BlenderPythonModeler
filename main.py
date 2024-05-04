filename = "boxbuilder.py"
script = open(filename).read()
exec(compile(script, filename, "exec"))
