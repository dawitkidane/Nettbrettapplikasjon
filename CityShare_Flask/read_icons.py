

import os, os.path

path = "C:\Users\webjo\Desktop\Github\Nettbrettapplikasjon\CityShare_Flask\static\icons"
valid_images = [".png"]
teller = 0
for f in os.listdir(path):
    if f.endswith(".png"):
        print("<option value='"+f+"' data-img-src='../static/Icons/"+f+"'>"+f.strip(".png")+"</option>")
        teller += 1

print(teller)


a =['asdasd,Point,2hand.png', 'zoo,Point,zoo.png']
b =['black,Road,#000000', 'blue,Road,#0000ff', 'green,Road,#008000']
c =['red,Area,#ff0000', 'white,Area,#ffffff', 'yellow,Area,#ffff00', 'purple,Area,#e916d9']
categories = a + b + c
for category in categories:
    cat = category.split(',')
    print(cat[0]+"-"+cat[1]+"-"+cat[2])