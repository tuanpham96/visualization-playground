# Testing `plotly-dash` in `heroku` 

This is based in the deployment [page](https://dash.plotly.com/deployment) for `dash`. 

However, this also takes into account a different branch and a subfolder instead of root. 

``` bash
pip freeze > requirements.txt # pip dependencies

heroku create test-plotly-dash-heroku # create app

git add . && git commit -m 'COMMIT MESSAGE' # add and commit

heroku git:remote -a test-plotly-dash-heroku # add heroku git remote 

# Pushing 
# 1. default option, main/master branch, top level    
git push heroku main

# 2. if using another branch called "my-app" 
git push heroku my-app:main

# 3. if using a subfolder ("my-repo/my-app"), need to be at top level ("my-repo")
git subtree push --prefix my-repo/my-app heroku main

# 4. if both using subfolder and branch 
git subtree push --prefix tests/plotly-dash heroku test-dashplotly:main

heroku ps:scale web=1 # run app with heroku dyno

# For updating
git add . && git commit -m 'CHANGES'
git subtree push --prefix tests/plotly-dash heroku test-dashplotly:main

```
