import os
import sys
# import json
# import subprocess

# import tkinter as tk
# from PIL import Image, ImageTk

# import nltk
import re


def default_camera():
    return """
    camera {
        perspective
        location <0.0, 1.5, -12.0>
        direction <0, 0, 1>
        up y
        right x*1.77
        look_at <0.0, 0.5, 0.00>
    }
    """


def default_light():
    return """
    light_source {
        <10.00, 15.00, -20.00>
        color White
        area_light <5, 0, 0>, <0, 0, 5>, 5, 5
        adaptive 1
        jitter
    }
    """


def header():
    return """
    #version 3.7;

    global_settings { assumed_gamma 2.2 }

    #include "colors.inc"
    #include "textures.inc"
    #include "shapes.inc"

    #declare rseed = seed(123);

    #default {
        pigment { White }
        finish {
            ambient .2
            diffuse .6
            specular .25
            roughness .1
        }
    }
    """

def row(arg):
    result = ""
    for x in range(-8, 9, 4):
        result += arg[:-2] + " translate <{0}, 0, 0> ".format(x) + arg[-2:] 

    return result


def stack(arg):
    result = ""
    for y in range(0, 10, 2):
        result += arg[:-2] + " translate <0, {0}, 0> ".format(y) + arg[-2:] 

    return result


def flat_array(arg):
    result = ""
    for x in range(-8, 9, 4):
        for z in range(-2, 15, 4):
            result += arg[:-2] + " translate <{0}, 0, {1}> ".format(x, z) + arg[-2:] 

    return result


def wall(arg):
    result = ""
    for x in range(-7, 8, 3):
        for y in range(0, 10, 2):
            result += arg[:-2] + " translate <{0}, {1}, 0> ".format(x, y) + arg[-2:] 

    return result


def do_function(function, arg):
    if function == "flat_array":
        return flat_array(arg)
    if function == "stack":
        return stack(arg)
    if function == "row":
        return row(arg)
    if function == "wall":
        return wall(arg)
    return ""


def initialize_dictionary():
    """
    load the translation file into memory
    """
    dictionary = {}
    with open("./data/NSL_Dictionary.data", "r") as handle:
        lines = handle.readlines()

    line_pattern = re.compile(r"^([A-Z]) ([A-Za-z0-9]+) (.+)$")
    for line in lines:
        match = line_pattern.match(line)
        if match:
            groups = match.groups()
            dictionary[groups[1]] = {'part': groups[0], 'code': groups[2]}

    return dictionary


def part_of_speech(record):
    return record['part']


def translate_adjective(functions, modifiers, record):
    text = modifiers
    text += record['code']
    return functions, text, ""


def translate_noun(functions, modifiers, record):
    text = ''
    text += record['code']
    text += " "
    text += modifiers
    text += " }\n"
    return functions, "", text


def translate_function(functions, modifiers, record):
    functions.append(record['code'])
    return functions, modifiers, ""


def translate(functions, modifiers, record):
    if part_of_speech(record) == "N":
        return translate_noun(functions, modifiers, record)

    elif part_of_speech(record) == "A":
        return translate_adjective(functions, modifiers, record)

    elif part_of_speech(record) == "F":
        return translate_function(functions, modifiers, record)
    else:
        return functions, modifiers, "" 


def text_to_pov(text):
    modifiers = ""
    subject = ""
    functions = []
    no_camera = True
    no_light = True
    line = re.split(" ", text.rstrip())

    lookup = initialize_dictionary()

    for token in line:
        record = lookup.get(token.lower(), {"part": "X", "code": ""})
        if part_of_speech(record) == "X":
            record = lookup.get(token.lower().rstrip("s"), {"part": "X", "code": ""})

        functions, modifiers, text = translate(functions, modifiers, record)

        if text:
            if not functions:
                subject += text
            else:
                for function in functions:
                    subject += do_function(function, text)
                functions = []    

    if no_camera:
        subject += default_camera()
    if no_light:
        subject += default_light()

    return subject

'''
def change_frame(frame):
    image = ImageTk.PhotoImage(Image.open("tmp/tmp{0}.ppm".format(frame)))
    canvas.configure(image=image)
    canvas.image = image
'''

def render(sentence, file_prefix):
    """
    parsed = parse_prompt(editor.get("1.0", tk.END))

    sentence = ""
    for tree in parsed:
        tree.pretty_print()
        sentence += " ".join([x[0] for x in extract("S", tree)])
        print("CLAUSE:", " ".join([x[0] for x in extract("CLAUSE", tree)]))
        print("NOUN PHRASES:", " ".join([x[0] for x in extract("NP", tree)]))
        print("VERB PHRASE:", " ".join([x[0] for x in extract("VP", tree)]))
        print("PREPOSITIONAL PHRASE:", " ".join([x[0] for x in extract("PP", tree)]))
        print("ADJECTIVES:", " ".join([x[0] for x in extract("JJ", tree)]))
    # DEBUG

    print("SENTENCE:", sentence)
    """

    with open("tmp/{0}.pov".format(file_prefix), "w") as handle:
        handle.write(header())
        handle.write(text_to_pov(sentence))

    cmd = "povray "
    cmd += "+Q10 "
    cmd += "+A0.5 +AM1 +R16 +J2.2 +UV +UL "
    cmd += "Output_File_Type=N "
    cmd += "-W1280 -H720 "

    frames = 1
    img_fname = "tmp/{0}.png".format(file_prefix)
    '''
    temp_frames = duration.get()
    if temp_frames[-1] == "s":
        frames = int(float(temp_frames[0:-1]) * 24)
    elif temp_frames[-1] == "f":
        frames = int(float(temp_frames[0:-1]))
    else:
        frames = int(float(temp_frames))

    if frames > 1:
        last_frame = 1001 + frames
        slider.configure(to=last_frame)
        cmd += "-KFI1001 -KFF{0} -KI0.0 -KF1.0 ".format(last_frame)
        img_fname = "tmp/{0}1001.ppm".format(file_prefix)
    '''
    cmd += "-Itmp/{0}.pov ".format(file_prefix)

    print(cmd)
    os.system(cmd)

    return img_fname


if not os.path.exists("tmp"):
    os.makedirs("tmp")
