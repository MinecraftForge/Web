Forge Web
=========

This repository serves as central hub for all things web and [Forge](https://github.com/MinecraftForge/MinecraftForge/). This includes stylesheets, images and scripts for Forge sites such as the docs and the [forums](https://minecraftforge.net/).

SASS Structure
--------------
To ensure that the look and feel across all sites is consistent, we heavily rely on the [SASS preprocessor](http://sass-lang.com/) to modularize and automatically generate our stylesheets.

Hence, you will find a specific structure when looking at the stylesheets:

  - Only files without an underscore prefix will get deployed to the sites and are the place where all other components come together. These files should stay as they are right now unless new modules are added or old ones removed.
  - Files with an underscore make up discrete modules of the stylesheets, their name specifies each module's purpose.
  - Files with a 'theme' prefix serve as mere variable references to allow for flexible and easy switching of color themes.
  - Files with a 'styles' prefix serve as combinations of multiple modules along with the respective themes, while the simple 'styles.scss' file is the location where generic styles are brought together.
  - Files with a 'screens' suffix generally contain nothing but media queries that specify adjustments for different screen and device sizes.

Contribution Guidelines
-----------------------
You can find instructions on how to setup, develop and make contributions to this repo [here](Instructions.md).

Contributions such as fixes or additions to the stylesheets are welcome, but they should adhere to the following rules:

  - The sites make heavy use of the flexbox model. Its capabilities should be used to the fullest rather than relying on hacks simply to work in old browsers.
  - Colors mustn't be hardcoded unless they work well across all themes. Either stick to the current color palette and use the theme variables or, if no other way is possible, introduce a new theme variable.
  - All dimensional measurements must be specified in `rem` or as a percentage. This ensures a consistent look and will make potential font sizes changes less of a hassle.
  - Unless absolutely necessary, new modules or edits to the deployment files should be avoided. Changes should go into an appropriate file, but one shouldn't need to look for a single change in too many files.
  - Use of all capabilities of SASS is helpful. Try to nest things where a hierarchy is given and comment the topmost element accordingly.