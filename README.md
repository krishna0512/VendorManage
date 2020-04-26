Basic README

Adding opencv support for heroku
add apt heroku buildpack using this command
The buildpack for the primary language of your app should be the last buildpack added.
$ heroku buildpacks:add --index 1 heroku-community/apt
Then add a Aptfile with contained dependencies and re-deploy the app with `git push heroku master`
source: https://elements.heroku.com/buildpacks/heroku/heroku-buildpack-apt

Thoughts on Permissions:
A worker cannot have the permission to change the product. as that permission is linked to many other things.
like uncompleting the products, marking a product as returned etc.