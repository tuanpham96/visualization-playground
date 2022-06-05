#!/ bin/bash

curl -o "data/netflix.json" \
  "https://www.whats-on-netflix.com/wp-content/plugins/whats-on-netflix/json/originals.json"

curl -o "data/appletv.json" \
  "https://www.apple.com/tv-pr/originals.originals.json"
