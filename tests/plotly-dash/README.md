# Testing `plotly-dash` in `heroku` 

This is based in the deployment [page](https://dash.plotly.com/deployment) for `dash`

``` bash
pip freeze > requirements.txt # pip dependencies
heroku create test-plotly-dash-heroku # create app
git add . && git commit -m 'COMMIT MESSAGE' # add and commit
```
