from PIL import Image, ImageDraw, ImageFilter
import math
W,H=1920,1080
def base(glow_xy, glow_r, rings_xy, ring_n, ring_step, ring_alpha):
    img=Image.new('RGB',(W,H))
    top=(5,22,40); bot=(10,37,64)
    px=img.load()
    for y in range(H):
        t=y/H
        c=tuple(int(top[i]*(1-t)+bot[i]*t) for i in range(3))
        for x in range(W): px[x,y]=c
    glow=Image.new('RGB',(W,H),(0,0,0))
    d=ImageDraw.Draw(glow)
    gx,gy=glow_xy
    d.ellipse([gx-glow_r,gy-glow_r,gx+glow_r,gy+glow_r],fill=(14,110,90))
    glow=glow.filter(ImageFilter.GaussianBlur(glow_r*0.6))
    img=Image.blend(img, Image.fromarray(__import__('numpy').clip(__import__('numpy').asarray(img,dtype='int16')+__import__('numpy').asarray(glow,dtype='int16')//2,0,255).astype('uint8')),1.0)
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    rx,ry=rings_xy
    for i in range(1,ring_n+1):
        r=i*ring_step
        a=int(ring_alpha*(1-(i-1)/ring_n))
        d.ellipse([rx-r,ry-r,rx+r,ry+r],outline=(120,210,180,a),width=2)
    img=Image.alpha_composite(img.convert('RGBA'),ov).convert('RGB')
    return img
base((1500,300),520,(1560,540),9,95,70).save('bg_title.png')
base((1750,-50),420,(1920,1080),7,110,28).save('bg_content.png')
