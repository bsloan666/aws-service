import os
import random
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
        aperture 0.3
        blur_samples 25
        focal_point <0.0, 0.5, 0.00>
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
    #include "functions.inc"

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


def modify_object(model, modifier):
    return model[:-2] + modifier + model[-2:] + "\n"


def int_hash(in_str):
    total = 0
    for char in in_str:
        total += ord(char)
    return total


def row(arg, modifiers):
    result = "union {\n"
    for x in range(-8, 9, 4):
        result += arg[:-2] + " translate <{0}, 0, 0> ".format(x) + arg[-2:]

    result += modifiers
    result += "}\n"
    return result


def stack(arg, modifiers):
    result = "union {\n"
    for y in range(0, 10, 2):
        result += arg[:-2] + " translate <0, {0}, 0> ".format(y) + arg[-2:]

    result += modifiers
    result += "}\n"
    return result


def line(arg, modifiers):
    result = "union {\n"
    for z in range(0, 20, 4):
        result += modify_object(arg, " translate <0, 0, {0}> ".format(z))

    result += modifiers
    result += "}\n"
    return result


def pair(arg, modifiers):
    result = "union {\n"
    result += modify_object(arg, " translate <3, 0, 0> ")
    result += modify_object(arg, " translate <3, 0, 0> scale <-1, 1, 1> ")

    result += modifiers
    result += "}\n"
    return result


def ring(arg, modifiers):
    result = "union {\n"
    for index in range(32):
        theta = index * 360 / 32
        result += modify_object(arg, " translate <5, 0, 0> rotate <0, {0}, 0> ".format(theta))

    result += modifiers
    result += "}\n"
    return result


def flat_array(arg, modifiers):
    result = "union {\n"
    for x in range(-8, 9, 4):
        for z in range(-2, 15, 4):
            result += arg[:-2] + " translate <{0}, 0, {1}> ".format(x, z) + arg[-2:]

    result += modifiers
    result += "}\n"
    return result


def pile(arg, modifiers):
    result = "union {\n"
    for dim in range(5, 0, -1):
        for x in range(int(-4 * dim / 2), int(4 * dim / 2), 4):
            for z in range(int(-4 * dim / 2) + 8, int(4 * dim / 2) + 8, 4):
                result += arg[:-2] + " translate <{0}, {1}, {2}> ".format(x, (5 - dim) * 2, z) + arg[-2:]

    result += modifiers
    result += "}\n"
    return result


def wall(arg, modifiers):
    result = "union {\n"
    for x in range(-6, 7, 3):
        for y in range(0, 10, 2):
            result += arg[:-2] + " translate <{0}, {1}, 0> ".format(x, y) + arg[-2:]

    result += modifiers
    result += "}\n"
    return result


def noop(arg, modifiers):
    result = modify_object(arg, modifiers)
    return result


def tree(arg, modifiers):
    result = "union {\n"
    random.seed(int_hash(arg))
    xpos = random.uniform(-0.25, 0.25)
    ypos = 2 * random.uniform(0.1, 2)
    zpos = random.uniform(-0.25, 0.25)
    result += "cylinder { " + "<0, -0.5, 0> <{0}, {1}, {2}> 0.3 ".format(xpos, ypos, zpos) + "}\n"
    result += "sphere { " + "<{0}, {1}, {2}> 0.3 ".format(xpos, ypos, zpos) + " }\n"
    result += "sphere { " + "<0, -0.5, 0> 0.3 }\n"
    length = 2.0
    attenuation = 0.666

    def make_branches(position, result, arg, depth, roots=False):
        factor = attenuation ** depth
        max_depth = 5
        if roots:
            max_depth = 2
        for branch in [0, 1]:
            xpos = position[0] + random.uniform(-factor * 2, factor * 2)
            if roots:
                ypos = position[1] - length * random.uniform(0.1, factor * 2)
            else:
                ypos = position[1] + length * random.uniform(0.1, factor * 2)
            zpos = position[2] + random.uniform(-factor * 2, factor * 2)
            result += "cylinder { " + "<{0}, {1}, {2}> <{3}, {4}, {5}> {6} " .format(
                position[0], position[1], position[2], xpos, ypos, zpos, factor / 4) + "}\n"
            result += "sphere { " + "<{0}, {1}, {2}> {3} ".format(
                xpos, ypos, zpos, factor / 4) + "}\n"
            if depth < max_depth:
                result = make_branches([xpos, ypos, zpos], result, arg, depth + 1, roots)
            else:
                if not roots:
                    result += modify_object(arg, " translate <{0}, {1}, {2}> ".format(xpos, ypos, zpos)) + "\n"
                return result

        return result

    result = make_branches([xpos, ypos, zpos], result, arg, 0, False)
    result = make_branches([0, -0.5, 0], result, arg, 0, True)

    result += modifiers
    result += "}\n"
    return result


def do_function(function_tuple, arg):
    lookup = {
        "flat_array": flat_array,
        "stack": stack,
        "row": row,
        "wall": wall,
        "pile": pile,
        "tree": tree,
        "pair": pair,
        "line": line,
        "ring": ring,
    }
    return lookup.get(function_tuple[0], noop)(arg, function_tuple[1])


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
    text = modify_object(record['code'], modifiers)
    return functions, "", text


def translate_function(functions, modifiers, record):
    functions.insert(0, (record['code'], modifiers))
    return functions, "", ""


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
    line = re.split(r"\s", text.rstrip())

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
                    text = do_function(function, text)
                functions = []
                subject += text
                text = ""

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


def render(sentence, file_prefix, width, height):
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
    cmd += "-W{0} -H{1} ".format(width, height)

    # frames = 1
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

    pov_file = "tmp/{0}.pov".format(file_prefix)

    os.remove(pov_file)

    return img_fname


if not os.path.exists("tmp"):
    os.makedirs("tmp")
