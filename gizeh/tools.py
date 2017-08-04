
def htmlcolor_to_rgb(string):

    if not (string.startswith('#') and len(string)==7):
        raise ValueError("Bad html color format. Expected: '#RRGGBB' ")
    

    return [1.0*int(n,16)/255 for n in (string[1:3], string[3:5], string[5:])]
