import zipfile, re, sys
src, dst = sys.argv[1], sys.argv[2]
zin = zipfile.ZipFile(src)
zout = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    data = zin.read(it.filename)
    if re.match(r'ppt/slides/slide\d+\.xml$', it.filename):
        x = data.decode('utf8')
        if '<p:transition' not in x:
            t = '<p:transition spd="slow"><p:fade/></p:transition>'
            if '<p:timing' in x: x = x.replace('<p:timing', t + '<p:timing', 1)
            else: x = x.replace('</p:sld>', t + '</p:sld>')
        data = x.encode('utf8')
    zout.writestr(it, data)
zout.close()
