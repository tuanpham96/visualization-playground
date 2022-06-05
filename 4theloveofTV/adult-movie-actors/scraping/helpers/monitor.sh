#!/bin/bash

hist() {
  
  if [[ $(wc -l "$1" | awk '{print $1}') -lt 1 ]] ; then 
    echo "$1 is still empty"; 
    sleep 10
  fi
  
  case "$2" in 
    "movie") 
      out="$(grep -oE 'year=[0-9]*' "$1" | sed 's/year=//g')"
      ;;
    "actor")
      out="$(grep -oE 'gender=.{1}' "$1" | sed 's/gender=//g')"
      ;;
  esac 
  
  echo "$out" | sort | \
    uniq -c | \
    sort -k2 -r -n | \
    awk '{print $2,$1}' OFS=' ' | \
    termgraph --title="$1" --width=20
}

plot_year() {
  if [ -z "$2" ] ; then 
    plt_width=50
  else
    plt_width=$2
  fi
  
  year_plt="$(grep -oE 'year=[0-9]*'  $1 | \
    sed 's/year=//g' | \
    tr '\n' ' ' | \
    asciigraph -w $plt_width -h 5 -c 'years')"
  echo "$year_plt"
}

case "$1" in
  "hist")
    hist "$2" "$3"
    ;;
"plot")
  plot_year "$2" "$3" 
  ;;
"--help" | "-h")
  echo -e "\tUsage examples of monitor.sh"
  echo -e "\t+ histogram of movie years: \t ./monitor.sh hist tmp/chkpnt_movie.txt movie"
  echo -e "\t+ plot movie year: \t\t ./monitor.sh plot tmp/chkpnt_movie.txt <WIDTH>"
  echo -e "\t+ histogram actor genders: \t ./monitor.sh hist tmp/chkpnt_actor.txt actor"
  ;;
esac 

