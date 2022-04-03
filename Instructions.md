# Introduction

There's two main parts to the build system and testing procedure:
1. Python pagegen for generated content (html templates, files in the `./test/out` folder)
2. Gradle for static content (js, sass -> css and images)

## Folder structure

Here's a brief description on what each of the folders are for that we understand:

- `gradle`
    - contains the gradle wrapper jar
- `images`
    - contains png and svg images
- `js`
    - contains JavaScript files that are put on various places of Forge's websites
- `python`
    - the PageGen code
- `test`
    - this is where you can test your changes
    - `maven`
        - contains dummy data used by pagegen, generated by the `setupTest` Gradle task
        - you can make your own by running the `publish` command on most Forge projects and copy the literal folder called `repo` from there over to here
        - poms and the like don't seem to be used by the pagegen, so feel free to make folders, add files inside and change up the json as you see fit to aid testing.
            - As long as it follows the expected format similar to the dummy data, it should work
    - `out`
        - the generated output by pagegen
    - `static`
        - contains compiled static content, such as the css, js and images, made by the `setupTest`
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

## Step 1: Setting up the test environment

Firstly, we need to setup the Python side:
1. Make sure Python is installed. At the time of writing, the latest Python 3.10.4 seems to work

Now, let's setup the Gradle side:
1. Import the `build.gradle` into your IDE
    - Due to the old Gradle 5.6.4 in use here, you'll need to use Java 8 for it to work
2. Run `gradlew setupTest`

## Step 2: Run PageGen

1. Run `gradlew runTestPageGen`
2. Open the pages you want to test, they can be found in the `./test/out` folder

## Step 3: Making changes

For HTML:
1. Edit the appropriate file(s) in the `./templates` folder
2. Run `gradlew runTestPageGen`
3. Open the pages you want to test in the `./test/out` folder

For CSS:
1. Edit the appropriate file(s) in the `./css` folder
2. Run `gradlew setupTest`
3. Run `gradlew runTestPageGen`
4. Open the pages you want to test in the `./test/out` folder

For SCSS:
1. Edit the appropriate file(s) in the `./sass` folder
2. Run `gradlew setupTest`
3. Run `gradlew runTestPageGen`
4. Open the pages you want to test in the `./test/out` folder

For JS:
1. Edit the appropriate file(s) in the `./js` folder
2. Run `gradlew setupTest`
3. Run `gradlew runTestPageGen`
4. Open the pages you want to test in the `./test/out` folder

For images:
1. Edit the appropriate file(s) in the `./images` folder
2. Run `gradlew setupTest`
3. Run `gradlew runTestPageGen`
4. Open the pages you want to test in the `./test/out` folder

For the Python side of the build system:
1. Edit the appropriate file(s) in the `./python` folder and the `requirements.txt`
2. Run `setupPageGen` if you changed the `requirements.txt`
3. Test PageGen with `runTestPageGen` and opening the pages you want to test in the `./test/out` folder

For the Gradle side of the build system:
1. Edit the appropriate Gradle file(s), such as `build.gradle`, `gradlew`, `gradlew.bat` and the `./gradle` folder
2. Refresh Gradle as usual

## Step 4: Committing

In your PR, commit any changed files inside the `./css`, `./sass`, `./js`, `./templates`, `./images` and `./python` folders

Note: The test html files generated in Step 2 are not intended to be published to a live site, as they contain `file://` references to your machine for some static resources, which won't work for anyone else.