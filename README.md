# INSTALLATION
You'll need exiv2 for Python, on a Mac:
  
    - brew install gexiv2 pygobject pygobject3
    - brew install boost-python3
    - brew install python-all-dev
    - brew install exiv2
    - pip3 install py3exiv2==0.7.1

# USAGE
    mirrormirror.py

    Change the "img" variable to a photo of your choice.
    This script will evolve into a "find similar faces" service.

# OUTPUT
    - A image.show() with rectangle around face and meta data.
    - Meta data in json on stdout.

# TODO
    - stdin folder argument, loop through all photos there
    - implement find similar faces
    - make it a web app
    - probably change to matplotlib for jpg output of show()
    - define all functionality as functions and call these
    - preserve all originial exif data and write to out.jpg
