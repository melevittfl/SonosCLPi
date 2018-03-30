from sense_hat import SenseHat

sense = SenseHat()
sense.Clear()

# colours
b = (0,0,0)  # Black
w = (255, 255, 255)  # White
o = (251, 192, 45)  # Orange
g = (20, 166, 91)  # Green

cl_matrix  = [
    b, b, b, b, b, b, b, o,
    b, b, b, w, w, b, o, o,
    b, b, b, w, w, o, o, o,
    b, w, w, b, b, o, o, o,
    b, w, w, g, g, o, o, o,
    g, g, g, w, w, g, w, w,
    g, g, g, w, w, g, w, w,
    g, g, g, g, g, g, g, o
]

sense.set_pixels(cl_matrix)

