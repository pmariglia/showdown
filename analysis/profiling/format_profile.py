fp = 'profiled.txt'
out = "formatted.txt"

with open(fp, 'r') as f:
    lines = f.readlines()

with open(out, 'w') as f:
    for line in lines:
        pre = line[:46]
        post = line[46:]
        f.write(",".join(pre.split()) + "," + post)
