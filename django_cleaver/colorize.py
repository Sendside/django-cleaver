from PIL import Image, ImageOps

img = Image.open('colorize_input.png')

# Bug workaround: explicitly load the image (otherwise you will get errors!)
img.load()

# Get the alpha channel
al = img.split()[3]

# Convert whole image to greyscale.
gr = ImageOps.grayscale(img)

# Colorize the image using these RGB tuples
col = ImageOps.colorize(gr, (128,0,0), (255,255,128))

# Split colorized image into component channels
bands = col.split()

# Create a new image comprised of the channels plus alpha
cal = Image.merge("RGBA", (bands[0], bands[1], bands[2], al))
    
# Save the resulting image out to a PNG file
cal.save("colorize_output.png", "PNG")

print "Created colorized file 'colorize_output.png'"
