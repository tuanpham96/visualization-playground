``` bash
watch -t -n 5 './helpers/monitor.sh hist $(ls data/pars* | tail -1) movie'
watch -t -n 5 './helpers/monitor.sh hist $(ls data/pars* | tail -1) actor; ./helpers/monitor.sh hist tmp/chkpnt_actor.txt actor '
watch -t -n 5 './helpers/monitor.sh hist tmp/chkpnt_movie.txt movie'
watch -n 5 './helpers/monitor.sh plot $(ls data/pars* | tail -1) 71'
watch -n 5 './helpers/monitor.sh plot tmp/chkpnt_movie.txt 30'
```
