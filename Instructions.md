# Introduction

There's two main parts to the build system and testing procedure:
1. Python pagegen for generated content (html templates, files in the `out` folder)
2. Gradle for static content (js, sass -> css)

## Folder structure

Here's a brief description on what each of the folders are for that we understand:

- `config`
    - contains the global_overrides.json file that the pagegen command needs, includes a bit of json to enable dummy ads
- `gradle`
    - contains the gradle wrapper jar
- `images`
    - self-explanatory
    - might be worth moving to static folder at some stage
- `js`
    - contains JavaScript files that are put on various places of Forge's website
- `out`
    - the generated output by pagegen
- `python`
    - the pagegen code
- `repo`
    - contains dummy data used by pagegen
    - you can make your own by running the `publish` command on most Forge projects and copy the literal folder called `repo` from there over to here
    - poms and the like don't seem to be used by the pagegen, so feel free to make folders, add files inside and change up the json as you see fit to aid testing.
        - As long as it follows the expected format similar to the dummy data, it should work
- `sass`
    - poorly named, actually has scss files inside which are used for styling
    - they get compiled to css by the gradle part of the build system
- `static`
    - contains compiled static content, such as the css, js and images
    - during testing, you probably want to compile to this folder and tell pagegen to use this with the `--static` arg
    - this folder also contains a copy of the images folder
- `templates`
    - the HTML templates used by the Python pagegen side of the build system

# Instructions

Here's some instructions on how to setup the environment and work with it.

## Step 1: Setting up the build tools

Firstly, we need to setup the Python side:
1. Make sure Python is installed. At the time of writing, I used the latest Python 3.10.4 and it seemed to work fine
2. In the repository root, run `pip install -r requirements.txt` to install the necessary dependencies for pagegen

Now, let's setup the Gradle side:
1. Import the `build.gradle` into your IDE
    - Due to the ancient Gradle 4.4.1 in use here, you'll need to use Java 8 for it to work

## Step 2: Manually setup for testing

1. Run `gradlew bundleFiles`
2. Extract the contents of the zip made in `./build/distributions/files-bundle.zip` to `./static`, overwriting any existing files
    - do *not* overwrite the corresponding base directories (`js`, `sass`, etc...) as the contents of this zip are minified and may contain the same file names, while the contents of the base directories are the source files. You don't want to be overwriting source files with minified ones!
3. Run `python .\python\page_generator.py --webout './out' --metaout './out' --folder './repo' --config './config/global_overrides.json' --static 'file://<full-path-to-this-folder>/static/' promote net.minecraftforge:forge 1.18.2-40.0.34 latest`
    - replacing `<full-path-to-this-folder>` accordingly. For example, `--static 'file://C:/Users/PaintNinja/Documents/GitHub/MinecraftForge-Web/static/'`
    - note: the `--static` argument must always use forward slashes, start with `file://` and end with a trailing forward slash (a "`/`")
4. Open the pages you want to test, they can be found in the `out` folder
    - note: many links are broken in testing - especially on Windows - this is a known issue

## Step 3: Making changes

For HTML:
- Edit the appropriate file(s) in the `templates` folder then follow Steps 2.3 and 2.4

For SCSS:
- Edit the appropriate file(s) in the `sass` folder then follow all the sub-steps in Step 2

For JS:
- Edit the appropriate file(s) in the `js` folder then follow all the sub-steps in Step 2

For images:
1. Edit the appropriate file(s) in the `images` folder
2. Copy it to the `static/images` folder
3. Open the pages you want to test in the `out` folder

For the Python side of the build system:
- Edit the appropriate file(s) in the `python` folder and the `requirements.txt`, then test pagegen by following all the sub-steps in Step 2

For the Gradle side of the build system:
- Edit the appropriate Gradle file(s), such as `build.gradle`, `gradlew`, `gradlew.bat` and the `gradle` folder

## Step 4: Committing

1. Important: Make sure you've compiled and updated the static folder.
2. In your PR, commit any changed files inside the sass/js/templates/static/images/python folders
    - Note: Do *not* commit the `out` or `build` folders

Note: The test html files generated in Step 2 are not intended to be published to a live site, as they contain `file://` references to your machine for some static resources, which won't work for anyone else.