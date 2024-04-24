import os.path
from PIL import Image, ImageFilter
from PIL.Image import Resampling
import argparse
import requests
import webbrowser
from os import remove

parser = argparse.ArgumentParser(
                    prog='SkinToPFP',
                    description='A cli program to download minecraft skins :)',
                    epilog='')
parser.add_argument('user', help='Minecraft Username, (local file if -l flag is passed)')
parser.add_argument('save_location', help='Directory to save to')
parser.add_argument('-s', '--skin', help='Only download skin (dont convert to profile pic)', action="store_true")
parser.add_argument('-z', '--size', help='Resize the output image by this much. minimum: 1, recommended: 6', default='6')
parser.add_argument('-a', '--ambient_bg', help='Sets the background to a Youtube-like ambient color', action='store_true')
parser.add_argument('-b', '--bg', help='Sets the background color to a RGB value. triple values 0-255 split with ":"')
parser.add_argument('-l', '--local', help='Use a local file as skin', action='store_true')


args = parser.parse_args()

save = args.save_location + args.user + ".png"
save2 = args.save_location + args.user + "_pfp.png"


def dl_from_web(user):
    global save
    if not args.local:
        skin_image = requests.get(f"https://minecraft.tools/download-skin/{user}")
        if skin_image.status_code == 200:
            with open(save, "wb") as f:
                f.write(skin_image.content)
            return skin_image.content
    else:
        with open(save, "rb") as f:
            cont = f.read()
        return cont


def image_to_pixels(image):
    """
    Convert an image to a list of pixels.
    Each pixel is represented as a tuple of RGB values.
    """
    img = image.convert('RGB')
    pixels = list(img.getdata())
    return pixels


def average_color(pixels):
    """
    Calculate the average color from a list of pixels.
    """
    sum_red = sum_green = sum_blue = 0
    num_pixels = len(pixels)

    for pixel in pixels:
        red, green, blue = pixel
        sum_red += red
        sum_green += green
        sum_blue += blue

    avg_red = sum_red / num_pixels
    avg_green = sum_green / num_pixels
    avg_blue = sum_blue / num_pixels

    return [255-avg_red, 255-avg_green, 255-avg_blue]


def mk_pfp():
    with Image.open(save) as img:
        head = img.crop((8, 9, 15, 16))
        headside = img.crop((5, 9, 8, 16))
        hair = img.crop((40, 9, 47, 16)).convert('RGBA')
        hairside = img.crop((37, 9, 40, 16)).convert('RGBA')
        torso_top = img.crop((21, 20, 27, 21))
        torso_mid = img.crop((20, 21, 28, 22))
        torso_bot = img.crop((20, 22, 28, 29))
        torso_top_out = img.crop((21, 36, 27, 37)).convert('RGBA')
        torso_mid_out = img.crop((20, 37, 28, 38)).convert('RGBA')
        torso_bot_out = img.crop((20, 38, 28, 45)).convert('RGBA')
        larm = img.crop((17, 22, 20, 29))
        rarm = img.crop((30, 22, 31, 29))
        if args.bg is not None:
            col = str(args.bg).split(':')[0:3]
        elif args.ambient_bg:
            head_pixels = image_to_pixels(head)
            headside_pixels = image_to_pixels(headside)
            hair_pixels = image_to_pixels(hair)
            hairside_pixels = image_to_pixels(hairside)
            torso_top_pixels = image_to_pixels(torso_top)
            torso_mid_pixels = image_to_pixels(torso_mid)
            torso_bot_pixels = image_to_pixels(torso_bot)
            torso_top_out_pixels = image_to_pixels(torso_top_out)
            torso_mid_out_pixels = image_to_pixels(torso_mid_out)
            torso_bot_out_pixels = image_to_pixels(torso_bot_out)
            larm_pixels = image_to_pixels(larm)
            rarm_pixels = image_to_pixels(rarm)
            amb = head_pixels+headside_pixels+hair_pixels+torso_top_pixels+torso_mid_pixels+torso_bot_pixels+larm_pixels+rarm_pixels+hairside_pixels+torso_top_out_pixels+torso_mid_out_pixels+torso_bot_out_pixels
            amb = average_color(amb)
            col = amb
        else:
            col = [0, 0, 0]
        for i in range(len(col)):
            col[i] = int(round(float(col[i])))
        col = tuple(col)
        final = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
        shade = Image.open('shade.png').convert('RGBA')
        sz = 20*int(args.size)
        final.paste(head, (8, 4))
        final.paste(headside, (5, 4))
        final.paste(torso_top, (7, 11))
        final.paste(torso_mid, (6, 12))
        final.paste(torso_bot, (6, 13))
        final.paste(torso_top_out, (7, 11), torso_top_out)
        final.paste(torso_mid_out, (6, 12), torso_mid_out)
        final.paste(torso_bot_out, (6, 13), torso_bot_out)
        final.paste(larm, (5, 13))
        final.paste(rarm, (14, 13))
        hair = hair.resize((round(7.5*int(args.size)), round(7.5*int(args.size))), resample=Resampling.BOX)
        hairside = hairside.resize((round(3.5*int(args.size)), round(7.5*int(args.size))), resample=Resampling.BOX)
        final.alpha_composite(shade)
        final = final.resize((sz, sz), resample=Resampling.BOX)
        final.paste(hair, (8*int(args.size)+round(int(args.size)/8), 4*int(args.size)-round(int(args.size)/8)), hair)
        final.paste(hairside, (5*int(args.size)+round(int(args.size)/8), 4*int(args.size)-round(int(args.size)/8)), hairside)
        finale = Image.new('RGBA', (sz, sz), col)
        shadow = final.filter(ImageFilter.GaussianBlur(2*int(args.size)))
        finale.alpha_composite(shadow)
        finale.paste(final, (0, 0), final)
        finale.convert('RGB')
        finale.save(save2, "PNG")
        print(f"Size: {sz}x{sz}")
        print(f"Saved To: {os.path.abspath(save2)}")


# unused function :)
def open_namemc(user):
    webbrowser.open(f"https://namemc.com/profile/{user}")


skin = dl_from_web(args.user)
if not args.skin:  # if user doesn't want a profile picture, respect that.
    mk_pfp()
if args.local is False or args.skin:
    remove(save)
